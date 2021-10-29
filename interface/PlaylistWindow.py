import os
import subprocess
import threading
from os import path

from PySide6.QtCore import Slot, QEvent, Qt
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton, QMessageBox, QFileDialog, QLabel

from core.playlist import get_playlist
from interface import open_with_default_application, _create_playlist_dict, _get_temp_file_name
from persistence import settings, input_, state

_WATCHED_COLOR = (QBrush(QColor.fromRgb(255, 121, 121))
                  if not settings.get_dark_mode() else
                  QBrush(QColor.fromRgb(77, 12, 12)))

_TOTAL_SHOWS_TEXT = 'Total Shows: {}'
_SELECTED_SHOWS_TEXT = 'Selected Shows: {}'


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self._row_color1, self._row_color2 = self._get_standard_row_colors()

        label_font = QFont()
        label_font.setPointSize(16)
        self.total_shows_label = QLabel()
        self.total_shows_label.setFont(label_font)

        self.playlist_dict: dict[str, str] = {}
        self.item_list: QListWidget = self._create_item_list()

        self.total_selected_label = QLabel()
        self.total_selected_label.setFont(label_font)
        self.item_list.selectAll()

        label_layout = QVBoxLayout()
        label_layout.addWidget(self.total_shows_label)
        label_layout.addWidget(self.total_selected_label)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.item_list)

        layout = QVBoxLayout(self)
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
            subprocess.run([settings.get_play_command()]
                           + [self.playlist_dict[i.text()] for i in self.item_list.selectedItems()])
        if self.playlist_dict is not None:
            thread = threading.Thread(target=_impl)
            thread.start()

    # O(1) memory, just cause
    @Slot()
    def mark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(input_.get_locations(), [])))
        with open(input_.get_watched_file_name(), 'r') as f:
            with open(_get_temp_file_name(), 'w') as tmp:
                for line in f:
                    if line.strip() != '' and line.strip() in full_playlist:
                        tmp.write(line.strip() + '\n')
                tmp.writelines('\n'.join(
                    map(lambda i: i.text(),
                        filter(lambda i: i.background() != _WATCHED_COLOR,  # lol
                               self.item_list.selectedItems()))))
        os.replace(_get_temp_file_name(), input_.get_watched_file_name())

        for item in self.item_list.selectedItems():
            item.setBackground(_WATCHED_COLOR)

    @Slot()
    def unmark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(input_.get_locations(), [])))
        with open(input_.get_watched_file_name(), 'r') as f:
            with open(_get_temp_file_name(), 'w') as tmp:
                for line in f:
                    if (line.strip() not in map(lambda i: i.text(), self.item_list.selectedItems())
                            and line.strip() != ''
                            and line.strip() in full_playlist):
                        tmp.write(line)
        os.replace(_get_temp_file_name(), input_.get_watched_file_name())

        for i in range(len(self.item_list.selectedItems())):
            color = self._row_color1 if i % 2 == 0 else self._row_color2
            self.item_list.selectedItems()[i].setBackground(color)

    @Slot()
    def refresh(self):
        self._refresh(self.item_list)

    def _refresh(self, item_list: QListWidget):
        item_list.clear()
        self.playlist_dict = _create_playlist_dict()
        if self.playlist_dict is not None:
            item_list.addItems(self.playlist_dict.keys())
        self.total_shows_label.setText(_TOTAL_SHOWS_TEXT.format(len(self.playlist_dict)))

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

    @Slot()
    def open_watched_file(self):
        def _impl():
            open_with_default_application(input_.get_watched_file_name())
        thread = threading.Thread(target=_impl)
        thread.start()

    @Slot()
    def selection_change(self):
        self.total_selected_label.setText(
            _SELECTED_SHOWS_TEXT.format(len(self.item_list.selectedItems())))

    @staticmethod
    def _get_standard_row_colors():
        # wow this is silly
        _hidden_list = QListWidget()
        _hidden_list.setAlternatingRowColors(True)
        _hidden_list.addItems(["", ""])
        color1 = _hidden_list.item(0).background()
        color2 = _hidden_list.item(1).background()
        return color1, color2
