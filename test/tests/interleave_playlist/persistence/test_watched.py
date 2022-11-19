#    Interleave Playlist
#    Copyright (C) 2022 Thomas Sweeney
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
from pathlib import Path

import pytest
from _pytest.mark import param
from pytest_mock import MockerFixture

from interleave_playlist.core import PlaylistEntry
from interleave_playlist.model import Location, Group
from interleave_playlist.persistence import watched

A_DIR_GROUP = '/A'


@pytest.fixture(autouse=True)
def before_each(mocker: MockerFixture, tmp_path: Path) -> None:
    os.mkdir(tmp_path / 'foo')
    mocker.patch('interleave_playlist.persistence.state.get_last_input_file',
                 return_value=tmp_path / Path("foo/input.yml"))
    mocker.patch('interleave_playlist.persistence.input_.get_locations')
    mocker.patch('interleave_playlist.persistence.settings.get_max_watched_remembered',
                 return_value=999)


def to_watched_file(content: list[tuple[str, str]], path: Path) -> None:
    with open(path, 'w') as f:
        f.writelines([",".join((f'"{cq}"' for cq in c)) + os.linesep for c in content])


def to_playlist_entry(filename: str, group_name: str) -> PlaylistEntry:
    group = Group(name=group_name)
    loc = Location(name=group_name, default_group=group)
    return PlaylistEntry(filename, loc, group)


@pytest.mark.parametrize(
    'content', [
        param(
            None,
            id='get watched with no file',
        ),
        param(
            [],
            id='get watched with zero entries'
        ),
        param(
            [('foo 1.mkv', A_DIR_GROUP)],
            id='get watched with one entry'
        ),
        param(
            [('foo 1.mkv', A_DIR_GROUP),
             ('foo 2.mkv', A_DIR_GROUP)],
            id='get watched with many entries'
        )
    ])
def test_get_watched(content: list[tuple[str, str]], tmp_path: Path) -> None:
    if content is not None:
        to_watched_file(content, tmp_path / Path('foo/input.yml.watched.txt'))
    expected = content if content is not None else []
    assert watched.get_watched() == expected


_zero: list[tuple[str, str]] = []
_one: list[tuple[str, str]] = [('1', 'g')]
_many: list[tuple[str, str]] = [('1', 'g'), ('2', 'g')]


@pytest.mark.parametrize(
    'content,add', [
        param(None, _zero, id='add watched with no file add zero'),
        param(_zero, _zero, id='add watched with zero content add zero'),
        param(_zero, _one, id='add watched with zero content add one'),
        param(_zero, _many, id='add watched with zero content add many'),
        param(_one, _zero, id='add watched with one content add zero'),
        param(_one, _one, id='add watched with one content add one'),
        param(_one, _many, id='add watched with one content add many'),
        param(_many, _zero, id='add watched with many content add zero'),
        param(_many, _one, id='add watched with many content add one'),
        param(_many, _many, id='add watched with many content add many'),
    ])
def test_add_watched(content: list[tuple[str, str]],
                     add: list[tuple[str, str]],
                     tmp_path: Path,
                     mocker: MockerFixture) -> None:
    if content is not None:
        to_watched_file(content, tmp_path / Path('foo/input.yml.watched.txt'))
        content_cpy = content.copy()
    else:
        content_cpy = []
    mocker.patch('interleave_playlist.core.playlist.get_playlist',
                 return_value=[to_playlist_entry(*c) for c in content_cpy])
    add_pl = [to_playlist_entry(*pl) for pl in add]
    content_cpy.extend(add)
    watched.add_watched(add_pl)
    assert watched.get_watched() == content_cpy


@pytest.mark.parametrize(
    'content,remove', [
        param(None, _zero, id='remove watched with no file remove zero'),
        param(_zero, _zero, id='remove watched with zero content remove zero'),
        param(_zero, _one, id='remove watched with zero content remove one'),
        param(_zero, _many, id='remove watched with zero content remove many'),
        param(_one, _zero, id='remove watched with one content remove zero'),
        param(_one, _one, id='remove watched with one content remove one'),
        param(_one, _many, id='remove watched with one content remove many'),
        param(_many, _zero, id='remove watched with many content remove zero'),
        param(_many, _one, id='remove watched with many content remove one'),
        param(_many, _many, id='remove watched with many content remove many'),
        param(_many, [('3', 'f'), ('4', 'f')],
              id='remove watched with many content remove nonexistent'),
        param(_many, [('3', 'f'), ('1', 'g')],
              id='remove watched with many content remove nonexistent and one existing')
    ])
def test_removed_watched(content: list[tuple[str, str]],
                         remove: list[tuple[str, str]],
                         tmp_path: Path,
                         mocker: MockerFixture) -> None:
    if content is not None:
        to_watched_file(content, tmp_path / Path('foo/input.yml.watched.txt'))
        content_cpy = content.copy()
    else:
        content_cpy = []
    mocker.patch('interleave_playlist.core.playlist.get_playlist',
                 return_value=[to_playlist_entry(*c) for c in content_cpy])
    add_pl = [to_playlist_entry(*pl) for pl in remove]
    for r in remove:
        if r in content_cpy:
            content_cpy.remove(r)
    watched.remove_watched(add_pl)
    assert watched.get_watched() == content_cpy
