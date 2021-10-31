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

import os

import yaml

import util

_SETTINGS_FILE = os.path.join(util.SCRIPT_LOC, 'config', 'settings.yml')
_CACHED_FILE = None


def get_font_size() -> int:
    return _get_settings()['font-size']


def get_play_command() -> str:
    return _get_settings()['play-command']


def get_dark_mode() -> bool:
    return _get_settings()['dark-mode']


def _get_settings():
    global _CACHED_FILE
    if _CACHED_FILE is None:
        with open(_SETTINGS_FILE, 'r') as f:
            _CACHED_FILE = yaml.safe_load(f)
    return _CACHED_FILE


def _create_settings_file():
    if not os.path.exists(_SETTINGS_FILE):
        with open(_SETTINGS_FILE, 'w') as f:
            f.write("""### This settings file is recreated with defaults if deleted ###
font-size: 12
play-command: mpv
dark-mode: false""")
