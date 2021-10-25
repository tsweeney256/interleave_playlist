import json
import os.path
import sys

import yaml
from yaml.parser import ParserError

from settings.InvalidInputFile import InvalidInputFile

SCRIPT_LOC = os.path.dirname(os.path.realpath(sys.argv[0]))
_SETTINGS_FILE = os.path.join(SCRIPT_LOC, 'config', 'settings.yml')
_STATE_FILE = os.path.join(SCRIPT_LOC, 'config', 'state.json')


def get_watched_file_name():
    fn = get_last_input_file() + '.watched.txt'
    if not os.path.exists(fn):
        with open(fn, 'w'):
            pass
    return fn


def create_needed_files():
    if not os.path.exists(_SETTINGS_FILE):
        _create_settings_file()
    if not os.path.exists(_STATE_FILE):
        _create_state_file()


def get_locations() -> list[str]:
    return _get_input(get_last_input_file())['locations']


def get_font_size() -> int:
    return _get_settings()['font-size']


def get_play_command() -> str:
    return _get_settings()['play-command']


def get_dark_mode() -> bool:
    return _get_settings()['dark-mode']


def get_last_input_file() -> str:
    return _get_state()['last-input-file']


def set_last_input_file(input_file: str):
    _get_input(input_file)  # ensure that the input can be read
    _set_state('last-input-file', input_file)


def _get_settings():
    with open(_SETTINGS_FILE, 'r') as f:
        return yaml.safe_load(f)


def _get_input(input_file: str):
    try:
        with open(input_file, 'r') as f:
            i = yaml.safe_load(f)
        if 'locations' not in i:
            raise InvalidInputFile
        if not isinstance(i['locations'], list):
            raise InvalidInputFile
        for loc in i['locations']:
            if not _expected_loc_type(loc):
                raise InvalidInputFile
    except ParserError as e:
        raise InvalidInputFile from e
    return i


def _expected_loc_type(location):
    return isinstance(location, str)


def _get_state():
    with open(_STATE_FILE, 'r') as f:
        return json.load(f)


def _set_state(key: str, val: any):
    state = _get_state()
    state[key] = val
    with open(_STATE_FILE, 'w') as f:
        return json.dump(state, f)


def _create_settings_file():
    with open(_SETTINGS_FILE, 'w') as f:
        f.write("""### This settings file is recreated with defaults if deleted ###
font-size: 12
play-command: mpv
dark-mode: false""")


def _create_state_file():
    with open(_STATE_FILE, 'w') as f:
        f.write('{"last-input-file": "See config/input.yml.example"}')
