#    Interleave Playlist
#    Copyright (C) 2021-2022 Thomas Sweeney
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
from collections.abc import Iterable
from datetime import datetime, timedelta
from pathlib import Path

from crontab import CronTab
from ruamel.yaml import YAML, YAMLError

from persistence import state


class Timed:
    def __init__(self, start: datetime, cron: CronTab, first: int,
                 amount: int, start_at_cron: bool):
        self.start = (start.astimezone()
                      if start.tzinfo is None else
                      start)
        self.cron = cron
        self.first = (first if first is not None and first > 0 else 1) - 1
        self.amount = amount if amount is not None and amount > 0 else 1
        self.start_at_cron = start_at_cron

    def __repr__(self):
        return str(self.__dict__)

    def get_current(self) -> int:
        now: datetime = datetime.now().astimezone()
        if self.start > now:
            return -1
        initial: int = self.first + (self.amount if not self.start_at_cron else 0)
        first_diff = timedelta(seconds=self.cron.next(self.start, default_utc=False))
        first_cron_amount: int = self.amount if self.start + first_diff < now else 0
        if first_cron_amount == 0 and self.start_at_cron:
            return -1
        diff = timedelta(seconds=self.cron.next(self.start + first_diff, default_utc=False))
        cron_amount = self.amount * max((now - (self.start + first_diff)) // diff, 0)
        return initial + first_cron_amount + cron_amount - 1


class Group:
    def __init__(self, name: str, priority: int, whitelist: list[str], blacklist: list[str],
                 timed: Timed):
        self.name = name
        self.priority = priority if priority is not None else sys.maxsize
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.timed = timed

    def __repr__(self):
        return str(self.__dict__)


class Location:
    def __init__(self, name: str, additional: list[str], default_group: Group, regex: str,
                 groups: list[Group]):
        self.name = name
        self.additional = additional
        self.default_group = default_group
        self.regex = regex
        self.groups = groups if groups is not None else []

    def __repr__(self):
        return str(self.__dict__)


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_: dict = _get_input(state.get_last_input_file())
    locations = []
    for loc in input_['locations']:
        if 'disabled' in loc and loc['disabled'] is True:
            continue
        options = [loc, input_]
        locations.append(
            Location(
                loc['name'],
                loc['additional'] if 'additional' in loc else [],
                Group(
                    loc['name'],
                    _nested_get('priority', options),
                    _nested_get('whitelist', options),
                    _nested_get('blacklist', options),
                    _get_timed(loc['timed']) if 'timed' in loc else None,
                ),
                _nested_get('regex', options),
                _get_group_list(loc['groups'], options) if 'groups' in loc else []
            )
        )
    return locations


def get_watched_file_name():
    fn = state.get_last_input_file() + '.watched.txt'
    if not os.path.exists(fn):
        with open(fn, 'w'):
            pass
    return fn


def drop_groups(location_groups: Iterable[tuple[str, str]]) -> None:
    input_ = _get_input(state.get_last_input_file())
    for location_group in location_groups:
        location_name = location_group[0]
        location = next(filter(lambda i: i['name'] == location_name, input_['locations']))
        if len(location_group) < 2:
            location['disabled'] = True
            continue
        group_name = location_group[1].strip()
        blacklist: list[str] = location.setdefault('blacklist', [])
        if group_name not in blacklist:
            blacklist.append(group_name)
    yaml = YAML()
    yaml.dump(input_, Path(state.get_last_input_file()))


def _get_group_list(groups: list[dict[str, any]], options: list[dict[str, any]]):
    data = []
    for g in groups:
        data.append(Group(
            g['name'],
            _nested_get('priority', options),
            _nested_get('whitelist', options),
            _nested_get('blacklist', options),
            _nested_get('timed', options),
        ))
    return data


def _get_timed(d: dict[str, any]):
    return Timed(
        datetime.fromisoformat(d['start']),
        CronTab(d['cron']),
        d.get('first'),
        d.get('amount'),
        d.get('start-at-cron'),
    )


def _get_input(input_file: str):
    try:
        with open(input_file, 'r') as f:
            yaml = YAML()
            yaml.preserve_quotes = True
            yml = yaml.load(f)
        _validate_group(yml)
        if 'locations' not in yml:
            raise InvalidInputFile('Input requires "locations"')
        if not isinstance(yml['locations'], list):
            raise InvalidInputFile('"locations" must be a list')
        for loc in yml['locations']:
            if 'name' not in loc:
                raise InvalidInputFile('Locations must have names')
            if not isinstance(loc['name'], str):
                raise InvalidInputFile('Location names must be strings')
            if not os.path.exists(loc['name']):
                raise LocationNotFound(loc['name'])
            if 'disabled' in loc and not isinstance(loc['disabled'], bool):
                raise InvalidInputFile('"disabled" must be a boolean')
            _validate_group(loc)
            _validate_timed(loc)
            if 'groups' in loc:
                if not isinstance(loc['groups'], list):
                    raise InvalidInputFile('groups must be a list')
                _validate_groups(loc['groups'])
            if 'additional' in loc:
                if not isinstance(loc['additional'], list):
                    raise InvalidInputFile('"additional" must be a list')
                for i in loc['additional']:
                    if not isinstance(i, str):
                        raise InvalidInputFile('"additional" entries must be strings')

    except YAMLError as e:
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


def _validate_group(group: dict):
    validators = [
        _validate_whitelist,
        _validate_blacklist,
        _validate_regex,
        _validate_priority,
    ]
    for validator in validators:
        validator(group)


def _validate_groups(groups: list[dict]):
    for group in groups:
        _validate_group(group)


def _nested_get(key: str, options: list[dict[str, any]]):
    for option in options:
        if key in option:
            return option.get(key)
