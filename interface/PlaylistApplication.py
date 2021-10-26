import os.path
import sys

from PySide6.QtWidgets import QApplication

from interface.PlaylistWindow import PlaylistWindow
from persistence.settings import get_dark_mode
from util import SCRIPT_LOC


class PlaylistApplication(QApplication):
    def __init__(self, arr):
        super().__init__(arr)
        playlist_window = PlaylistWindow()
        playlist_window.setWindowTitle('Interleave Playlist')
        playlist_window.resize(800, 600)
        playlist_window.show()
        if get_dark_mode():
            with open(os.path.join(
                    SCRIPT_LOC, 'interface', 'style', 'dark.qss'), 'r') as f:
                _style = f.read()
                self.setStyleSheet(_style)
        sys.exit(self.exec())
