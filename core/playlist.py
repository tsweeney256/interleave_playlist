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
from itertools import groupby
from os import path, listdir
from re import Pattern
from typing import Iterator

from core.interleave import interleave_all
from persistence.input_ import Location, Timed


def get_playlist(locations: list[Location], watched_list: list[str]) -> iter:
    def _key(i): return i.priority
    priority_locations = {k: list(v) for k, v in groupby(sorted(locations, key=_key), _key)}
    data = []
    for locations in priority_locations.values():
        data += _get_playlist(locations, watched_list)
    return data


def _get_playlist(locations: list[Location], watched_list: list[str]) -> iter:
    data = []
    for loc in locations:
        regex_str = loc.regex if loc.regex is not None else ''
        regex: Pattern = re.compile(regex_str)
        loc_list = list(map(lambda i: loc.name + '/' + i, sorted(listdir(loc.name))))
        timed_slice = _timed_slice(loc.timed, loc_list) if loc.timed else loc_list
        items = list(filter(
            lambda i: (i in timed_slice
                       and path.basename(i) not in watched_list
                       and _matches_whitelist(i, loc.whitelist)
                       and not _matches_blacklist(i, loc.blacklist)
                       and regex.match(i)),
            loc_list))
        grouped_items = _group_items_by_regex(items, regex)
        if len(grouped_items) > 0:
            data.append(interleave_all(list(grouped_items.values())))
    return interleave_all(data)


def _group_items_by_regex(items: Iterator[str], regex: Pattern):
    grouped_items = {}
    for item in items:
        match = regex.match(item)
        match_dict = match.groupdict()
        if 'group' in match_dict:
            group = grouped_items.setdefault(path.basename(match.group('group')), list())
        else:
            group = grouped_items.setdefault('', list())
        group.append(item)
    return grouped_items


def _timed_slice(timed: Timed, loc_list: list[str]):
    if timed is None:
        return loc_list
    cur_release = min(timed.get_current(), len(loc_list))
    if cur_release < 0:
        return []
    return loc_list[timed.first: cur_release + 1]


def _matches_whitelist(s: str, whitelist: list[str]):
    if whitelist is None:
        return True
    for white in whitelist:
        if white in s:
            return True
    return False


def _matches_blacklist(s: str, blacklist: list[str]):
    if blacklist is None:
        return False
    for black in blacklist:
        if black and black in s:
            return True
    return False
