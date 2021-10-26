import os

import yaml
from yaml.parser import ParserError

from persistence import state


class InvalidInputFile(Exception):
    pass


def get_locations() -> list[str]:
    return _get_input(state.get_last_input_file())['locations']


def get_watched_file_name():
    fn = state.get_last_input_file() + '.watched.txt'
    if not os.path.exists(fn):
        with open(fn, 'w'):
            pass
    return fn


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
