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

from core import PlaylistEntry
from core.interleave import interleave_all
from persistence import Group, Location, Timed, settings

FilePathsByGroup = dict[Group, list[str]]
FileGroup = tuple[str, str]
PlaylistEntriesByGroup = dict[Group, list[PlaylistEntry]]


def get_playlist(locations: list[Location],
                 watched_list: list[FileGroup],
                 search_filter: str = "") -> list[PlaylistEntry]:
    location_groups: PlaylistEntriesByGroup = {}
    for loc in locations:
        location_groups.update(_group_items_by_regex(loc))

    def _key(i) -> int: return i[0].priority
    entries_by_priority: dict[int, PlaylistEntriesByGroup] = {
        k: dict(v) for k, v in groupby(sorted(location_groups.items(), key=_key), _key)
    }
    data: list[PlaylistEntry] = []
    for ep in entries_by_priority.values():
        data.extend(_get_playlist(ep, watched_list, search_filter))
    return data


def _get_playlist(entries_by_group: PlaylistEntriesByGroup,
                  watched_list: list[FileGroup],
                  search_filter: str = "") -> list[PlaylistEntry]:
    filtered_entries: list[list[PlaylistEntry]] = []
    watched_names = [i[0] for i in watched_list]
    for group, entries in entries_by_group.items():
        timed_slice = _timed_slice(group.timed, entries) if group.timed else entries
        group_entries = [entry for entry in filter(
            lambda i: (i in timed_slice
                       and search_filter.upper() in path.basename(i.filename).upper()
                       and path.basename(i.filename) not in watched_names
                       and _matches_whitelist(i.filename, group.whitelist)
                       and not _matches_blacklist(i.filename, group.blacklist)
                       and (not settings.get_exclude_directories() or isfile(i.filename))),
            entries)]
        if group_entries:
            filtered_entries.append(group_entries)
    if not filtered_entries:
        return []
    # Need to do some convoluted nonsense to remove alphabetical biasing in the playlist.
    # Need to make sure the playlist is ordered by least recently watched in a way
    # that doesn't interfere with the quality of the interleaving.
    masked: list[list[tuple[int, int]]] = _mask_data(filtered_entries)
    masked_playlist: list[tuple[int, int]] = interleave_all(masked)
    sorted_group: list[list[PlaylistEntry]] = _sort_data_by_least_recently_watched(filtered_entries, watched_list)
    return _unmask_playlist(masked_playlist, sorted_group)


def _group_items_by_regex(loc: Location) -> PlaylistEntriesByGroup:
    regex_str: str = loc.regex if loc.regex is not None else ''
    regex: Pattern = re.compile(regex_str)
    grouped_items: PlaylistEntriesByGroup = {}
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
            group_name = path.basename(match.group('group')).strip()
            group = _get_from_dict_key_superset(group_name, group_dict)
            if group is None:
                group = copy(loc.default_group)
                group_dict[group_name] = group
            # Overwrite name so we always use the full name
            group.name = group_name
        else:
            group = loc.default_group
        group_members = grouped_items.setdefault(group, list())
        group_members.append(PlaylistEntry(p, loc, group))
    return grouped_items


def _timed_slice(timed: Timed, loc_list: list[PlaylistEntry]) -> list[PlaylistEntry]:
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


def _mask_data(data: list[list[PlaylistEntry]]) -> list[list[tuple[int, int]]]:
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


def _sort_data_by_least_recently_watched(data: list[list[PlaylistEntry]],
                                         watched_list: list[FileGroup]) -> list[list[PlaylistEntry]]:
    lru_groups: list[str] = _get_watched_groups_lru(watched_list)
    ideal_group_sorting: list[list[PlaylistEntry]] = []
    for i, d in enumerate(data):
        if d[0].group.name not in lru_groups:
            ideal_group_sorting.append(d)
    for group in lru_groups:
        for i, d in enumerate(data):
            if d[0].group.name == group:
                ideal_group_sorting.append(d)
    return ideal_group_sorting


def _unmask_playlist(masked_playlist: list[tuple[int, int]], data: list[list[PlaylistEntry]]) \
        -> list[PlaylistEntry]:
    playlist: list[PlaylistEntry] = []
    data_size_dict: dict[int, list[list[PlaylistEntry]]] = {}
    group_len_group_idx_dict: dict[int, dict[int, int]] = {}
    group_file_idx_dict: dict[tuple[int, int], int] = {}
    for group in data:
        sized_data: list[list[PlaylistEntry]] = data_size_dict.setdefault(len(group), [])
        sized_data.append(group)
    for masked_group in masked_playlist:
        group_idx, group_len = masked_group
        group_idx_dict = group_len_group_idx_dict.setdefault(group_len, {})
        mapped_group_idx = group_idx_dict.setdefault(group_idx, len(group_idx_dict))
        group_file_idx = group_file_idx_dict.setdefault(masked_group, 0)
        group_file_idx_dict[masked_group] = group_file_idx + 1

        playlist.append(data_size_dict[group_len][mapped_group_idx][group_file_idx])
    return playlist
