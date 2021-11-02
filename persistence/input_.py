#    Interleave Playlist
#    Copyright (C) 2021 Thomas Sweeney
#    This file is part of Interleave Playlist.
#    Interleave Playlist is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    Interleave Playlist is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
from datetime import datetime, timedelta

import yaml
from crontab import CronTab
from yaml.parser import ParserError

from persistence import state


class Timed:
    def __init__(self, start: datetime, cron: CronTab, first: int,
                 amount: int, start_at_cron: bool):
        self.start = start
        self.cron = cron
        self.first = (first if first is not None and first > 0 else 1) - 1
        self.amount = amount if amount is not None and amount > 0 else 1
        self.start_at_cron = start_at_cron

    def get_current(self) -> int:
        if self.start > datetime.now():
            return -1
        now: datetime = datetime.now()
        initial: int = self.first + (self.amount if not self.start_at_cron else 0)
        first_diff = timedelta(seconds=self.cron.next(self.start, default_utc=False))
        first_cron_amount: int = self.amount if self.start + first_diff < now else 0
        if first_cron_amount == 0 and self.start_at_cron:
            return -1
        diff = timedelta(seconds=self.cron.next(self.start + first_diff, default_utc=False))
        cron_amount = self.amount * max((now - (self.start + diff)) // diff, 0)
        return initial + first_cron_amount + cron_amount - 1


class Location:
    def __init__(self, name: str, whitelist: list[str], blacklist: list[str],
                 regex: str, timed: Timed, priority: int):
        self.name = name
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.regex = regex
        self.timed = timed
        self.priority = priority if priority is not None else sys.maxsize


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
                timed_yml.get('start-at-cron'),
            )
        else:
            timed = None
        locations.append(
            Location(
                loc['name'],
                loc['whitelist'] if 'whitelist' in loc else input_.get('whitelist'),
                loc['blacklist'] if 'blacklist' in loc else input_.get('blacklist'),
                loc['regex'] if 'regex' in loc else input_.get('regex'),
                timed,
                loc['priority'] if 'priority' in loc else input_.get('priority')
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
            yml = yaml.safe_load(f)
        overridable_value_validators = [
            _validate_whitelist,
            _validate_blacklist,
            _validate_regex,
            _validate_priority,
        ]
        for validator in overridable_value_validators:
            validator(yml)
        if 'locations' not in yml:
            raise InvalidInputFile('Input requires "locations"')
        if not isinstance(yml['locations'], list):
            raise InvalidInputFile('"locations" must be a list')
        for loc in yml['locations']:
            if 'name' not in loc:
                raise InvalidInputFile("Locations must have names")
            if not isinstance(loc['name'], str):
                raise InvalidInputFile("Location names must be strings")
            if not os.path.exists(loc['name']):
                raise LocationNotFound(loc['name'])
            for validator in overridable_value_validators:
                validator(loc)
            _validate_timed(loc)

    except ParserError as e:
        raise InvalidInputFile("Unable to parse input file") from e
    return yml


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


def _validate_priority(d: dict):
    if 'priority' in d and not isinstance(d['priority'], int):
        raise InvalidInputFile('priority must be an integer')
