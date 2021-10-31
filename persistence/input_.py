import os
import re
from datetime import datetime, timedelta

import yaml
from crontab import CronTab
from yaml.parser import ParserError

from persistence import state


class Timed:
    def __init__(self, start: datetime, cron: CronTab, first: int, amount: int):
        self.start = start
        self.cron = cron
        self.first = first if first is not None and first > 0 else 1
        self.amount = amount if amount is not None and amount > 0 else 1

    def get_current(self) -> int:
        if self.start > datetime.now():
            return -1
        i: int = self.first
        now: datetime = datetime.now()
        cur: datetime = self.start
        diff: timedelta = timedelta(seconds=self.cron.next(cur, default_utc=False))
        # TODO: do this in O(1)
        while cur + diff < now:
            cur += diff
            diff = timedelta(seconds=self.cron.next(cur, default_utc=False))
            i += self.amount
        return i


class Location:
    def __init__(self, name: str, whitelist: list[str], blacklist: list[str],
                 regex: str, timed: Timed):
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.regex = regex
        self.timed = timed


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_: dict = _get_input(state.get_last_input_file())
    locations = []
    for loc in input_['locations']:
        if loc.get('timed'):
            timed_yml: dict = loc['timed']
            timed = Timed(
                datetime.fromisoformat(timed_yml['start']),
                CronTab(timed_yml['cron']),
                timed_yml.get('first'),
                timed_yml.get('amount'),
            )
        else:
            timed = None
        locations.append(
            Location(
                loc['name'],
                loc['whitelist'] if 'whitelist' in loc else input_.get('whitelist'),
                loc['blacklist'] if 'blacklist' in loc else input_.get('blacklist'),
                loc['regex'] if 'regex' in loc else input_.get('regex'),
                timed
            )
        )
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
            _validate_timed(loc)

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
    if d.get('regex'):
        if not isinstance(d['regex'], str):
            raise InvalidInputFile("Regex must be a string")
        try:
            re.compile(d['regex'])
        except re.error:
            raise InvalidInputFile("Regex is invalid")


def _validate_timed(d: dict):
    if d.get('timed'):
        if 'start' not in d['timed']:
            raise InvalidInputFile('Usage of timed requires a start datetime')
        if 'cron' not in d['timed']:
            raise InvalidInputFile('Usage of timed requires a cron rule')
        try:
            datetime.fromisoformat(d['timed']['start'])
        except (TypeError, ValueError) as e:
            raise InvalidInputFile('Invalid start date format. Requires ISO string') from e
        try:
            CronTab(d['timed']['cron'])
        except ValueError as e:
            raise InvalidInputFile('Invalid cron format') from e
        if 'first' in d['timed'] and not isinstance(d['timed']['first'], int):
            raise InvalidInputFile('timed.first must be an integer')
        if 'amount' in d['timed'] and not isinstance(d['timed']['amount'], int):
            raise InvalidInputFile('timed.amount must be an integer')
