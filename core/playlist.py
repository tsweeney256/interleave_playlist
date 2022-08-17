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

import re
from copy import copy
from itertools import groupby
from os import path, listdir
from os.path import isfile
from re import Pattern

from natsort import natsorted, ns

from core.interleave import interleave_all
from persistence import settings
from persistence.input_ import Location, Timed, Group

LocationGroups = dict[Group, list[str]]
FileGroup = tuple[str, str]


def get_playlist(locations: list[Location],
                 watched_list: list[FileGroup],
                 search_filter: str = "") -> list[FileGroup]:
    location_groups: LocationGroups = {}
    for loc in locations:
        location_groups.update(_group_items_by_regex(loc))

    def _key(i): return i[0].priority
    priority_location_groups: dict[int, LocationGroups] = {
        k: dict(v) for k, v in groupby(sorted(location_groups.items(), key=_key), _key)
    }
    data: list[FileGroup] = []
    for lg in priority_location_groups.values():
        data += _get_playlist(lg, watched_list, search_filter)
    return data


def _get_playlist(location_groups: LocationGroups,
                  watched_list: list[FileGroup],
                  search_filter: str = "") -> list[FileGroup]:
    data: list[list[FileGroup]] = []
    watched_names = [i[0] for i in watched_list]
    for group, locations in location_groups.items():
        timed_slice = _timed_slice(group.timed, locations) if group.timed else locations
        items = [(loc, group.name) for loc in filter(
            lambda i: (i in timed_slice
                       and search_filter.upper() in path.basename(i).upper()
                       and path.basename(i) not in watched_names
                       and _matches_whitelist(i, group.whitelist)
                       and not _matches_blacklist(i, group.blacklist)
                       and (not settings.get_exclude_directories() or isfile(i))),
            locations)]
        if items:
            data.append(items)
    if not data:
        return []
    # Need to do some convoluted nonsense to remove alphabetical biasing in the playlist.
    # Need to make sure the playlist is ordered by least recently watched in a way
    # that doesn't interfere with the quality of the interleaving.
    masked: list[list[tuple[int, int]]] = _mask_data(data)
    masked_playlist: list[tuple[int, int]] = interleave_all(masked)
    sorted_group: list[list[FileGroup]] = _sort_data_by_least_recently_watched(data, watched_list)
    return _unmask_playlist(masked_playlist, sorted_group)


def _group_items_by_regex(loc: Location) -> dict[Group, list[str]]:
    regex_str: str = loc.regex if loc.regex is not None else ''
    regex: Pattern = re.compile(regex_str)
    grouped_items: dict[Group, list[str]] = {}
    group_dict = {group.name: group for group in loc.groups}

    paths = [(loc.name, i) for i in listdir(loc.name)]
    for a in loc.additional:
        paths += [(a, i) for i in listdir(a)]
    paths = list(map(lambda i: path.join(i[0], i[1]),
                     natsorted(paths, key=lambda i: i[1], alg=ns.IGNORECASE)))
    for p in paths:
        match = regex.match(path.basename(p))
        if not match:
            continue
        match_dict = match.groupdict()
        if 'group' in match_dict:
            group_name = loc.default_group.name + '_____' + path.basename(match.group('group'))
            group = _get_from_dict_key_superset(group_name, group_dict)
            if group is None:
                group = copy(loc.default_group)
                group.name = group_name
                group_dict[group_name] = group
        else:
            group = loc.default_group
        group_members = grouped_items.setdefault(group, list())
        group_members.append(p)
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


def _get_watched_groups_lru(watched_list: list[FileGroup]):
    groups: list[str] = []
    for i in reversed(watched_list):
        if not i[1] in groups:
            groups.append(i[1])
    groups.reverse()
    return groups


def _mask_data(data: list[list[FileGroup]]) -> list[list[tuple[int, int]]]:
    masked: list[list[tuple[int, int]]] = []
    group_idx: dict[int, int] = {}
    for group in data:
        masked_group: list[tuple[int, int]] = []
        masked.append(masked_group)
        idx = group_idx.setdefault(len(group), 0)
        for _ in group:
            masked_group.append((idx, len(group)))
        group_idx[len(group)] = idx + 1
    return masked


def _sort_data_by_least_recently_watched(data: list[list[FileGroup]],
                                         watched_list: list[FileGroup]) -> list[list[FileGroup]]:
    lru_groups: list[str] = _get_watched_groups_lru(watched_list)
    ideal_group_sorting: list[list[FileGroup]] = []
    for i, d in enumerate(data):
        if d[0][1] not in lru_groups:
            ideal_group_sorting.append(d)
    for group in lru_groups:
        for i, d in enumerate(data):
            if d[0][1] == group:
                ideal_group_sorting.append(d)
    return ideal_group_sorting


def _unmask_playlist(masked_playlist: list[tuple[int, int]], data: list[list[FileGroup]]) \
        -> list[FileGroup]:
    playlist: list[FileGroup] = []
    data_size_dict: dict[int, list[list[FileGroup]]] = {}
    group_len_group_idx_dict: dict[int, dict[int, int]] = {}
    group_file_idx_dict: dict[tuple[int, int], int] = {}
    for group in data:
        sized_data: list[list[FileGroup]] = data_size_dict.setdefault(len(group), [])
        sized_data.append(group)
    for masked_group in masked_playlist:
        group_idx, group_len = masked_group
        group_idx_dict = group_len_group_idx_dict.setdefault(group_len, {})
        mapped_group_idx = group_idx_dict.setdefault(group_idx, len(group_idx_dict))
        group_file_idx = group_file_idx_dict.setdefault(masked_group, 0)
        group_file_idx_dict[masked_group] = group_file_idx + 1

        playlist.append(data_size_dict[group_len][mapped_group_idx][group_file_idx])
    return playlist
