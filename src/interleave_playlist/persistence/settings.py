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

import interleave_playlist
from interleave_playlist import CriticalUserError

_SETTINGS_FILE = pathlib.Path(os.path.join(appdirs.user_config_dir(interleave_playlist.APP_NAME),
                                           'settings.yml'))
_CACHED_FILE: dict[str, Any] = {}

T = typing.TypeVar('T')


class InvalidSettingsYmlException(Exception):

    def __init__(self, message: str, key: Any, value: Any) -> None:
        self.message = message
        self.key = key
        self.value = value


def get_font_size() -> int:
    return _get_settings_and_convert('font-size', int)


def get_play_command() -> str:
    return _get_settings_and_convert('play-command', str)


def get_dark_mode() -> bool:
    return _get_settings_and_convert('dark-mode', _convert_to_bool)


def get_max_watched_remembered() -> int:
    return _get_settings_and_convert('max-watched-remembered', int)


def get_exclude_directories() -> bool:
    return _get_settings_and_convert('exclude-directories', _convert_to_bool)


def _get_settings(option: str) -> Any:
    global _CACHED_FILE
    if not _CACHED_FILE:
        with open(_SETTINGS_FILE, 'r') as f:
            yaml = YAML()
            yaml.preserve_quotes = True  # type: ignore
            _CACHED_FILE = yaml.load(f)
            if _CACHED_FILE is None:
                _CACHED_FILE = {}
            default_settings = _get_default_settings()
        for key in default_settings.keys():
            if key not in _CACHED_FILE:
                _CACHED_FILE[key] = default_settings[key]
        with open(_SETTINGS_FILE, 'w') as f:
            yaml.dump(_CACHED_FILE, f)

    return _CACHED_FILE[option]


def _get_settings_and_convert(key: str, conv: typing.Callable[[Any], T]) -> T:
    value = _get_settings(key)
    try:
        return conv(value)
    except Exception:
        raise InvalidSettingsYmlException(
            f"Invalid settings.yml value for '{key}': {value}", key, value
        )


def _convert_to_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    elif isinstance(x, str):
        if x.upper() == 'TRUE':
            return True
        elif x.upper() == 'FALSE':
            return False
    raise ValueError(f'Unable to convert {x} to type bool')


def _get_default_settings() -> dict[str, Any]:
    return {
        'font-size': 12,
        'play-command': 'mpv',
        'dark-mode': False,
        'max-watched-remembered': 100,
        'exclude-directories': True
    }


def create_settings_file() -> None:
    if not os.path.exists(_SETTINGS_FILE):
        if not os.path.exists(_SETTINGS_FILE.parent):
            os.mkdir(_SETTINGS_FILE.parent)
        with open(_SETTINGS_FILE, 'w') as f:
            yaml = YAML()
            yaml.dump(_get_default_settings(), f)


def validate_settings_file() -> None:
    options = [
        get_font_size,
        get_play_command,
        get_dark_mode,
        get_max_watched_remembered,
        get_exclude_directories
    ]
    errors = []
    for option in options:
        try:
            option()
        except InvalidSettingsYmlException as e:
            errors.append(e)
    if errors:
        message = 'Invalid settings.yml values:'
        for error in errors:
            message += f'\n    {error.key}: {error.value}'
        raise CriticalUserError(message)
