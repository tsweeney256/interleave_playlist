import os
import re

import yaml
from yaml.parser import ParserError

from persistence import state


class Location:
    def __init__(self, name, filters, regex):
        self.name = name
        self.filters = filters
        self.regex = regex


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_ = _get_input(state.get_last_input_file())
    locations = []
    for loc in input_['locations']:
        locations.append(Location(loc['name'],
                                  loc['filters'] if 'filters' in loc else input_.get('filters'),
                                  loc['regex'] if 'regex' in loc else input_.get('regex')))
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
        _validate_filters(i)
        _validate_regex(i)
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
            _validate_filters(loc)
            _validate_regex(loc)

    except ParserError as e:
        raise InvalidInputFile("Unable to parse input file") from e
    return i


def _validate_filters(d: dict):
    if 'filters' in d:
        if not isinstance(d['filters'], list):
            raise InvalidInputFile('"filters" must be a list')
        for filter_ in d['filters']:
            if not isinstance(filter_, str):
                raise InvalidInputFile('Filter entries must be strings')


def _validate_regex(d: dict):
    if 'regex' in d and d['regex'] is not None:
        if not isinstance(d['regex'], str):
            raise InvalidInputFile("Regex must be a string")
        try:
            re.compile(d['regex'])
        except re.error:
            raise InvalidInputFile("Regex is invalid")
