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
from types import TracebackType
from typing import Type, Optional, Sequence

from PySide6.QtWidgets import QApplication, QMessageBox

from interleave_playlist import SCRIPT_LOC
from interleave_playlist.interface.PlaylistWindow import PlaylistWindow
from interleave_playlist.persistence.settings import get_dark_mode


class PlaylistApplication(QApplication):
    def __init__(self, arr: Sequence[str]):
        super().__init__(arr)
        playlist_window = PlaylistWindow()
        playlist_window.setWindowTitle('Interleave Playlist')
        playlist_window.resize(800, 600)
        playlist_window.show()
        if get_dark_mode():
            with open(os.path.join(
                    SCRIPT_LOC,
                    'interface',
                    'style',
                    'dark.qss'
            ), 'r') as f:
                _style = f.read()
                self.setStyleSheet(_style)
        sys.exit(self.exec())


def excepthook(cls: Type[BaseException], exception: BaseException,
               traceback: Optional[TracebackType]) -> None:
    err = "".join(format_exception(cls, exception, traceback))
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Error")
    msg_box.setText(f'Encountered an unhandled exception. This is a bug.\n'
                    f'Please file a bug report so that this can be fixed\n\n{err}')
    msg_box.setIcon(QMessageBox.Icon.Critical)
    msg_box.exec()


sys.excepthook = excepthook
