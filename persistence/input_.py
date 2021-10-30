import os
import re

import yaml
from yaml.parser import ParserError

from persistence import state


class Location:
    def __init__(self, name, whitelist, blacklist, regex):
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.regex = regex


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_ = _get_input(state.get_last_input_file())
    locations = []
    for loc in input_['locations']:
        locations.append(
            Location(loc['name'],
                     loc['whitelist'] if 'whitelist' in loc else input_.get('whitelist'),
                     loc['blacklist'] if 'blacklist' in loc else input_.get('blacklist'),
                     loc['regex'] if 'regex' in loc else input_.get('regex')))
    return locations


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
        _validate_whitelist(i)
        _validate_blacklist(i)
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
            _validate_whitelist(loc)
            _validate_blacklist(i)
            _validate_regex(loc)

    except ParserError as e:
        raise InvalidInputFile("Unable to parse input file") from e
    return i


def _validate_wb_list(d: dict, wb_list: str):
    if wb_list in d:
        if not isinstance(d[wb_list], list):
            raise InvalidInputFile(wb_list + ' must be a list')
        for white in d[wb_list]:
            if not isinstance(white, str):
                raise InvalidInputFile(wb_list + ' entries must be strings')


def _validate_whitelist(d: dict):
    _validate_wb_list(d, 'blacklist')


def _validate_blacklist(d: dict):
    _validate_wb_list(d, 'whitelist')


def _validate_regex(d: dict):
    if 'regex' in d and d['regex'] is not None:
        if not isinstance(d['regex'], str):
            raise InvalidInputFile("Regex must be a string")
        try:
            re.compile(d['regex'])
        except re.error:
            raise InvalidInputFile("Regex is invalid")
