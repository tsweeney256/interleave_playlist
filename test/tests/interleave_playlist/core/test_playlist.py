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
import pathlib

import pytest

from interleave_playlist.core import PlaylistEntry
from interleave_playlist.core.playlist import get_playlist
from interleave_playlist.persistence import Location, Group, settings
from tests.helper import mock_listdir, get_mock_open

default_settings_content = 'dummy: text'
default_settings_mock = {settings._SETTINGS_FILE: default_settings_content}

A_DIR_PATH = pathlib.Path('/dir/A')
A_DIR = str(A_DIR_PATH)
B_DIR_PATH = pathlib.Path('/dir/B')
B_DIR = str(B_DIR_PATH)


def test_get_playlist_with_no_locations():
    actual = get_playlist([], [])
    expected = []
    assert actual == expected


def test_get_playlist_with_one_location_empty(mocker):
    mock_listdir(mocker, {A_DIR: []})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_one_location_one_file(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group)]
    assert actual == expected


def test_get_playlist_with_one_location_many_files(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'bar.mkv'), location, group),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_no_files(mocker):
    mock_listdir(mocker, {
        A_DIR: [],
        B_DIR: [],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_one_file(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
        B_DIR: ['bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar.mkv'), bl, bg),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_many_files(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv', 'hooplah.mkv'],
        B_DIR: ['bar.mkv', 'something.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'hooplah.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar.mkv'), bl, bg),
        PlaylistEntry(str(B_DIR_PATH / 'something.mkv'), bl, bg),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_duplicate_locations_no_files(mocker):
    mock_listdir(mocker, {
        A_DIR: [],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    aag = Group(A_DIR)
    aal = Location(A_DIR, aag)
    actual = get_playlist([al, aal], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_duplicate_locations_one_file(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    aag = Group(A_DIR)
    aal = Location(A_DIR, aag)
    actual = get_playlist([al, aal], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, ag),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_duplicate_locations_many_files(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv', 'bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    aag = Group(A_DIR)
    aal = Location(A_DIR, aag)
    actual = get_playlist([al, aal], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'bar.mkv'), al, ag),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_no_files_with_regex(mocker):
    mock_listdir(mocker, {A_DIR: []})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_no_files_with_group_regex(mocker):
    mock_listdir(mocker, {A_DIR: []})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_with_regex_no_matches(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mp4', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_with_group_regex_no_matches(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mp4', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_one_regex_match(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group)]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_one_regex_group(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, Group('foo'))]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_many_regex_groups(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'bar 1.mp4', 'bar 1.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), location, Group('bar')),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_many_regex_groups_many_files_each(mocker):
    mock_listdir(mocker, {A_DIR: [
        'foo 1.mkv', 'bar 1.mp4', 'bar 1.mkv', 'bar 2.mkv', 'foo 2.mkv'
    ]})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), location, Group('bar')),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), location, Group('bar')),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_many_regex_groups_many_files_each_interleaved(mocker):
    mock_listdir(mocker, {A_DIR: [
        'foo 1.mkv', 'bar 1.mp4', 'bar 1.mkv', 'bar 2.mkv', 'foo 2.mkv'
    ]})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), location, Group('bar')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), location, Group('bar')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, Group('foo')),
    ]
    assert actual == expected


def test_get_playlist_with_many_locations_with_regex_with_no_matches(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
        B_DIR: ['bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='[A-Z]+.+\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='[A-Z]+.+\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_with_regex_group_with_no_groups(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
        B_DIR: ['bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[A-Z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[A-Z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_one_regex_match_each(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
        B_DIR: ['bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='[a-z]+.*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='[a-z]+.*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(B_DIR_PATH / 'bar.mkv'), bl, Group(B_DIR)),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_one_regex_group_each(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo.mkv'],
        B_DIR: ['bar.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar.mkv'), bl, Group('bar')),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_many_regex_matches_each(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='[a-z]+.*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='[a-z]+.*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group(B_DIR)),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_many_regex_matches_each_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='[a-z]+.*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='[a-z]+.*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group(B_DIR)),
    ]
    assert actual == expected


def test_get_playlist_with_many_locations_many_regex_groups_each(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group('bar')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group('bar')),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_many_locations_many_regex_groups_each_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group('bar')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group('bar')),
    ]
    assert actual == expected


# TODO: actual bug
# These need to be counted as entirely separate groups
@pytest.mark.skip(reason='This found an actual, existing, bug')
def test_get_playlist_with_many_locations_many_regex_groups_each_with_groups_crossing_locations(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 2.mkv'],
        B_DIR: ['bar 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group('foo')),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group('bar')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group('bar')),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_using_regex_other_no_regex_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'foo 0.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group('foo')),
        PlaylistEntry(str(B_DIR_PATH / 'foo 0.mkv'), bl, Group(B_DIR)),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_with_priority(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR, priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR, priority=1)),
    ]
    assert actual == expected


def test_get_playlist_with_many_locations_with_same_priority(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR, priority=1)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR, priority=1)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR, priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR, priority=1)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group(B_DIR, priority=1)),
    ]
    assert actual == expected


def test_get_playlist_with_many_locations_with_one_priority_one_no_priority(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR, priority=1)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR, priority=1)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group(B_DIR, priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR)),
    ]
    assert actual == expected


def test_get_playlist_with_many_locations_different_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=2)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR, priority=1)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, Group(B_DIR, priority=1)),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, Group(B_DIR, priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group(A_DIR, priority=2)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group(A_DIR, priority=2)),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_same_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, Group('bar', priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, Group('foo', priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, Group('bar', priority=1)),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, Group('foo', priority=1)),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_same_priority_group_overrides(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    foo_g = Group('foo', priority=1)
    bar_g = Group('bar', priority=1)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_one_with_priority_one_with_no_priority(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    foo_g = Group('foo')
    bar_g = Group('bar', priority=1)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_different_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    foo_g = Group('foo', priority=2)
    bar_g = Group('bar', priority=1)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


def test_get_playlist_with_many_location_many_regex_groups_same_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    foo_g = Group('foo', priority=1)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR, priority=1)
    bar_g = Group('bar', priority=1)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, bar_g),
    ]
    assert actual == expected


def test_get_playlist_with_many_location_many_regex_groups_one_with_one_without_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR)
    foo_g = Group('foo')
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR, priority=1)
    bar_g = Group('bar', priority=1)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bar_g),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


def test_get_playlist_with_many_location_many_regex_groups_different_priorities(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=2)
    foo_g = Group('foo', priority=2)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR, priority=1)
    bar_g = Group('bar', priority=1)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bar_g),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


def test_get_playlist_with_many_location_many_regex_groups_different_priorities_from_default(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: default_settings_content})

    ag = Group(A_DIR, priority=1)
    foo_g = Group('foo', priority=2)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g])
    bg = Group(B_DIR, priority=2)
    bar_g = Group('bar', priority=1)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv', groups=[bar_g])
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bar_g),
        PlaylistEntry(str(B_DIR_PATH / 'bar 2.mkv'), bl, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
    ]
    assert actual == expected


@pytest.mark.skip
def test_get_playlist_with_search_filter_matching_exact():
    pass


@pytest.mark.skip
def test_get_playlist_with_search_filter_matching_subset():
    pass


@pytest.mark.skip
def test_get_playlist_with_search_filter_matching_subset_case_insensitive():
    pass


@pytest.mark.skip
def test_get_playlist_with_whitelist_exact():
    pass


@pytest.mark.skip
def test_get_playlist_with_whitelist_subset():
    pass


@pytest.mark.skip
def test_get_playlist_with_whitelist_subset_case_insensitive():
    pass


@pytest.mark.skip
def test_get_playlist_with_blacklist_exact():
    pass


@pytest.mark.skip
def test_get_playlist_with_blacklist_subset():
    pass


@pytest.mark.skip
def test_get_playlist_with_blacklist_subset_case_insensitive():
    pass


@pytest.mark.skip
def test_get_playlist_with_exclude_directories_setting_on():
    pass


@pytest.mark.skip
def test_get_playlist_with_not_exclude_directories_setting_off():
    pass


@pytest.mark.skip
def test_get_playlist_with_blacklist_and_whitelist_working_together():
    pass


@pytest.mark.skip
def test_get_playlist_with_blacklist_and_whitelist_contradicting():
    pass


@pytest.mark.skip
def test_get_playlist_with_regex_and_whitelist():
    pass


@pytest.mark.skip
def test_get_playlist_with_regex_and_blacklist():
    pass


@pytest.mark.skip
def test_get_playlist_with_regex_and_whitelist_and_blacklist():
    pass


@pytest.mark.skip
def test_get_playlist_with_one_loc_timed_for_future():
    pass


@pytest.mark.skip
def test_get_playlist_with_one_loc_timed():
    pass


@pytest.mark.skip
def test_get_playlist_with_many_loc_timed():
    pass


@pytest.mark.skip
def test_get_playlist_with_many_amount():
    pass


@pytest.mark.skip
def test_get_playlist_with_starting_at_episode():
    pass


@pytest.mark.skip
def test_get_playlist_with_one_watched():
    pass


@pytest.mark.skip
def test_get_playlist_with_many_watched():
    pass


@pytest.mark.skip
def test_get_playlist_with_watched_not_in_list():
    pass


@pytest.mark.skip
def test_get_playlist_with_timed_and_watched():
    pass


@pytest.mark.skip
def test_get_playlist_with_least_recently_watched_bias():
    pass


@pytest.mark.skip
def test_get_playlist_using_cache_without_existing_yet():
    pass


@pytest.mark.skip
def test_get_playlist_using_cache_with_existing_after_update():
    pass


@pytest.mark.skip
def test_get_playlist_using_cache_after_refreshing_cache_after_update():
    pass


# TODO: add "additional" tests, don't forget sorting paths vs files