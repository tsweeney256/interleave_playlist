import yaml


with open('config/settings.yml', 'r') as f:
    _settings: dict[str] = yaml.safe_load(f)


def create_needed_files():
    with open('config/blacklist.txt', 'a'):
        pass


def get_locations() -> list[str]:
    return _settings['locations']


def get_font_size() -> int:
    return _settings['font-size']
