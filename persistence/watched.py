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
import csv
import os
from os import path

from core.playlist import FileGroup, get_playlist
from persistence import input_, settings


def get_watched() -> list[FileGroup]:
    with open(input_.get_watched_file_name(), 'r') as f:
        rows = csv.reader(f)
        watched_list: list[FileGroup] = []
        for row in rows:
            if len(row) == 0:
                continue
            item = row[0]
            if len(row) > 1:
                group = row[1]
            else:
                group = ''
            watched_list.append((item, group))
        return watched_list


def add_watched(add: list[FileGroup]) -> None:
    new_watched_list: list[FileGroup] = _clean_watched_list([])
    for a in add:
        new_watched_list.append((path.basename(a[0]), a[1]))
    _write_new_watched_list(new_watched_list)


def remove_watched(remove: list[FileGroup]) -> None:
    remove_names = [path.basename(i[0]) for i in remove]
    new_watched_list: list[FileGroup] = _clean_watched_list(remove_names)
    _write_new_watched_list(new_watched_list)


def _get_temp_file_name() -> str:
    return input_.get_watched_file_name() + '.tmp'


def _get_basename_playlist() -> list[FileGroup]:
    return list(map(lambda i: (path.basename(i[0]), i[1]),
                    get_playlist(input_.get_locations(), [])))


def _clean_watched_list(remove_names: list[str]) -> list[FileGroup]:
    full_playlist = _get_basename_playlist()
    watched_list = get_watched()
    new_watched_list: list[FileGroup] = []
    max_watched_remembered = settings.get_max_watched_remembered()
    watched_remembered = 0
    for row in reversed(watched_list):
        new_watched_list_len = len(new_watched_list)
        if row[0] not in remove_names:
            for item in full_playlist:
                if row[0].strip() == item[0].strip():
                    new_watched_list.append(row)
                    break
            if (new_watched_list_len == len(new_watched_list)
                    and watched_remembered < max_watched_remembered):
                watched_remembered += 1
                new_watched_list.append(row)
    new_watched_list.reverse()
    return new_watched_list


def _write_new_watched_list(new_watched_list: list[FileGroup]):
    with open(_get_temp_file_name(), 'w') as tmp:
        writer = csv.writer(tmp, quoting=csv.QUOTE_ALL)
        writer.writerows(new_watched_list)
    os.replace(_get_temp_file_name(), input_.get_watched_file_name())
