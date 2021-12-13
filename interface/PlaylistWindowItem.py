#    Interleave Playlist
#    Copyright (C) 2021 Thomas Sweeney
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
from os import path

from PySide6.QtWidgets import QListWidgetItem

from core.playlist import FileGroup

_USER_TYPE: int = 1001


class PlaylistWindowItem(QListWidgetItem):

    def __init__(self, *args, value: FileGroup, **kwargs):
        super().__init__(*args, type=_USER_TYPE, **kwargs)
        self.value: FileGroup = value
        self.setText(path.basename(value[0]))

    def setValue(self, value: FileGroup):
        self.value = value

    def getValue(self):
        return self.value
