import json

import yaml


def _get_settings():
    with open('config/settings.yml', 'r') as f:
        return yaml.safe_load(f)


def _get_input():
    with open('config/input.yml', 'r') as f:
        return yaml.safe_load(f)


def _get_state():
    with open('config/state.json', 'r') as f:
        return json.load(f)


def _set_state(key: str, val: any):
    state = _get_state()
    state[key] = val
    with open('config/state.json', 'w') as f:
        return json.dump(state, f)


def create_needed_files():
    with open('config/blacklist.txt', 'a'):
        pass


def get_locations() -> list[str]:
    return _get_input()['locations']


def get_font_size() -> int:
    return _get_settings()['font-size']


def get_play_command() -> str:
    return _get_settings()['play-command']


def get_dark_mode() -> bool:
    return _get_settings()['dark-mode']


def get_last_input_file() -> str:
    return _get_state()['last-input-file']


def set_last_input_file(last: str):
    _set_state('last-input-file', last)
