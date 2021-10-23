import sys

from PySide6.QtWidgets import QApplication

from interface.PlaylistWindow import PlaylistWindow


class PlaylistApplication(QApplication):
    def __init__(self, arr):
        super().__init__(arr)
        playlist_window = PlaylistWindow()
        playlist_window.setWindowTitle('Interleave Playlist')
        playlist_window.resize(800, 600)
        playlist_window.show()
        sys.exit(self.exec())
