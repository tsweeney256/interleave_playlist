import yaml


def _get_settings():
    with open('config/settings.yml', 'r') as f:
        return yaml.safe_load(f)


def create_needed_files():
    with open('config/blacklist.txt', 'a'):
        pass


def get_locations() -> list[str]:
    return _get_settings()['locations']


def get_font_size() -> int:
    return _get_settings()['font-size']


def get_play_command() -> str:
    return _get_settings()['play-command']


def get_dark_mode() -> bool:
    return _get_settings()['dark-mode']
