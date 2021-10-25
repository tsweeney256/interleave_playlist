import os
import subprocess
import threading
from os import path

from PySide6.QtCore import Slot, QEvent, Qt
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton, QMessageBox, QFileDialog

import settings
from core.playlist import get_playlist
from interface import open_with_default_application, _create_playlist_dict, _get_temp_file_name

WATCHED_COLOR = QBrush(QColor.fromRgbF(1, 0, 0))


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.item_list = QListWidget()
        self.item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.item_list.setAlternatingRowColors(True)
        font = QFont()
        font.setPointSize(settings.get_font_size())
        self.item_list.setFont(font)
        try:
            self.playlist_dict: dict[str, str] = _create_playlist_dict()
            self._refresh(self.playlist_dict)
        except FileNotFoundError:
            QMessageBox(text="Input yml file not found: {}\n\n"
                             "Please create or find file and open it"
                        .format(settings.get_last_input_file()),
                        icon=QMessageBox.Warning).exec()
        except settings.InvalidInputFile:
            QMessageBox(text="Unable to parse input yml file. Please fix it and try again\n\n{}"
                        .format(settings.get_last_input_file()),
                        icon=QMessageBox.Warning).exec()
        self.item_list.selectAll()

        play_btn = QPushButton('Play')
        play_btn.clicked.connect(self.play)
        self.item_list.doubleClicked.connect(self.play)
        self.item_list.installEventFilter(self)

        watched_btn = QPushButton('Mark Watched')
        watched_btn.clicked.connect(self.mark_watched)

        unwatched_btn = QPushButton('Unmark Watched')
        unwatched_btn.clicked.connect(self.unmark_watched)

        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh)

        open_input_btn = QPushButton('Open Input File')
        open_input_btn.clicked.connect(self.open_input)

        open_watched_btn = QPushButton('Open Watched File')
        open_watched_btn.clicked.connect(self.open_blacklist)

        button_layout = QHBoxLayout()
        button_layout.addWidget(play_btn)
        button_layout.addWidget(watched_btn)
        button_layout.addWidget(unwatched_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(open_input_btn)
        button_layout.addWidget(open_watched_btn)

        list_layout = QVBoxLayout()
        list_layout.addWidget(self.item_list)

        layout = QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addLayout(list_layout)

        self.item_list.setFocus()

    def eventFilter(self, widget: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            switch: dict[int, callable] = {
                Qt.NoModifier + Qt.Key_Return: self._play,
                Qt.NoModifier + Qt.Key_Enter: self._play,
                Qt.ControlModifier + Qt.Key_W: self.mark_watched,
                Qt.ControlModifier + Qt.Key_U: self.unmark_watched,
                Qt.ControlModifier + Qt.Key_O: self.open_input,
                Qt.ControlModifier + Qt.ShiftModifier + Qt.Key_O: self.open_blacklist
            }
            if event.keyCombination().toCombined() in switch:
                switch[event.keyCombination().toCombined()]()
                return True
        return False

    @Slot()
    def play(self):
        self._play()

    def _play(self):
        def _play_impl():
            subprocess.run([settings.get_play_command()]
                           + [self.playlist_dict[i.text()] for i in self.item_list.selectedItems()])
        if self.playlist_dict is not None:
            thread = threading.Thread(target=_play_impl)
            thread.start()

    # O(1) memory, just cause
    @Slot()
    def mark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(settings.get_locations(), [])))
        with open(settings.get_watched_file_name(), 'r') as f:
            with open(_get_temp_file_name(), 'w') as tmp:
                for line in f:
                    if line.strip() != '' and line.strip() in full_playlist:
                        tmp.write(line.strip() + '\n')
                tmp.writelines('\n'.join(
                    map(lambda i: i.text(),
                        filter(lambda i: i.background() != WATCHED_COLOR,  # lol
                               self.item_list.selectedItems()))))
        os.replace(_get_temp_file_name(), settings.get_watched_file_name())

        for item in self.item_list.selectedItems():
            item.setBackground(WATCHED_COLOR)

    @Slot()
    def unmark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(settings.get_locations(), [])))
        with open(settings.get_watched_file_name(), 'r') as f:
            with open(_get_temp_file_name(), 'w') as tmp:
                for line in f:
                    if (line.strip() not in map(lambda i: i.text(), self.item_list.selectedItems())
                            and line.strip() != ''
                            and line.strip() in full_playlist):
                        tmp.write(line)
        os.replace(_get_temp_file_name(), settings.get_watched_file_name())

        white = QBrush(QColor.fromRgbF(1, 1, 1))
        for item in self.item_list.selectedItems():
            item.setBackground(white)

    @Slot()
    def refresh(self):
        self._refresh(_create_playlist_dict())

    def _refresh(self, playlist_dict: dict[str, str]):
        self.item_list.clear()
        self.playlist_dict = playlist_dict
        if playlist_dict is not None:
            self.item_list.addItems(self.playlist_dict.keys())

    @Slot()
    def open_input(self):
        file_name: str = QFileDialog.getOpenFileName(
            self, 'Open yaml', os.path.expanduser('~'), 'yaml files (*.yml *.yaml)')[0]
        if file_name.strip() == '':
            return
        try:
            settings.set_last_input_file(file_name)
        except settings.InvalidInputFile:
            QMessageBox(text='Error: Attempted to open invalid settings yaml file\n\n'
                             '{}'.format(file_name),
                        icon=QMessageBox.Critical).exec()
            return
        self._refresh(_create_playlist_dict())

    @Slot()
    def open_blacklist(self):
        open_with_default_application(settings.get_watched_file_name())
