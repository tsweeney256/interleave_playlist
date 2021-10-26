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
