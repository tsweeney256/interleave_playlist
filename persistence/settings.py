import os

import yaml

import util

_SETTINGS_FILE = os.path.join(util.SCRIPT_LOC, 'config', 'settings.yml')


def get_font_size() -> int:
    return _get_settings()['font-size']


def get_play_command() -> str:
    return _get_settings()['play-command']


def get_dark_mode() -> bool:
    return _get_settings()['dark-mode']


def _get_settings():
    with open(_SETTINGS_FILE, 'r') as f:
        return yaml.safe_load(f)


def _create_settings_file():
    if not os.path.exists(_SETTINGS_FILE):
        with open(_SETTINGS_FILE, 'w') as f:
            f.write("""### This settings file is recreated with defaults if deleted ###
font-size: 12
play-command: mpv
dark-mode: false""")
