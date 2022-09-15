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
import os
import platform
import subprocess
from math import log10, ceil

from PySide6.QtWidgets import QMessageBox

from interleave_playlist.core.playlist import get_playlist, PlaylistEntry
from interleave_playlist.persistence import input_
from interleave_playlist.persistence.watched import get_watched


# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
def open_with_default_application(filepath: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def _create_playlist(search_filter: str = "") -> list[PlaylistEntry]:
    try:
        return get_playlist(input_.get_locations(), get_watched(), search_filter)
    except FileNotFoundError:
        QMessageBox(text="Input yml file not found: {}\n\n"
                         "Please create or find file and open it"
                    .format(input_.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    except input_.InvalidInputFile as e:
        QMessageBox(text="Error reading yml file. Please fix it and try again\n{}\n{}"
                    .format(e, input_.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    except input_.LocationNotFound as e:
        QMessageBox(text="Location from input file not found. Please fix it and try again\n{}\n{}"
                    .format(e, input_.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    return []


def _get_temp_file_name():
    return input_.get_watched_file_name() + '.tmp'


def _get_duration_str(ms: int, override_ms: int):
    hours, remainder = divmod(ms, 1000 * 60 * 60)
    minutes, remainder = divmod(remainder, 1000 * 60)
    seconds, remainder = divmod(remainder, 1000)
    hours_override = override_ms / (1000 * 60 * 60)
    hours_len = 2 if hours_override <= 0 else max(ceil(log10(hours_override)), 2)
    hours_fmt = '{' + ':0{}d'.format(hours_len) + '}'
    return (hours_fmt + ':{:02d}:{:02d}').format(hours, minutes, seconds)
