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

import json
import os

import util
from persistence.input_ import _get_input

_STATE_FILE = os.path.join(util.SCRIPT_LOC, 'config', 'state.json')


def get_last_input_file() -> str:
    return _get_state()['last-input-file']


def set_last_input_file(input_file: str):
    _get_input(input_file)  # ensure that the input can be read
    _set_state('last-input-file', input_file)


def _get_state():
    with open(_STATE_FILE, 'r') as f:
        return json.load(f)


def _set_state(key: str, val: any):
    state = _get_state()
    state[key] = val
    with open(_STATE_FILE, 'w') as f:
        return json.dump(state, f)


def _create_state_file():
    if not os.path.exists(_STATE_FILE):
        with open(_STATE_FILE, 'w') as f:
            f.write('{"last-input-file": "See config/input.yml.example"}')
