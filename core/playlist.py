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
from os import path, listdir

from core.interleave import interleave_all
from persistence.input_ import Location


def get_playlist(locations: list[Location], watched_list: list[str]) -> iter:
    data = []
    for loc in locations:
        if loc.regex is not None:
            regex = re.compile(loc.regex)
        else:
            regex = re.compile('')
        items = filter(
            lambda i: (path.basename(i) not in watched_list
                       and _matches_whitelist(i, loc.whitelist)
                       and not _matches_blacklist(i, loc.blacklist)
                       and regex.match(i)),
            map(lambda i: loc.name + '/' + i, listdir(loc.name)))
        grouped_items = {}
        for item in items:
            match = regex.match(item)
            match_dict = match.groupdict()
            if 'group' in match_dict:
                group = grouped_items.setdefault(path.basename(match.group('group')), list())
            else:
                group = grouped_items.setdefault('all', list())
            group.append(item)
        for k, v in grouped_items.items():
            sorted_grouped_items = sorted(v)
            if loc.timed is not None:
                cur_release = min(loc.timed.get_current(), len(sorted_grouped_items))
                if cur_release < 0:
                    continue
                sorted_grouped_items = sorted_grouped_items[loc.timed.first - 1: cur_release + 1]
            grouped_items[k] = sorted_grouped_items
        if len(grouped_items) > 0:
            data.append(interleave_all(list(grouped_items.values())))
    return interleave_all(data)


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
