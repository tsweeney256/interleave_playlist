#    Interleave Playlist
#    Copyright (C) 2021-2022 Thomas Sweeney
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
import itertools
import math
import os
import subprocess
import threading
import typing
from typing import Optional, Callable, Any

import natsort
from PySide6.QtCore import Slot, QEvent, Qt, Signal, QThread, QDeadlineTimer, SignalInstance
from PySide6.QtGui import QFont, QColor, QBrush, QFontDatabase, QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton, QMessageBox, QFileDialog, QLabel, QGridLayout, QProgressBar, QRadioButton, \
    QGroupBox, QCheckBox, QLineEdit, QLayout
from natsort import natsorted
from pymediainfo import MediaInfo

from interleave_playlist.core.playlist import PlaylistEntry
from interleave_playlist.interface import open_with_default_application, _create_playlist, \
    _get_duration_str
from interleave_playlist.interface.PlaylistWindowItem import PlaylistWindowItem
from interleave_playlist.interface.SearchBarThread import SearchBarThread, \
    SearchBarThreadAlreadyDeadException
from interleave_playlist.persistence import input_
from interleave_playlist.persistence import settings
from interleave_playlist.persistence.input_ import set_last_input_file
from interleave_playlist.persistence.watched import add_watched, remove_watched

_LIGHT_MODE_WATCHED_COLOR = QBrush(QColor.fromRgb(255, 121, 121))
_DARK_MODE_WATCHED_COLOR = QBrush(QColor.fromRgb(77, 12, 12))
_TOTAL_SHOWS_TEXT = 'Total Shows:    {}'
_SELECTED_SHOWS_TEXT = 'Selected Shows: {}'
_TOTAL_RUNTIME = 'Total Runtime:    {}'
_SELECTED_RUNTIME = 'Selected Runtime: {}'


class RuntimeCalculationThread(QThread):
    value_updated = typing.cast(SignalInstance, Signal(int))
    completed = typing.cast(SignalInstance, Signal(dict, int))
    error = typing.cast(SignalInstance, Signal(BaseException))

    def __init__(self,
                 playlist: list[PlaylistEntry],
                 duration_cache: Optional[dict[str, int]] = None):
        super(RuntimeCalculationThread, self).__init__()
        if duration_cache is None:
            duration_cache = {}
        self.running: bool = False
        self.stop: bool = False
        self.playlist: list[PlaylistEntry] = playlist.copy()
        self.duration_cache: dict[str, int] = ({}
                                               if duration_cache is None else
                                               duration_cache.copy())
        self.pending_playlist: Optional[list[PlaylistEntry]] = None

    def __del__(self) -> None:
        self.wait()

    def set_pending_playlist(self, playlist: list[PlaylistEntry]) -> None:
        self.pending_playlist = playlist.copy()

    def run(self) -> None:
        self.running = True
        try:
            self._run()
        except BaseException as e:
            self.error.emit(e)
        finally:
            self.running = False

    def _run(self) -> None:
        while True:
            total_duration = 0
            for i, elem in enumerate(item.filename for item in self.playlist):
                if self.stop:
                    return
                if elem not in self.duration_cache:
                    duration: int = 0
                    if os.path.isfile(elem):
                        media_info = MediaInfo.parse(elem)
                        if len(media_info.video_tracks) > 0 \
                                and media_info.video_tracks[0].duration:
                            duration = int(float(media_info.video_tracks[0].duration))
                        elif len(media_info.audio_tracks) > 0 \
                                and media_info.audio_tracks[0].duration:
                            duration = int(float(media_info.audio_tracks[0].duration))
                        else:
                            print(f'Warning: {elem} has no duration info for video or audio')
                            duration = 0
                    self.duration_cache[elem] = duration
                    self.value_updated.emit(i+1)
                total_duration += self.duration_cache[elem]
            if not self.pending_playlist:
                break
            self.playlist = self.pending_playlist
            self.pending_playlist = None
        self.completed.emit(self.duration_cache, total_duration)


class PlaylistWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._warned_about_mediainfo_missing = False
        self.selection_dependent_buttons: list[QPushButton] = []
        self._row_color1, self._row_color2 = self._get_standard_row_colors()
        self.duration_cache: dict[str, int] = {}
        self.durations_loaded = False
        counter = itertools.count()
        self.sort: Callable[[Any], Any] = lambda x: next(counter)

        self.search_bar_thread = None
        label_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        label_font.setPointSize(int(settings.get_font_size() * 1.25))
        self.total_shows_label = QLabel()
        self.total_shows_label.setFont(label_font)

        self.total_selected_label = QLabel()
        self.total_selected_label.setFont(label_font)

        self.playlist: list[PlaylistEntry] = []
        self.item_list: QListWidget = self._create_item_list()

        self.total_runtime_label = QLabel(_TOTAL_RUNTIME.format('...'))
        self.total_runtime_label.setFont(label_font)
        self.total_runtime_progress = QProgressBar()
        self.total_runtime_progress.setMaximum(len(self.playlist))
        self.total_runtime_progress.hide()

        self.selected_runtime_label = QLabel(_SELECTED_RUNTIME.format('...'))
        self.selected_runtime_label.setFont(label_font)
        self.item_list.selectAll()

        self.runtime_thread = None
        self.total_duration: int = 0

        search_label = QLabel("Search ")
        self.search_bar = QLineEdit()
        self.search_bar.textEdited.connect(self.search_bar_text_edited)
        self.search_bar.editingFinished.connect(self.search_bar_editing_finished)
        self.search_bar.setToolTip("Ctrl+F")
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)

        self.interleave_radio = QRadioButton("Interleave")
        self.interleave_radio.setToolTip('Ctrl+Shift+I')
        self.interleave_radio.toggle()
        self.interleave_radio.toggled.connect(self.interleave_sort)
        self.alphabetical_radio = QRadioButton("Alphabetical")
        self.alphabetical_radio.setToolTip('Ctrl+Shift+A')
        self.alphabetical_radio.toggled.connect(self.alphabetical_sort)
        self.last_modified_radio = QRadioButton("Last Modified")
        self.last_modified_radio.setToolTip('Ctrl+Shift+M')
        self.last_modified_radio.toggled.connect(self.last_modified_sort)
        self.reversed_checkbox = QCheckBox("Reversed")
        self.reversed_checkbox.toggled.connect(self.reverse_sort)
        self.reversed_checkbox.setToolTip('Ctrl+Shift+R')

        total_layout = QVBoxLayout()
        stats_group = QGroupBox("Stats")
        total_layout.addWidget(self.total_shows_label)
        total_layout.addWidget(self.total_selected_label)
        runtime_layout = QVBoxLayout()
        runtime_layout.addWidget(self.total_runtime_label)
        runtime_layout.addWidget(self.selected_runtime_label)
        stats_layout = QHBoxLayout()
        stats_layout.addLayout(total_layout)
        stats_layout.addLayout(runtime_layout)
        stats_group.setLayout(stats_layout)
        label_layout = QHBoxLayout()
        label_layout.addWidget(stats_group, 4)

        radio_group = QGroupBox("Search && Sort")
        radio_layout = QGridLayout()
        radio_layout.addWidget(self.interleave_radio,    0, 0)
        radio_layout.addWidget(self.alphabetical_radio,  1, 0)
        radio_layout.addWidget(self.last_modified_radio, 0, 1)
        radio_layout.addWidget(self.reversed_checkbox,   1, 1)
        radio_layout.addLayout(search_layout,            2, 0, 1, 2)
        radio_group.setLayout(radio_layout)

        label_layout.addWidget(radio_group, 2)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.item_list)

        layout = QVBoxLayout(self)
        layout.addWidget(self.total_runtime_progress)
        layout.addLayout(label_layout)
        layout.addLayout(self._create_button_layout())
        layout.addLayout(list_layout)

        self._refresh()
        self.item_list.selectAll()

    def _create_item_list(self) -> QListWidget:
        item_list = QListWidget()
        item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        item_list.setAlternatingRowColors(True)
        font = QFont()
        font.setPointSize(settings.get_font_size())
        item_list.setFont(font)
        item_list.doubleClicked.connect(self.play)
        item_list.itemSelectionChanged.connect(self.selection_change)
        item_list.installEventFilter(self)
        return item_list

    def _create_button_layout(self) -> QLayout:
        button_layout = QHBoxLayout()
        buttons = [
            ('Play', self.play, 'Enter', True),
            ('Mark Watched', self.mark_watched, 'Ctrl-W', True),
            ('Unmark Watched', self.unmark_watched, 'Ctrl-U', True),
            ('Drop Shows', self.drop_groups, 'Ctrl-Shift-D', True),
            ('Refresh', self.refresh, 'F5', False),
            ('Open Input File', self.open_input, 'Ctrl-O', False),
            ('Open Watched File', self.open_watched_file, 'Ctrl-Shift-O', False),
        ]
        for name, func, tooltip, selection_dependent in buttons:
            button = QPushButton(name)
            button.clicked.connect(func)
            if tooltip is not None:
                button.setToolTip(tooltip)
            if selection_dependent:
                self.selection_dependent_buttons.append(button)
            button_layout.addWidget(button)
        return button_layout

    @typing.no_type_check
    def eventFilter(self, widget: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            switch: dict[int, Callable] = {
                Qt.NoModifier + Qt.Key_Return: self._play,
                Qt.NoModifier + Qt.Key_Enter: self._play,
                Qt.ControlModifier + Qt.Key_W: self.mark_watched,
                Qt.ControlModifier + Qt.Key_U: self.unmark_watched,
                Qt.NoModifier + Qt.Key_F5: self.refresh,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_D: self.drop_groups,
                Qt.ControlModifier + Qt.Key_O: self.open_input,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_O: self.open_watched_file,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_I: self.interleave_radio.toggle,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_A: self.alphabetical_radio.toggle,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_M: self.last_modified_radio.toggle,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_R: self.reversed_checkbox.toggle,
                Qt.ControlModifier + Qt.Key_F: self._focus_search_bar
            }
            if event.keyCombination().toCombined() in switch:
                switch[event.keyCombination().toCombined()]()
                return True
        return False

    @Slot()
    def play(self) -> None:
        self._play()
        self.item_list.setFocus()

    def _play(self) -> None:
        def _impl() -> None:
            files = [i.getValue().filename
                     for i
                     in typing.cast(list[PlaylistWindowItem], self.item_list.selectedItems())]
            subprocess.run([settings.get_play_command()] + files)
        if self.playlist is not None:
            thread = threading.Thread(target=_impl)
            thread.start()

    @Slot()
    def mark_watched(self) -> None:
        selected_values: list[PlaylistEntry] = [
            i.getValue()
            for i
            in typing.cast(list[PlaylistWindowItem], self.item_list.selectedItems())
        ]
        add_watched(selected_values)
        for item in self.item_list.selectedItems():
            item.setBackground(self._get_watched_color())
        self.item_list.setFocus()

    @Slot()
    def unmark_watched(self) -> None:
        selected_values: list[PlaylistEntry] = [
            i.getValue()
            for i
            in typing.cast(list[PlaylistWindowItem], self.item_list.selectedItems())
        ]
        remove_watched(selected_values)
        for i, item in enumerate(self.item_list.selectedItems()):
            color = self._row_color1 if i % 2 == 0 else self._row_color2
            item.setBackground(color)
        self.item_list.setFocus()

    @Slot()
    def drop_groups(self) -> None:
        selected_entries: list[PlaylistEntry] = [
            i.getValue()
            for i
            in typing.cast(list[PlaylistWindowItem], self.item_list.selectedItems())
        ]
        if len(selected_entries) == 0:
            return
        groups_str = set()
        for entry in selected_entries:
            groups_str.add(entry.group.name)
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Drop Groups')
        msg_box.setText("You are about to drop the following groups. "
                        "Do you wish to continue?\n    {}"
                        .format('\n    '.join(natsorted(groups_str))))
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        reply = msg_box.exec()
        if reply == QMessageBox.Ok:
            input_.drop_groups(selected_entries)
        self.item_list.setFocus()

    @Slot()
    def refresh(self) -> None:
        self._refresh()

    def _refresh(self, *, use_cache: bool = False) -> None:
        self.item_list.clear()
        self.playlist = _create_playlist(self.search_bar.text(), use_cache)
        if self.playlist is not None:
            for item in sorted(self.playlist,
                               key=self.sort,
                               reverse=self.reversed_checkbox.isChecked()):
                self.item_list.addItem(
                    PlaylistWindowItem(value=item)
                )
        self.total_shows_label.setText(_TOTAL_SHOWS_TEXT.format(len(self.playlist)))
        self.durations_loaded = False
        if self.item_list.count() > 0:
            self.item_list.setCurrentItem(self.item_list.item(0))
        self._run_calculate_total_runtime_thread()
        self._refresh_buttons()
        self.item_list.setFocus()

    @Slot()
    def open_input(self) -> None:
        try:
            file_name: str = QFileDialog.getOpenFileName(
                self, 'Open yaml', os.path.expanduser('~'), 'yaml files (*.yml *.yaml)')[0]
            if file_name.strip() == '':
                return
            try:
                set_last_input_file(file_name)
            except input_.InvalidInputFile:
                msg_box = QMessageBox()
                msg_box.setWindowTitle('Error')
                msg_box.setText(f'Error: Attempted to open invalid input yaml file\n\n{file_name}')
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()
                return
            self._stop_runtime_thread()
            self._refresh()
        finally:
            self.item_list.setFocus()

    @Slot()
    def open_watched_file(self) -> None:
        def _impl() -> None:
            open_with_default_application(input_.get_watched_file_name())
        thread = threading.Thread(target=_impl)
        thread.start()
        self.item_list.setFocus()

    @Slot()
    def selection_change(self) -> None:
        self._selection_change(len(self.item_list.selectedItems()))

    @Slot()
    def update_total_runtime_progress_bar(self, value: int) -> None:
        if self.runtime_thread is None:
            return
        self.total_runtime_progress.setMaximum(len(self.runtime_thread.playlist))
        self.total_runtime_progress.setValue(value)

    @Slot()
    def total_runtime_thread_completed(self, duration_cache: dict[str, int],
                                       total_duration: int) -> None:
        self.duration_cache = duration_cache
        self.total_duration = total_duration
        self.total_runtime_label.setText(
            _TOTAL_RUNTIME.format(_get_duration_str(total_duration, total_duration)))
        self.durations_loaded = True
        self._get_selected_runtime()
        self.total_runtime_progress.hide()

    @Slot()
    def total_runtime_thread_error(self, exception: BaseException) -> None:
        raise exception

    @Slot()
    def search_bar_thread_error(self, exception: BaseException) -> None:
        raise exception

    @Slot()
    def interleave_sort(self, checked: bool) -> None:
        if not checked:
            return
        counter = itertools.count()
        self.sort = lambda x: next(counter)
        self._refresh(use_cache=True)
        self.item_list.setFocus()

    @Slot()
    def alphabetical_sort(self, checked: bool) -> None:
        if not checked:
            return
        self.sort = natsort.natsort_keygen(
            lambda i: os.path.basename(i.filename))  # type: ignore[no-any-return]
        self._refresh(use_cache=True)
        self.item_list.setFocus()

    @Slot()
    def last_modified_sort(self, checked: bool) -> None:
        if not checked:
            return
        self.sort = lambda x: os.path.getmtime(x.filename)
        self._refresh(use_cache=True)
        self.item_list.setFocus()

    @Slot()
    def reverse_sort(self, checked: bool) -> None:
        self._refresh(use_cache=True)
        self.item_list.setFocus()

    @Slot()
    def search_bar_text_edited(self, text: str) -> None:
        if self.search_bar_thread is None:
            self._init_search_bar_thread(text)
            return
        try:
            self.search_bar_thread.search_value = text
            return
        except SearchBarThreadAlreadyDeadException:
            self._init_search_bar_thread(text)

    @Slot()
    def search_bar_editing_finished(self) -> None:
        self._refresh(use_cache=True)
        # we don't want focus back here. we're finished

    @Slot()
    def search_bar_thread_completed(self, text: str) -> None:
        self._refresh(use_cache=True)
        self.search_bar.setFocus()

    def _init_search_bar_thread(self, text: str) -> None:
        self.search_bar_thread = SearchBarThread(text, 500)
        self.search_bar_thread.error.connect(self.search_bar_thread_error)
        self.search_bar_thread.completed.connect(self.search_bar_thread_completed)
        self.search_bar_thread.start()

    def _focus_search_bar(self) -> None:
        self.search_bar.setFocus()
        self.search_bar.selectAll()

    def _selection_change(self, num_selected: int) -> None:
        self.total_selected_label.setText(
            _SELECTED_SHOWS_TEXT.format(
                str(num_selected).rjust(math.ceil(
                    math.log10(len(self.playlist))
                    if len(self.playlist) > 0 else
                    1
                ))))
        self._get_selected_runtime()
        for btn in self.selection_dependent_buttons:
            btn.setEnabled(num_selected > 0)

    def _get_selected_runtime(self) -> None:
        if not self.durations_loaded:
            return
        self.selected_runtime_label.setText(_SELECTED_RUNTIME.format('...'))
        duration = sum([self.duration_cache[i.getValue().filename]
                        for i
                        in typing.cast(list[PlaylistWindowItem], self.item_list.selectedItems())])
        self.selected_runtime_label.setText(
            _SELECTED_RUNTIME.format(_get_duration_str(duration, self.total_duration)))

    @staticmethod
    def _get_standard_row_colors() -> tuple[QBrush, QBrush]:
        # wow this is silly
        _hidden_list = QListWidget()
        _hidden_list.setAlternatingRowColors(True)
        _hidden_list.addItems(["", ""])
        color1 = _hidden_list.item(0).background()
        color2 = _hidden_list.item(1).background()
        return color1, color2

    @staticmethod
    def _get_watched_color() -> QBrush:
        return (_LIGHT_MODE_WATCHED_COLOR
                if not settings.get_dark_mode() else
                _DARK_MODE_WATCHED_COLOR)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._stop_runtime_thread()

    def _run_calculate_total_runtime_thread(self) -> None:
        self.selected_runtime_label.setText(_SELECTED_RUNTIME.format('...'))
        self.durations_loaded = False
        if not MediaInfo.can_parse():
            if not self._warned_about_mediainfo_missing:
                self._warned_about_mediainfo_missing = True
                msg_box = QMessageBox()
                msg_box.setWindowTitle('Warning')
                msg_box.setText("libmediainfo not found. Will be unable to calculate "
                                "runtimes unless installed")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()
            return
        if self.runtime_thread is not None and not self.runtime_thread.isFinished():
            self.runtime_thread.set_pending_playlist(self.playlist)
            return
        self.total_runtime_progress.setValue(0)
        self.total_runtime_progress.show()
        self.total_runtime_label.setText(_TOTAL_RUNTIME.format('...'))
        self.runtime_thread = RuntimeCalculationThread(self.playlist, self.duration_cache)
        self.runtime_thread.value_updated.connect(self.update_total_runtime_progress_bar)
        self.runtime_thread.completed.connect(self.total_runtime_thread_completed)
        self.runtime_thread.error.connect(self.total_runtime_thread_error)
        self.runtime_thread.start()

    def _stop_runtime_thread(self) -> None:
        if self.runtime_thread is None:
            return

        self.runtime_thread.stop = True
        self.runtime_thread.wait(QDeadlineTimer(10 * 1000))
        self.runtime_thread = None
        self.durations_loaded = False
        self.duration_cache = {}

    def _refresh_buttons(self) -> None:
        for button in self.selection_dependent_buttons:
            button.setEnabled(len(self.item_list.selectedItems()) > 0)
