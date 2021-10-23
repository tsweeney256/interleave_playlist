import os
import subprocess
from os import path

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont, QColor, QBrush
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton

import settings
from core.playlist import get_playlist
from interface import open_with_default_application, _create_playlist_dict

WATCHED_COLOR = QBrush(QColor.fromRgbF(1, 0, 0))


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.playlist_dict = _create_playlist_dict()
        self.item_list = QListWidget()
        self.item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        font = QFont()
        font.setPointSize(settings.get_font_size())
        self.item_list.setFont(font)
        self._refresh()
        self.item_list.selectAll()

        play_btn = QPushButton('Play')
        play_btn.clicked.connect(self.play)

        watched_btn = QPushButton('Mark Watched')
        watched_btn.clicked.connect(self.mark_watched)

        unwatched_btn = QPushButton('Unmark Watched')
        unwatched_btn.clicked.connect(self.unmark_watched)

        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh)

        open_input_btn = QPushButton('Open Input File')
        open_input_btn.clicked.connect(self.open_settings)

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

    @Slot()
    def play(self):
        subprocess.run([settings.get_play_command()]
                       + [self.playlist_dict[i.text()] for i in self.item_list.selectedItems()])

    @Slot()
    def mark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(False)))
        with open('config/blacklist.txt', 'r') as f:
            with open('config/tmp.txt', 'w') as tmp:
                for line in f:
                    if line.strip() != '' and line.strip() in full_playlist:
                        tmp.write(line.strip() + '\n')
                tmp.writelines('\n'.join(
                    map(lambda i: i.text(),
                        filter(lambda i: i.background() != WATCHED_COLOR,  # lol
                               self.item_list.selectedItems()))))
        os.replace('config/tmp.txt', 'config/blacklist.txt')

        for item in self.item_list.selectedItems():
            item.setBackground(WATCHED_COLOR)

    @Slot()
    def unmark_watched(self):
        full_playlist = list(map(path.basename, get_playlist(False)))
        with open('config/blacklist.txt', 'r') as f:
            with open('config/tmp.txt', 'w') as tmp:
                for line in f:
                    if (line.strip() not in map(lambda i: i.text(), self.item_list.selectedItems())
                            and line.strip() != ''
                            and line.strip() in full_playlist):
                        tmp.write(line)
        os.replace('config/tmp.txt', 'config/blacklist.txt')

        white = QBrush(QColor.fromRgbF(1, 1, 1))
        for item in self.item_list.selectedItems():
            item.setBackground(white)

    @Slot()
    def refresh(self):
        self._refresh()

    def _refresh(self):
        self.playlist_dict = _create_playlist_dict()
        self.item_list.clear()
        self.item_list.addItems(self.playlist_dict.keys())

    @Slot()
    def open_settings(self):
        open_with_default_application('config/settings.yml')

    @Slot()
    def open_blacklist(self):
        open_with_default_application('config/blacklist.txt')
