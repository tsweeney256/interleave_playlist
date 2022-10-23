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
import pathlib
import typing
from typing import Any

import appdirs
from ruamel.yaml import YAML

_SETTINGS_FILE = pathlib.Path(os.path.join(appdirs.user_config_dir(),
                                           'interleave_playlist',
                                           'settings.yml'))
_CACHED_FILE: dict[str, Any] = {}


def get_font_size() -> int:
    return typing.cast(int, _get_settings('font-size'))


def get_play_command() -> str:
    return typing.cast(str, _get_settings('play-command'))


def get_dark_mode() -> bool:
    return typing.cast(bool, _get_settings('dark-mode'))


def get_max_watched_remembered() -> int:
    return typing.cast(int, _get_settings('max-watched-remembered'))


def get_exclude_directories() -> bool:
    return typing.cast(bool, _get_settings('exclude-directories'))


def _get_settings(option: str) -> Any:
    global _CACHED_FILE
    if not _CACHED_FILE:
        with open(_SETTINGS_FILE, 'r') as f:
            yaml = YAML()
            yaml.preserve_quotes = True  # type: ignore
            _CACHED_FILE = yaml.load(f)
            default_settings = _get_default_settings()
        for key in default_settings.keys():
            if key not in _CACHED_FILE:
                _CACHED_FILE[key] = default_settings[key]
        with open(_SETTINGS_FILE, 'w') as f:
            yaml.dump(_CACHED_FILE, f)

    return _CACHED_FILE[option]


def _get_default_settings() -> dict[str, Any]:
    return {
        'font-size': 12,
        'play-command': 'mpv',
        'dark-mode': False,
        'max-watched-remembered': 100,
        'exclude-directories': True
    }


def _create_settings_file() -> None:
    if not os.path.exists(_SETTINGS_FILE):
        if not os.path.exists(_SETTINGS_FILE.parent):
            os.mkdir(_SETTINGS_FILE.parent)
        with open(_SETTINGS_FILE, 'w') as f:
            yaml = YAML()
            yaml.dump(_get_default_settings(), f)
