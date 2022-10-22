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
from copy import copy
from itertools import groupby
from os import path
from re import Pattern
from typing import Any

from natsort import natsorted, ns

from interleave_playlist.core import PlaylistEntry
from interleave_playlist.core.interleave import interleave_all
from interleave_playlist.persistence import Group, Location, Timed
from interleave_playlist.persistence import settings

FilePathsByGroup = dict[Group, list[str]]
FileGroup = tuple[str, str]
PlaylistEntriesByGroup = dict[Group, list[PlaylistEntry]]
_FILE_CACHE: dict[str, list[str]] = {}


def get_playlist(locations: list[Location],
                 watched_list: list[FileGroup],
                 search_filter: str = "",
                 use_cache: bool = False) -> list[PlaylistEntry]:
    location_groups: PlaylistEntriesByGroup = {}
    for loc in locations:
        paths: list[str] = _get_paths_from_location(loc, use_cache)
        location_groups.update(_group_items_by_regex(loc, paths))

    def _key(i: tuple[Group, list[PlaylistEntry]]) -> int: return i[0].priority
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
    watched_names = [i[0].upper() for i in watched_list]
    for group, entries in entries_by_group.items():
        # Ordering is important! Filter out invalid considerations first
        group_entries = [entry for entry in filter(
            lambda i: (_matches_whitelist(path.basename(i.filename), group.whitelist)
                       and not _matches_blacklist(path.basename(i.filename), group.blacklist)
                       and (not settings.get_exclude_directories() or os.path.isfile(i.filename))),
            entries)]
        # Now that invalid considerations are gone, we can slice by timing considerations
        # or else invalid considerations will be part of the result, then removed anyway
        group_entries = _timed_slice(group.timed, group_entries) if group.timed else group_entries
        # Now that invalid and timed considerations are gone, we can finally remove things
        # that we've already seen and match by the search filter
        group_entries = [
            entry for entry in filter(
                lambda i: path.basename(i.filename).upper() not in watched_names
                and search_filter.upper() in path.basename(i.filename).upper(),
                group_entries
            )
        ]
        if group_entries:
            filtered_entries.append(group_entries)
    if not filtered_entries:
        return []
    # Need to do some convoluted nonsense to remove alphabetical biasing in the playlist.
    # Need to make sure the playlist is ordered by least recently watched in a way
    # that doesn't interfere with the quality of the interleaving.
    masked: list[list[tuple[int, int]]] = _mask_data(filtered_entries)
    masked_playlist: list[tuple[int, int]] = interleave_all(masked)
    sorted_group: list[list[PlaylistEntry]] = \
        _sort_data_by_least_recently_watched(filtered_entries, watched_list)
    return _unmask_playlist(masked_playlist, sorted_group)


def _get_paths_from_location(loc: Location, use_cache: bool) -> list[str]:
    if use_cache and loc.name in _FILE_CACHE:
        return _FILE_CACHE[loc.name]
    path_parts = [(loc.name, i) for i in os.listdir(loc.name)]
    for a in loc.additional:
        path_parts += [(a, i) for i in os.listdir(a)]
    paths = list(map(lambda i: path.join(i[0], i[1]),
                     natsorted(path_parts, key=lambda i: i[1], alg=ns.IGNORECASE)))
    _FILE_CACHE[loc.name] = paths
    return paths


def _group_items_by_regex(loc: Location, paths: list[str]) -> PlaylistEntriesByGroup:
    regex_str: str = loc.regex if loc.regex is not None else ''
    regex: Pattern = re.compile(regex_str)
    grouped_items: PlaylistEntriesByGroup = {}
    group_dict = {group.name.upper(): group for group in loc.groups}

    for p in paths:
        match = regex.match(path.basename(p))
        if not match:
            continue
        match_dict = match.groupdict()
        if 'group' in match_dict:
            group_name = path.basename(match.group('group')).strip()
            group = _get_from_dict_key_superset(group_name.upper(), group_dict)
            if group is None:
                group = copy(loc.default_group)
                group_dict[group_name.upper()] = group
            # Overwrite name so we always use the full name
            group.name = group_name
        else:
            group = loc.default_group
        group_members = grouped_items.setdefault(group, list())
        group_members.append(PlaylistEntry(p, loc, group))
    return grouped_items


def _timed_slice(timed: Timed, loc_list: list[PlaylistEntry]) -> list[PlaylistEntry]:
    cur_release = min(timed.get_current(), len(loc_list))
    if cur_release < 0:
        return []
    return loc_list[timed.first: cur_release + 1]


def _matches_whitelist(s: str, whitelist: list[str]) -> bool:
    if not whitelist:
        return True
    for white in whitelist:
        if white.upper() in s.upper():
            return True
    return False


def _matches_blacklist(s: str, blacklist: list[str]) -> bool:
    if not blacklist:
        return False
    for black in blacklist:
        if black and black.upper() in s.upper():
            return True
    return False


def _get_from_dict_key_superset(super_key: str, d: dict[str, Any]) -> Any:
    for k, v in d.items():
        if k in super_key:
            return v


def _get_watched_groups_lru(watched_list: list[FileGroup]) -> list[str]:
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


def _sort_data_by_least_recently_watched(
        data: list[list[PlaylistEntry]],
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
