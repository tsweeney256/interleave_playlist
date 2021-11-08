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

import re
from copy import copy
from itertools import groupby
from os import path, listdir
from re import Pattern

from natsort import natsorted, ns

from core.interleave import interleave_all
from persistence.input_ import Location, Timed, Group

LocationGroups = dict[Group, list[str]]


def get_playlist(locations: list[Location], watched_list: list[str]) -> list[str]:
    location_groups: dict[Group, list[str]] = {}
    for loc in locations:
        location_groups.update(_group_items_by_regex(loc))

    def _key(i): return i[0].priority
    priority_location_groups: dict[int, LocationGroups] = {
        k: dict(v) for k, v in groupby(sorted(location_groups.items(), key=_key), _key)
    }
    data = []
    for lg in priority_location_groups.values():
        data += _get_playlist(lg, watched_list)
    return data


def _get_playlist(location_groups: LocationGroups, watched_list: list[str]) -> list[str]:
    data: list[list[str]] = []
    for group, locations in location_groups.items():
        timed_slice = _timed_slice(group.timed, locations) if group.timed else locations
        items = list(filter(
            lambda i: (i in timed_slice
                       and path.basename(i) not in watched_list
                       and _matches_whitelist(i, group.whitelist)
                       and not _matches_blacklist(i, group.blacklist)),
            locations))
        data.append(items)
    return interleave_all(data)


def _group_items_by_regex(loc: Location) -> dict[Group, list[str]]:
    regex_str: str = loc.regex if loc.regex is not None else ''
    regex: Pattern = re.compile(regex_str)
    grouped_items: dict[Group, list[str]] = {}
    group_dict = {group.name: group for group in loc.groups}
    paths = list(map(lambda i: loc.default_group.name + '/' + i,
                     natsorted(listdir(loc.default_group.name), alg=ns.IGNORECASE)))
    for p in paths:
        match = regex.match(path.basename(p))
        if not match:
            continue
        match_dict = match.groupdict()
        if 'group' in match_dict:
            group_name = path.basename(match.group('group'))
            group = _get_from_dict_key_superset(group_name, group_dict)
            if group is None:
                group = copy(loc.default_group)
                group.name = group_name
                group_dict[group_name] = group
            group = grouped_items.setdefault(group, list())
        else:
            group = grouped_items.setdefault(loc.default_group, list())
        group.append(p)
    return grouped_items


def _timed_slice(timed: Timed, loc_list: list[str]) -> list[str]:
    if timed is None:
        return loc_list
    cur_release = min(timed.get_current(), len(loc_list))
    if cur_release < 0:
        return []
    return loc_list[timed.first: cur_release + 1]


def _matches_whitelist(s: str, whitelist: list[str]) -> bool:
    if whitelist is None:
        return True
    for white in whitelist:
        if white in s:
            return True
    return False


def _matches_blacklist(s: str, blacklist: list[str]) -> bool:
    if blacklist is None:
        return False
    for black in blacklist:
        if black and black in s:
            return True
    return False


def _get_from_dict_key_superset(super_key: str, d: dict[str, any]) -> any:
    for k, v in d.items():
        if k in super_key:
            return v
