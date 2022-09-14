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
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from crontab import CronTab
from ruamel.yaml import YAML, YAMLError

from core import PlaylistEntry
from persistence import Location, Group, Timed, _STATE_FILE


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


def _get_group_list(groups: list[dict[str, any]], additional_options: list[dict[str, any]]):
    data = []
    for g in groups:
        options = [g, *additional_options]
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
        if 'locations' not in yml and 'manual' not in yml:
            raise InvalidInputFile('Input requires "locations" or "manual"')
        if 'locations' in yml:
            _validate_locations(yml['locations'])
        if 'manual' in yml:
            _validate_manual(yml['manual'])
    except YAMLError as e:
        raise InvalidInputFile("Unable to parse input file") from e
    return yml


def _validate_locations(locations):
    if not isinstance(locations, list):
        raise InvalidInputFile('"locations" must be a list')
    for loc in locations:
        _validate_name(loc, "Location")
        if not os.path.exists(loc['name']):
            raise LocationNotFound(loc['name'])
        _validate_disabled(loc)
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


def _validate_manual(manual):
    if not isinstance(manual, list):
        raise InvalidInputFile('"manual" must be a list')
    for m in manual:
        _validate_name(m, "Manual rule")
        _validate_disabled(m)
        _validate_group(m)
        _validate_timed(m)
        _validate_command(m)
        _validate_variables(m)
        _validate_episode_scheme(m)
        _validate_seasons(m)


def _validate_season(d: dict):
    _validate_name(d, "season")
    if 'episode-count' not in d:
        raise InvalidInputFile('seasons must have an "episode-count"')
    if not isinstance(d['episode-count'], int):
        raise InvalidInputFile('"episode-count" must be an integer')


def _validate_seasons(d: dict):
    if 'seasons' not in d:
        return
    seasons = d['seasons']
    if not isinstance(seasons, list):
        raise InvalidInputFile('"seasons" must be a list')
    for season in seasons:
        _validate_season(season)


def _validate_episode_scheme(d: dict):
    if 'episode-scheme' not in d:
        raise InvalidInputFile('"manual" rules require "episode-scheme"')
    if not isinstance(d['episode-scheme'], str):
        raise InvalidInputFile("'episode-scheme' must be a string")


def _validate_variables(d: dict):
    if 'variables' not in d:
        return
    variables = d['variables']
    if not isinstance(variables, dict):
        raise InvalidInputFile('"variables" must be a map of string key/values')
    for k, v in variables.items():
        if not isinstance(v, str):
            raise InvalidInputFile(f'"variable" {k} is not a string')


def _validate_command(d: dict):
    if 'command' in d and not isinstance(d['command'], str):
        raise InvalidInputFile('"command" must be a string')


def _validate_name(d: dict, obj_name: str):
    if 'name' not in d:
        raise InvalidInputFile(f'{obj_name}s must have names')
    if not isinstance(d['name'], str):
        raise InvalidInputFile(f'{obj_name} names must be strings')


def _validate_disabled(d: dict):
    if 'disabled' in d and not isinstance(d['disabled'], bool):
        raise InvalidInputFile('"disabled" must be a boolean')


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


def get_last_input_file() -> str:
    return _get_state()['last-input-file']


def set_last_input_file(input_file: str):
    _get_input(input_file)  # ensure that the input can be read
    _set_state('last-input-file', input_file)


def _get_state():
    with open(_STATE_FILE, 'r') as f:
        return json.load(f)


def _set_state(key: str, val: any):
    state = _get_state()
    state[key] = val
    with open(_STATE_FILE, 'w') as f:
        return json.dump(state, f)
