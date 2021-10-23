from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QListWidget, QWidget, QAbstractItemView, QHBoxLayout, \
    QPushButton

import settings
from core.playlist import get_playlist


class PlaylistWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.item_list = QListWidget()
        self.item_list.addItems(get_playlist())
        self.item_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.font = QFont()
        self.font.setPointSize(settings.get_font_size())
        self.item_list.setFont(self.font)

        self.play_btn = QPushButton('Play')
        self.watched_btn = QPushButton('Mark Watched')
        self.unwatched_btn = QPushButton('Unmark Watched')
        self.open_input_btn = QPushButton('Open Input File')
        self.open_watched_btn = QPushButton('Open Watched File')

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

