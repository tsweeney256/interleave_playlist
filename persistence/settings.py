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
from pathlib import Path

from ruamel.yaml import YAML

import util

_SETTINGS_FILE = os.path.join(util.SCRIPT_LOC, 'config', 'settings.yml')
_CACHED_FILE = None


def get_font_size() -> int:
    return _get_settings('font-size')


def get_play_command() -> str:
    return _get_settings('play-command')


def get_dark_mode() -> bool:
    return _get_settings('dark-mode')


def get_max_watched_remembered() -> int:
    return _get_settings('max-watched-remembered')


def get_exclude_directories() -> bool:
    return _get_settings('exclude-directories')


def _get_settings(option):
    global _CACHED_FILE
    if _CACHED_FILE is None:
        with open(_SETTINGS_FILE, 'r') as f:
            yaml = YAML()
            yaml.preserve_quotes = True
            _CACHED_FILE = yaml.load(f)
            default_settings = _get_default_settings()
        for key in default_settings.keys():
            if key not in _CACHED_FILE:
                _CACHED_FILE[key] = default_settings[key]
            yaml.dump(_CACHED_FILE, Path(_SETTINGS_FILE))

    return _CACHED_FILE[option]


def _get_default_settings() -> dict[str, any]:
    return {
        'font-size': 12,
        'play-command': 'mpv',
        'dark-mode': False,
        'max-watched-remembered': 100,
        'exclude-directories': True
    }


def _create_settings_file():
    if not os.path.exists(_SETTINGS_FILE):
        with open(_SETTINGS_FILE, 'w') as f:
            yaml = YAML()
            yaml.dump(_get_default_settings(), Path(_SETTINGS_FILE))
