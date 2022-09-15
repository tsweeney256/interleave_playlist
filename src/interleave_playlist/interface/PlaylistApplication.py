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

import os.path
import sys
from traceback import format_exception

from PySide6.QtWidgets import QApplication, QMessageBox

from interleave_playlist.interface.PlaylistWindow import PlaylistWindow
from interleave_playlist.persistence.settings import get_dark_mode
from interleave_playlist.util import SCRIPT_LOC


class PlaylistApplication(QApplication):
    def __init__(self, arr):
        super().__init__(arr)
        playlist_window = PlaylistWindow()
        playlist_window.setWindowTitle('Interleave Playlist')
        playlist_window.resize(800, 600)
        playlist_window.show()
        if get_dark_mode():
            with open(os.path.join(
                    SCRIPT_LOC,
                    'src',
                    'interleave_playlist',
                    'interface',
                    'style',
                    'dark.qss'
            ), 'r') as f:
                _style = f.read()
                self.setStyleSheet(_style)
        sys.exit(self.exec())


def excepthook(cls, exception, traceback):
    QMessageBox(text="Encountered an unhandled exception. This is a bug.\n"
                     "Please file a bug report so that this can be fixed\n\n{}"
                .format(''.join(format_exception(cls, exception, traceback))),
                icon=QMessageBox.Warning).exec()


sys.excepthook = excepthook
