#    Interleave Playlist
#    Copyright (C) 2022-2025 Thomas Sweeney
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
import json
import os.path
from pathlib import Path
from typing import Any, Optional

import appdirs

import interleave_playlist


class _KEYS:
    LAST_INPUT_FILE: str = 'last-input-file'


_STATE_FILE = Path(os.path.join(appdirs.user_data_dir(interleave_playlist.APP_NAME),
                                'state.json'))
_DEFAULT_STATE = {
    _KEYS.LAST_INPUT_FILE: '',
}

_CACHED_STATE: dict[str, Any] = {}


def create_state_file() -> None:
    if not os.path.exists(_STATE_FILE.parent):
        os.mkdir(_STATE_FILE.parent)
    if not os.path.exists(_STATE_FILE):
        with open(_STATE_FILE, 'w') as f:
            json.dump(_DEFAULT_STATE, f)


def get_last_input_file() -> Optional[Path]:
    last_input_file: str = _get_json_value(_KEYS.LAST_INPUT_FILE)
    if last_input_file:
        return Path(last_input_file)
    else:
        return None


def set_last_input_file(last_input_file: Path) -> None:
    _set_json(_KEYS.LAST_INPUT_FILE, str(last_input_file))


def _get_json_value(key: str) -> Any:
    _load_state()
    return _CACHED_STATE[key] if key in _CACHED_STATE else ''


def _set_json(key: str, value: Any) -> None:
    _load_state()
    _CACHED_STATE[key] = value
    _save_state()


def _load_state() -> None:
    global _CACHED_STATE
    if not _CACHED_STATE:
        with open(_STATE_FILE, 'r') as f:
            _CACHED_STATE = json.load(f)


def _save_state() -> None:
    with open(_STATE_FILE, 'w') as f:
        json.dump(_CACHED_STATE, f)
