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
from os import path
from typing import Any

from PySide6.QtWidgets import QListWidgetItem

from interleave_playlist.core.playlist import PlaylistEntry

_USER_TYPE: int = 1001


class PlaylistWindowItem(QListWidgetItem):

    def __init__(self, *args: list[Any], value: PlaylistEntry, **kwargs: dict[Any, Any]):
        super().__init__(*args, type=_USER_TYPE, **kwargs)  # type: ignore
        self.value: PlaylistEntry = value
        self.setText(path.basename(value.filename))

    def setValue(self, value: PlaylistEntry) -> None:
        self.value = value

    def getValue(self) -> PlaylistEntry:
        return self.value
