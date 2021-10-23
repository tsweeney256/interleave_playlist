import subprocess
from os import path

from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton

import settings
from core.playlist import get_playlist
from interface import open_with_default_application


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.playlist = list(get_playlist())
        self.playlist_map = dict(zip(map(path.basename, self.playlist), self.playlist))

        self.item_list = QListWidget()
        self.item_list.addItems(self.playlist_map.keys())
        self.item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.font = QFont()
        self.font.setPointSize(settings.get_font_size())
        self.item_list.setFont(self.font)
        self.item_list.selectAll()

        self.play_btn = QPushButton('Play')
        self.play_btn.clicked.connect(self.play)

        self.watched_btn = QPushButton('Mark Watched')
        self.unwatched_btn = QPushButton('Unmark Watched')

        self.open_input_btn = QPushButton('Open Input File')
        self.open_input_btn.clicked.connect(self.open_settings)

        self.open_watched_btn = QPushButton('Open Watched File')
        self.open_watched_btn.clicked.connect(self.open_blacklist)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.play_btn)
        self.button_layout.addWidget(self.watched_btn)
        self.button_layout.addWidget(self.unwatched_btn)
        self.button_layout.addWidget(self.open_input_btn)
        self.button_layout.addWidget(self.open_watched_btn)

        self.list_layout = QVBoxLayout()
        self.list_layout.addWidget(self.item_list)

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.button_layout)
        self.layout.addLayout(self.list_layout)

    @Slot()
    def play(self):
        subprocess.run([settings.get_play_command()]
                       + [self.playlist_map[i.text()] for i in self.item_list.selectedItems()])

    @Slot()
    def open_settings(self):
        open_with_default_application('config/settings.yml')

    @Slot()
    def open_blacklist(self):
        open_with_default_application('config/blacklist.txt')

