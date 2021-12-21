#    Interleave Playlist
#    Copyright (C) 2021 Thomas Sweeney
#    This file is part of Interleave Playlist.
#    Interleave Playlist is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    Interleave Playlist is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import os
import subprocess
import threading

from PySide6.QtCore import Slot, QEvent, Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor, QBrush, QFontDatabase, QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton, QMessageBox, QFileDialog, QLabel, QGridLayout, QProgressBar, QRadioButton, \
    QGroupBox
from pymediainfo import MediaInfo

from core.playlist import FileGroup
from interface import open_with_default_application, _create_playlist, _get_duration_str
from interface.PlaylistWindowItem import PlaylistWindowItem
from persistence import settings, input_, state
from persistence.watched import add_watched, remove_watched

_LIGHT_MODE_WATCHED_COLOR = QBrush(QColor.fromRgb(255, 121, 121))
_DARK_MODE_WATCHED_COLOR = QBrush(QColor.fromRgb(77, 12, 12))
_TOTAL_SHOWS_TEXT =    'Total Shows:    {}'
_SELECTED_SHOWS_TEXT = 'Selected Shows: {}'
_TOTAL_RUNTIME =       'Total Runtime:    {}'
_SELECTED_RUNTIME =    'Selected Runtime: {}'


class RuntimeCalculationThread(QThread):
    value_updated = Signal(int)
    completed = Signal(dict)

    def __init__(self, playlist: dict[str, str], duration_cache=None):
        super(RuntimeCalculationThread, self).__init__()
        if duration_cache is None:
            duration_cache = {}
        self.running = False
        self.stop = False
        self.playlist = playlist.copy()
        self.duration_cache: dict[str, int] = ({}
                                               if duration_cache is None else
                                               duration_cache.copy())
        self.pending_playlist = None

    def __del__(self):
        self.wait()

    def set_pending_playlist(self, playlist: dict[str, str]):
        self.pending_playlist = playlist.copy()

    def run(self):
        self.running = True
        while True:
            for i, elem in enumerate(item[0] for item in self.playlist):
                if self.stop:
                    return
                if elem not in self.duration_cache:
                    media_info = MediaInfo.parse(elem)
                    self.duration_cache[elem] = int(float(media_info.video_tracks[0].duration))
                    self.value_updated.emit(i+1)
            if not self.pending_playlist:
                break
            else:
                self.playlist = self.pending_playlist
                self.pending_playlist = None
        self.completed.emit(self.duration_cache)
        self.running = False


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self._row_color1, self._row_color2 = self._get_standard_row_colors()
        self.duration_cache = {}
        self.durations_loaded = False

        label_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        label_font.setPointSize(settings.get_font_size() * 1.25)
        self.total_shows_label = QLabel()
        self.total_shows_label.setFont(label_font)

        self.total_selected_label = QLabel()
        self.total_selected_label.setFont(label_font)

        self.playlist: dict[str, str] = {}
        self.item_list: QListWidget = self._create_item_list()

        self.total_runtime_label = QLabel(_TOTAL_RUNTIME.format('...'))
        self.total_runtime_label.setFont(label_font)
        self.total_runtime_progress = QProgressBar()
        self.total_runtime_progress.setMaximum(len(self.playlist))

        self.selected_runtime_label = QLabel(_SELECTED_RUNTIME.format('...'))
        self.selected_runtime_label.setFont(label_font)
        self.item_list.selectAll()

        self.runtime_thread = None
        self._run_calculate_total_runtime_thread()

        self.interleave_radio = QRadioButton("Interleave")
        self.interleave_radio.toggle()
        self.alphabetical_radio = QRadioButton("Alphabetical")
        self.last_modified_radio = QRadioButton("Last Modified")
        self.lru_radio = QRadioButton("Least Recently Watched")

        total_layout = QVBoxLayout()
        total_group = QGroupBox("Stats")
        total_group.setLayout(total_layout)
        total_layout.addWidget(self.total_shows_label)
        total_layout.addWidget(self.total_selected_label)
        runtime_layout = QVBoxLayout()
        runtime_group = QGroupBox(" ")
        runtime_group.setLayout(runtime_layout)
        runtime_layout.addWidget(self.total_runtime_label)
        runtime_layout.addWidget(self.selected_runtime_label)
        label_layout = QHBoxLayout()
        label_layout.addWidget(total_group)
        label_layout.addWidget(runtime_group)

        radio_group = QGroupBox("Sort")
        radio_layout = QGridLayout()
        radio_layout.addWidget(self.interleave_radio,    0, 0)
        radio_layout.addWidget(self.alphabetical_radio,  1, 0)
        radio_layout.addWidget(self.last_modified_radio, 0, 1)
        radio_layout.addWidget(self.lru_radio,           1, 1)
        radio_group.setLayout(radio_layout)

        label_layout.addWidget(radio_group)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.item_list)

        layout = QVBoxLayout(self)
        layout.addWidget(self.total_runtime_progress)
        layout.addLayout(label_layout)
        layout.addLayout(self._create_button_layout())
        layout.addLayout(list_layout)

        self.item_list.setFocus()

    def _create_item_list(self):
        item_list = QListWidget()
        item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        item_list.setAlternatingRowColors(True)
        font = QFont()
        font.setPointSize(settings.get_font_size())
        item_list.setFont(font)
        item_list.doubleClicked.connect(self.play)
        item_list.itemSelectionChanged.connect(self.selection_change)
        item_list.installEventFilter(self)
        self._refresh(item_list)
        return item_list

    def _create_button_layout(self):
        button_layout = QHBoxLayout()
        buttons = {
            'Play': self.play,
            'Mark Watched': self.mark_watched,
            'Unmark Watched': self.unmark_watched,
            'Drop Shows': self.drop_groups,
            'Refresh': self.refresh,
            'Open Input File': self.open_input,
            'Open Watched File': self.open_watched_file,
        }
        for key, value in buttons.items():
            button = QPushButton(key)
            button.clicked.connect(value)
            button_layout.addWidget(button)
        return button_layout

    def eventFilter(self, widget: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            switch: dict[int, callable] = {
                Qt.NoModifier + Qt.Key_Return: self._play,
                Qt.NoModifier + Qt.Key_Enter: self._play,
                Qt.ControlModifier + Qt.Key_W: self.mark_watched,
                Qt.ControlModifier + Qt.Key_U: self.unmark_watched,
                Qt.NoModifier + Qt.Key_F5: self.refresh,
                Qt.ControlModifier + Qt.Key_O: self.open_input,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_O: self.open_watched_file
            }
            if event.keyCombination().toCombined() in switch:
                switch[event.keyCombination().toCombined()]()
                return True
        return False

    @Slot()
    def play(self):
        self._play()

    def _play(self):
        def _impl():
            files = [i.getValue()[0] for i in self.item_list.selectedItems()]
            subprocess.run([settings.get_play_command()] + files)
        if self.playlist is not None:
            thread = threading.Thread(target=_impl)
            thread.start()

    @Slot()
    def mark_watched(self):
        selected_values: list[FileGroup] = [
            i.getValue() for i in self.item_list.selectedItems()
        ]
        add_watched(selected_values)
        for item in self.item_list.selectedItems():
            item.setBackground(self._get_watched_color())

    @Slot()
    def unmark_watched(self):
        selected_values: list[FileGroup] = [
            i.getValue() for i in self.item_list.selectedItems()
        ]
        remove_watched(selected_values)
        for i, item in enumerate(self.item_list.selectedItems()):
            color = self._row_color1 if i % 2 == 0 else self._row_color2
            item.setBackground(color)

    @Slot()
    def drop_groups(self):
        selected_values: list[FileGroup] = [
            i.getValue() for i in self.item_list.selectedItems()
        ]
        groups = set()
        for value in selected_values:
            if len(value) > 1:
                # hacky for now
                groups.add(tuple(value[1].split('_____')))
        input_.drop_groups(groups)

    @Slot()
    def refresh(self):
        self._refresh(self.item_list)
        self._run_calculate_total_runtime_thread()

    def _refresh(self, item_list: QListWidget):
        item_list.clear()
        self.playlist = _create_playlist()
        if self.playlist is not None:
            for item in self.playlist:
                item_list.addItem(
                    PlaylistWindowItem(value=item)
                )
        self.total_shows_label.setText(_TOTAL_SHOWS_TEXT.format(len(self.playlist)))
        self._selection_change(0)

    @Slot()
    def open_input(self):
        file_name: str = QFileDialog.getOpenFileName(
            self, 'Open yaml', os.path.expanduser('~'), 'yaml files (*.yml *.yaml)')[0]
        if file_name.strip() == '':
            return
        try:
            state.set_last_input_file(file_name)
        except input_.InvalidInputFile:
            QMessageBox(text='Error: Attempted to open invalid settings yaml file\n\n'
                             '{}'.format(file_name),
                        icon=QMessageBox.Critical).exec()
            return
        self._refresh(self.item_list)
        self._run_calculate_total_runtime_thread()

    @Slot()
    def open_watched_file(self):
        def _impl():
            open_with_default_application(input_.get_watched_file_name())
        thread = threading.Thread(target=_impl)
        thread.start()

    @Slot()
    def selection_change(self):
        self._selection_change(len(self.item_list.selectedItems()))

    @Slot()
    def update_total_runtime_progress_bar(self, value):
        self.total_runtime_progress.setMaximum(len(self.runtime_thread.playlist))
        self.total_runtime_progress.setValue(value)

    @Slot()
    def total_runtime_thread_completed(self, duration_cache: dict[str, int]):
        self.duration_cache = duration_cache
        total_duration = sum(duration_cache.values())
        self.total_runtime_label.setText(
            _TOTAL_RUNTIME.format(_get_duration_str(total_duration, total_duration)))
        self._get_selected_runtime()
        self.total_runtime_progress.hide()
        self.durations_loaded = True

    def _selection_change(self, num_selected: int):
        self.total_selected_label.setText(
            _SELECTED_SHOWS_TEXT.format(
                str(num_selected).rjust(math.ceil(
                    math.log10(len(self.playlist))
                    if len(self.playlist) > 0 else
                    1
                ))))
        if self.durations_loaded:
            self._get_selected_runtime()

    def _get_selected_runtime(self):
        self.selected_runtime_label.setText(_SELECTED_RUNTIME.format('...'))
        duration = sum([self.duration_cache[i.getValue()[0]]
                        for i in self.item_list.selectedItems()])
        total_duration = sum(self.duration_cache.values())
        self.selected_runtime_label.setText(
            _SELECTED_RUNTIME.format(_get_duration_str(duration, total_duration)))

    @staticmethod
    def _get_standard_row_colors():
        # wow this is silly
        _hidden_list = QListWidget()
        _hidden_list.setAlternatingRowColors(True)
        _hidden_list.addItems(["", ""])
        color1 = _hidden_list.item(0).background()
        color2 = _hidden_list.item(1).background()
        return color1, color2

    @staticmethod
    def _get_watched_color():
        return (_LIGHT_MODE_WATCHED_COLOR
                if not settings.get_dark_mode() else
                _DARK_MODE_WATCHED_COLOR)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.runtime_thread.stop = True

    def _run_calculate_total_runtime_thread(self):
        self.selected_runtime_label.setText(_SELECTED_RUNTIME.format('...'))
        self.durations_loaded = False
        if self.runtime_thread is None or self.runtime_thread.isFinished():
            self.total_runtime_progress.show()
            self.total_runtime_label.setText(_TOTAL_RUNTIME.format('...'))
            self.runtime_thread = RuntimeCalculationThread(self.playlist, self.duration_cache)
            self.runtime_thread.value_updated.connect(self.update_total_runtime_progress_bar)
            self.runtime_thread.completed.connect(self.total_runtime_thread_completed)
            self.total_runtime_progress.setValue(0)
            self.runtime_thread.start()
        else:
            self.runtime_thread.set_pending_playlist(self.playlist)
