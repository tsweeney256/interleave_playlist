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
import sys
from math import log10, ceil

from PySide6.QtWidgets import QMessageBox

from interleave_playlist.core.playlist import get_playlist, PlaylistEntry
from interleave_playlist.persistence import input_
from interleave_playlist.persistence.watched import get_watched


# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
def open_with_default_application(filepath: str) -> None:
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    # This is actually ridiculous https://github.com/python/mypy/issues/8547
    elif sys.platform == 'win32' or sys.platform == 'cygwin':  # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def _create_playlist(search_filter: str = "", use_cache: bool = False) -> list[PlaylistEntry]:
    def show_warning(text: str) -> None:
        msg_box = QMessageBox()
        msg_box.setWindowTitle('Error')
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.show()
    try:
        return get_playlist(input_.get_locations(), get_watched(), search_filter, use_cache)
    except FileNotFoundError:
        show_warning(f'Input yml file not found: {input_.get_last_input_file()}\n\n'
                     'Please create or find file and open it')
    except input_.InvalidInputFile as e:
        show_warning(f'Error reading yml file. Please fix it and try again\n'
                     f'{input_.get_last_input_file()}\n{e}')
    except input_.LocationNotFound as e:
        show_warning(f'Location from input file not found. Please fix it and try again\n'
                     f'{input_.get_last_input_file()}\n{e}')
    return []


def _get_temp_file_name() -> str:
    return input_.get_watched_file_name() + '.tmp'


def _get_duration_str(ms: int, override_ms: int) -> str:
    hours, remainder = divmod(ms, 1000 * 60 * 60)
    minutes, remainder = divmod(remainder, 1000 * 60)
    seconds, remainder = divmod(remainder, 1000)
    hours_override = override_ms / (1000 * 60 * 60)
    hours_len = 2 if hours_override <= 0 else max(ceil(log10(hours_override)), 2)
    hours_fmt = '{' + ':0{}d'.format(hours_len) + '}'
    return (hours_fmt + ':{:02d}:{:02d}').format(hours, minutes, seconds)
