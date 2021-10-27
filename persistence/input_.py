import os

import yaml
from yaml.parser import ParserError

from persistence import state


class Location:
    def __init__(self, name, filters):
        self.name = name
        self.filters = filters


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_ = _get_input(state.get_last_input_file())
    locations = []
    for loc in input_['locations']:
        locations.append(Location(loc['name'],
                                  loc['filters'] if 'filters' in loc else input_['filters']))
    return locations


def get_global_filter() -> list[str]:
    return _get_input(state.get_last_input_file())['filter']


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
        if 'filters' not in i:
            raise InvalidInputFile('Input requires top level "filters"')
        if not isinstance(i['filters'], list):
            raise InvalidInputFile('"filters" must be a list')
        for filter_ in i['filters']:
            if not isinstance(filter_, str):
                raise InvalidInputFile('Filter entries must be strings')
        if 'locations' not in i:
            raise InvalidInputFile('Input requires "locations"')
        if not isinstance(i['locations'], list):
            raise InvalidInputFile('"locations" must be a list')
        for loc in i['locations']:
            if 'name' not in loc:
                raise InvalidInputFile("Locations must have names")
            if not isinstance(loc['name'], str):
                raise InvalidInputFile("Location names must be strings")
            if not os.path.exists(loc['name']):
                raise LocationNotFound(loc['name'])
            if 'filters' in loc and loc['filters'] is not None and isinstance(loc['filters'], str):
                raise InvalidInputFile("Location specific filters must be strings")
    except ParserError as e:
        raise InvalidInputFile("Unable to parse input file") from e
    return i
