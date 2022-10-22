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
import json
import os
import re
import typing
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from crontab import CronTab
from ruamel.yaml import YAML, YAMLError

from interleave_playlist.core import PlaylistEntry
from interleave_playlist.persistence import Location, Group, Timed, _STATE_FILE


class InvalidInputFile(Exception):
    pass


class LocationNotFound(Exception):
    pass


def get_locations() -> list[Location]:
    input_: dict = _get_input(get_last_input_file())
    locations = []
    for loc in input_['locations']:
        if 'disabled' in loc and loc['disabled'] is True:
            continue
        options = [loc, input_]
        locations.append(
            Location(
                loc['name'],
                Group(
                    loc['name'],
                    loc['name'],
                    _nested_get('priority', options),
                    _nested_get('whitelist', options),
                    _nested_get('blacklist', options),
                    _get_timed(loc['timed']) if 'timed' in loc else None,
                ),
                loc['additional'] if 'additional' in loc else [],
                _nested_get('regex', options),
                _get_group_list(loc['groups'], options) if 'groups' in loc else []
            )
        )
    return locations


def get_watched_file_name() -> str:
    fn = get_last_input_file() + '.watched.txt'
    if not os.path.exists(fn):
        with open(fn, 'w'):
            pass
    return fn


def drop_groups(entries: Iterable[PlaylistEntry]) -> None:
    input_ = _get_input(get_last_input_file())
    for entry in entries:
        location = next(filter(lambda i: i['name'] == entry.location.name, input_['locations']))
        if entry.group.name == entry.location.name:
            location['disabled'] = True
            continue
        group_name = entry.group.name
        blacklist: list[str] = location.setdefault('blacklist', [])
        if group_name not in blacklist:
            blacklist.append(group_name)
    yaml = YAML()
    yaml.dump(input_, Path(get_last_input_file()))


def _get_group_list(data: list[dict[str, Any]], additional_options: list[dict[str, Any]]) \
        -> list[Group]:
    groups = []
    for g in data:
        options = [g, *additional_options]
        groups.append(Group(
            g['name'],
            _nested_get('name', additional_options),
            _nested_get('priority', options),
            _nested_get('whitelist', options),
            _nested_get('blacklist', options),
            _nested_get('timed', options),
        ))
    return groups


def _get_timed(d: dict[str, Any]) -> Timed:
    return Timed(
        datetime.fromisoformat(d['start']),
        CronTab(d['cron']),
        d.get('first'),
        d.get('amount'),
        d.get('start-at-cron'),
    )


def _get_input(input_file: str) -> dict[str, Any]:
    try:
        with open(input_file, 'r') as f:
            yaml = YAML()
            yaml.preserve_quotes = True  # type: ignore
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
    return typing.cast(dict[str, Any], yml)


def _validate_wb_list(d: dict, wb_list: str) -> None:
    if wb_list in d:
        if not isinstance(d[wb_list], list):
            raise InvalidInputFile(wb_list + ' must be a list')
        for white in d[wb_list]:
            if not isinstance(white, str):
                raise InvalidInputFile(wb_list + ' entries must be strings')


def _validate_whitelist(d: dict) -> None:
    _validate_wb_list(d, 'blacklist')


def _validate_blacklist(d: dict) -> None:
    _validate_wb_list(d, 'whitelist')


def _validate_regex(d: dict) -> None:
    if d.get('regex'):
        if not isinstance(d['regex'], str):
            raise InvalidInputFile("Regex must be a string")
        try:
            re.compile(d['regex'])
        except re.error:
            raise InvalidInputFile("Regex is invalid")


def _validate_timed(d: dict) -> None:
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


def _validate_priority(d: dict) -> None:
    if 'priority' in d and not isinstance(d['priority'], int):
        raise InvalidInputFile('priority must be an integer')


def _validate_group(group: dict) -> None:
    validators = [
        _validate_whitelist,
        _validate_blacklist,
        _validate_regex,
        _validate_priority,
    ]
    for validator in validators:
        validator(group)


def _validate_groups(groups: list[dict]) -> None:
    for group in groups:
        _validate_group(group)


def _nested_get(key: str, options: list[dict[str, Any]]) -> Any:
    for option in options:
        if key in option:
            return option.get(key)


def get_last_input_file() -> str:
    return typing.cast(str, _get_state()['last-input-file'])


def set_last_input_file(input_file: str) -> None:
    _get_input(input_file)  # ensure that the input can be read
    _set_state('last-input-file', input_file)


def _get_state() -> dict[str, Any]:
    with open(_STATE_FILE, 'r') as f:
        return typing.cast(dict[str, Any], json.load(f))


def _set_state(key: str, val: Any) -> None:
    state = _get_state()
    state[key] = val
    with open(_STATE_FILE, 'w') as f:
        json.dump(state, f)
