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
from datetime import datetime, timedelta

import pytest
from crontab import CronTab
from freezegun import freeze_time

from interleave_playlist.core import PlaylistEntry, playlist
from interleave_playlist.core.playlist import get_playlist
from interleave_playlist.persistence import Location, Group, settings, Timed
from tests.helper import mock_listdir, get_mock_open, get_mock_isfile

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S'
NEW_YEAR_2000 = datetime.strptime('2000-01-01T00:00:00', ISO_FORMAT)
DEFAULT_SETTINGS_CONTENT = 'dummy: text'
DEFAULT_SETTINGS_MOCK = {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT}

A_DIR_PATH = pathlib.Path('/dir/A')
A_DIR = str(A_DIR_PATH)
B_DIR_PATH = pathlib.Path('/dir/B')
B_DIR = str(B_DIR_PATH)


@pytest.fixture(autouse=True)
def before_each():
    settings._CACHED_FILE = {}
    playlist._FILE_CACHE = {}


def test_get_playlist_with_no_locations():
    actual = get_playlist([], [])
    expected = []
    assert actual == expected


def test_get_playlist_with_one_location_empty(mocker):
    mock_listdir(mocker, {A_DIR: []})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_one_location_one_file(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group)]
    assert actual == expected


def test_get_playlist_with_one_location_many_files(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_no_files_with_group_regex(mocker):
    mock_listdir(mocker, {A_DIR: []})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_with_regex_no_matches(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mp4', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_with_group_regex_no_matches(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mp4', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_with_files_one_regex_match(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='.+\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group)]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_one_regex_group(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mp4']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group, regex='(?P<group>.+)\\.mkv')
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, Group('foo'))]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_location_many_regex_groups(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'bar 1.mp4', 'bar 1.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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


def test_get_playlist_with_many_locations_many_regex_group_files_each_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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


def test_get_playlist_with_many_locations_many_regex_groups_each_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
        B_DIR: ['cat 1.mkv', 'cat 2.mkv', 'dog 1.mkv', 'dog 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo')
    bar_group = Group('bar')
    cat_group = Group('cat')
    dog_group = Group('dog')
    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 1.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 1.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 2.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 2.mkv'), bl, dog_group),
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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    foo_g = Group('foo', priority=1)
    bar_g = Group('bar', priority=2)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_same_priority_group_subset_overrides(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    foo_g = Group('fo', priority=1)
    bar_g = Group('ba', priority=2)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_same_priority_group_subset_case_insensitive_overrides(mocker):  # noqa: E501
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    foo_g = Group('fO', priority=1)
    bar_g = Group('Ba', priority=2)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_g, bar_g])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_g),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_g),
    ]
    assert actual == expected


def test_get_playlist_with_one_location_many_regex_groups_one_with_priority_one_with_no_priority(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

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


def test_get_playlist_with_search_empty_string_no_op(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_no_entries_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: [],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='bar 1.mkv')
    expected = []
    assert actual == expected


def test_get_playlist_with_search_filter_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='bar 1.mkv')
    expected = []
    assert actual == expected


def test_get_playlist_with_search_filter_matching_exact(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='foo 1.mkv')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_matching_subset(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='1.mkv')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_matching_subset_case_insensitive(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='FoO 1.mKv')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_with_many_locations_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[], search_filter='1')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bg),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar 10.mkv'), bl, bg),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_with_many_groups_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    foo_group = Group('foo')
    bar_group = Group('bar')
    actual = get_playlist([al], watched_list=[], search_filter='1')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_with_many_locations_and_groups_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
        B_DIR: ['cat 1.mkv', 'cat 2.mkv', 'cat 10.mkv', 'dog 1.mkv', 'dog 2.mkv', 'dog 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    foo_group = Group('foo')
    bar_group = Group('bar')
    cat_group = Group('cat')
    dog_group = Group('dog')
    actual = get_playlist([al, bl], watched_list=[], search_filter='1')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 1.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 1.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 10.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 10.mkv'), bl, dog_group),
    ]
    assert actual == expected


def test_get_playlist_with_search_filter_with_many_groups_different_priorities_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
        B_DIR: ['cat 1.mkv', 'cat 2.mkv', 'cat 10.mkv', 'dog 1.mkv', 'dog 2.mkv', 'dog 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo', priority=1)
    bar_group = Group('bar')
    cat_group = Group('cat')
    dog_group = Group('dog', priority=1)
    ag = Group(A_DIR)
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_group])
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv', groups=[dog_group])
    actual = get_playlist([al, bl], watched_list=[], search_filter='1')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 1.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 10.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 1.mkv'), bl, cat_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 10.mkv'), bl, cat_group),
    ]
    assert actual == expected


def test_get_playlist_with_search_ignoring_directory(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter=A_DIR)
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_no_entries_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: [],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['3'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_matching_exact(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['foo 1.mkv'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_matching_subset(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_matching_subset_case_insensitive(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['FoO 1.MkV'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_group_whitelist_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    foo_group = Group('foo', whitelist=['1'])
    al = Location(A_DIR, ag, groups=[foo_group], regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_with_many_locations_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv'],
        B_DIR: ['bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag)
    bg = Group(B_DIR, whitelist=['1'])
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar 1.mkv'), bl, bg),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, ag),
        PlaylistEntry(str(B_DIR_PATH / 'bar 10.mkv'), bl, bg),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_with_many_groups_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    foo_group = Group('foo', whitelist=['1'])
    bar_group = Group('bar', whitelist=['1'])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_with_many_locations_and_groups_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
        B_DIR: ['cat 1.mkv', 'cat 2.mkv', 'cat 10.mkv', 'dog 1.mkv', 'dog 2.mkv', 'dog 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    bg = Group(B_DIR, whitelist=['1'])
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv')
    foo_group = Group('foo', whitelist=['1'])
    bar_group = Group('bar', whitelist=['1'])
    cat_group = Group('cat', whitelist=['1'])
    dog_group = Group('dog', whitelist=['1'])
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 1.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 1.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 10.mkv'), bl, cat_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 10.mkv'), bl, dog_group),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_with_many_groups_different_priorities_interleaved(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 10.mkv', 'bar 1.mkv', 'bar 2.mkv', 'bar 10.mkv'],
        B_DIR: ['cat 1.mkv', 'cat 2.mkv', 'cat 10.mkv', 'dog 1.mkv', 'dog 2.mkv', 'dog 10.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo', priority=1, whitelist=['1'])
    bar_group = Group('bar', whitelist=['1'])
    cat_group = Group('cat', whitelist=['1'])
    dog_group = Group('dog', priority=1, whitelist=['1'])
    ag = Group(A_DIR, whitelist=['1'])
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_group])
    bg = Group(B_DIR, whitelist=['1'])
    bl = Location(B_DIR, bg, regex='(?P<group>[a-z]+).*\\.mkv', groups=[dog_group])
    actual = get_playlist([al, bl], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 1.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 10.mkv'), al, foo_group),
        PlaylistEntry(str(B_DIR_PATH / 'dog 10.mkv'), bl, dog_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 1.mkv'), bl, cat_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 10.mkv'), al, bar_group),
        PlaylistEntry(str(B_DIR_PATH / 'cat 10.mkv'), bl, cat_group),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_ignoring_directory(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=[A_DIR])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_blacklist_no_entries_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: [],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['1'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_blacklist_none_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['3'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag)
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_exact(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo 1.mkv'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_subset(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['1.mkv'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_subset_case_insensitive(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['1.MkV'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_group_blacklist_matching(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    foo_group = Group('foo', blacklist=['2'])
    al = Location(A_DIR, ag, groups=[foo_group], regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_ignoring_directory(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=[A_DIR])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_and_whitelist_working_together(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo'], whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_and_whitelist_contradicting(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['bar'], whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[])
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_and_search_working_together(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='mkv')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_and_search_contradicting(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='foo')
    expected = []
    assert actual == expected


def test_get_playlist_with_blacklist_and_search_working_together(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='bar')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_blacklist_and_search_contradicting(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='bar')
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_and_blacklist_and_search_working_together(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo'], whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='bar')
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_whitelist_and_blacklist_and_search_contradicting_because_whitelist(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['bar'], whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='foo')
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_and_blacklist_and_search_contradicting_because_blacklist(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo'], whitelist=['foo'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='foo')
    expected = []
    assert actual == expected


def test_get_playlist_with_whitelist_and_blacklist_and_search_contradicting_because_search(
        mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['foo'], whitelist=['bar'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[], search_filter='foo')
    expected = []
    assert actual == expected


def test_get_playlist_with_exclude_directories_setting_on(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'foo']})
    get_mock_isfile(mocker, {
        A_DIR_PATH / 'foo.mkv': True,
        A_DIR_PATH / 'foo': False
    })
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group)]
    assert actual == expected


def test_get_playlist_with_not_exclude_directories_setting_off(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'foo']})
    get_mock_isfile(mocker, {
        A_DIR_PATH / 'foo.mkv': True,
        A_DIR_PATH / 'foo': False
    })
    get_mock_open(mocker, {settings._SETTINGS_FILE: 'exclude-directories: false'})
    group = Group(A_DIR)
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo'), location, group)
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_one_watched(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('bar 1.mkv', al.name)])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag)]
    assert actual == expected


def test_get_playlist_with_many_watched(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[
        ('bar 1.mkv', al.name),
        ('foo 1.mkv', al.name)
    ])
    expected = []
    assert actual == expected


def test_get_playlist_with_watched_not_in_list(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('baz 1.mkv', al.name)])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag)
    ]
    assert set(actual) == set(expected)


# This functionality is desirable if going from default group to group override
def test_get_playlist_with_watched_and_different_group(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo')
    ag = Group(A_DIR)
    al = Location(A_DIR, ag, groups=[foo_group])
    actual = get_playlist([al], watched_list=[('foo 1.mkv', al.name)])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, ag)
    ]
    assert set(actual) == set(expected)


# This is desirable if you move your location path around
# Unfortunately this blocks any use case where duplicates across different locations is desired
# The former is going to be /far/ more common than the latter though
def test_get_playlist_with_watched_and_different_location(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv'],
        B_DIR: ['foo 1.mkv']
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    bg = Group(B_DIR)
    bl = Location(B_DIR, bg)
    actual = get_playlist([al, bl], watched_list=[('foo 1.mkv', al.name)])
    expected = []
    assert set(actual) == set(expected)


def test_get_playlist_with_watched_and_case_insensitive(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('bAr 1.MkV', al.name)])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag)]
    assert actual == expected


def test_get_playlist_with_watched_and_searched(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('bar 1.mkv', al.name)], search_filter='bar 1.mkv')
    expected = []
    assert actual == expected


def test_get_playlist_with_watched_and_whitelisted(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, whitelist=['bar 1.mkv'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('bar 1.mkv', al.name)])
    expected = []
    assert actual == expected


def test_get_playlist_with_watched_and_blacklisted(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR, blacklist=['bar 1.mkv'])
    al = Location(A_DIR, ag)
    actual = get_playlist([al], watched_list=[('bar 1.mkv', al.name)])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag)]
    assert actual == expected


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_one_loc_timed_for_future(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 + timedelta(days=1),
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_one_loc_timed(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000 - timedelta(seconds=1))
def test_get_playlist_with_many_loc_timed_right_before(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 3.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_many_loc_timed(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 3.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000 + timedelta(seconds=1))
def test_get_playlist_with_many_loc_timed_right_after(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 3.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_loc_timed_finished(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=5),
        cron=CronTab('0 0 * * *')
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_many_amount(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
        amount=2
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_zero_amount(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
        amount=0
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_negative_amount(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
        amount=-20
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_starting_at_episode(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
        first=2
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_one_loc_timed_start_at_cron_is_true(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 1 * * *'),
        start_at_cron=True
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = []
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_one_loc_timed_start_at_cron_is_false(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 1 * * *'),
        start_at_cron=False
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_many_loc_timed_start_at_cron_is_true(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 1 * * *'),
        start_at_cron=True
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_many_loc_timed_start_at_cron_is_false(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 1 * * *'),
        start_at_cron=False
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_one_loc_timed_start_at_cron_is_true_exact_at_cron(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
        start_at_cron=True
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group)]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_many_loc_timed_start_at_cron_is_true_exact_at_cron(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000 - timedelta(days=1),
        cron=CronTab('0 0 * * *'),
        start_at_cron=True
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_timed_and_watched(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[('foo 1.mkv', group.name)])
    expected = []
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_timed_and_whitelist(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, whitelist=['foo 2.mkv'], timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_timed_and_blacklist(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, blacklist=['foo 1.mkv'], timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), location, group)
    ]
    assert set(actual) == set(expected)


# TODO: fix timed with search filter
@pytest.mark.skip(reason='This is actually bugged and needs to be fixed')
@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_timed_ands_search(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR, timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *'),
    ))
    location = Location(A_DIR, group)
    actual = get_playlist([location], watched_list=[], search_filter='foo 2.mkv')
    expected = []
    assert set(actual) == set(expected)


@freeze_time(NEW_YEAR_2000)
def test_get_playlist_with_timed_group_override(mocker):
    mock_listdir(mocker, {A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'bar 1.mkv', 'bar 2.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})
    group = Group(A_DIR)
    foo_group = Group('foo', timed=Timed(
        start=NEW_YEAR_2000,
        cron=CronTab('0 0 * * *')
    ))
    bar_group = Group('bar')
    location = Location(A_DIR, group, regex='(?P<group>[a-z]+).*\\.mkv', groups=[foo_group])
    actual = get_playlist([location], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), location, foo_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), location, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), location, bar_group)
    ]
    assert set(actual) == set(expected)


def test_get_playlist_with_least_recently_watched_bias_with_groups(mocker):
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'foo 2.mkv', 'foo 3.mkv',
                'bar 1.mkv', 'bar 2.mkv', 'bar 3.mkv',
                'baz 1.mkv', 'baz 2.mkv', 'baz 3.mkv',
                'abc 1.mkv', 'abc 2.mkv'],
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    abc_group = Group('abc')
    foo_group = Group('foo')
    bar_group = Group('bar')
    baz_group = Group('baz')
    al = Location(A_DIR, ag, regex='(?P<group>[a-z]+).*\\.mkv')
    actual = get_playlist([al], watched_list=[
        ('foo 1.mkv', foo_group.name),
        ('bar 1.mkv', bar_group.name),
        ('baz 1.mkv', baz_group.name),
    ])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'abc 1.mkv'), al, abc_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 2.mkv'), al, foo_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 2.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'baz 2.mkv'), al, baz_group),
        PlaylistEntry(str(A_DIR_PATH / 'abc 2.mkv'), al, abc_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 3.mkv'), al, foo_group),
        PlaylistEntry(str(A_DIR_PATH / 'bar 3.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'baz 3.mkv'), al, baz_group),
    ]
    assert actual == expected


def test_get_playlist_with_least_recently_watched_bias_with_locations(mocker):
    foo_dir_path = pathlib.Path('/dir/foo')
    bar_dir_path = pathlib.Path('/dir/bar')
    baz_dir_path = pathlib.Path('/dir/baz')
    abc_dir_path = pathlib.Path('/dir/abc')
    mock_listdir(mocker, {
        str(foo_dir_path): ['foo 1.mkv', 'foo 2.mkv', 'foo 3.mkv', 'foo 4.mkv'],
        str(bar_dir_path): ['bar 1.mkv', 'bar 2.mkv', 'bar 3.mkv', 'bar 4.mkv'],
        str(baz_dir_path): ['baz 1.mkv', 'baz 2.mkv', 'baz 3.mkv', 'baz 4.mkv'],
        str(abc_dir_path): ['abc 1.mkv', 'abc 2.mkv']
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group(str(foo_dir_path))
    bar_group = Group(str(bar_dir_path))
    baz_group = Group(str(baz_dir_path))
    abc_group = Group(str(abc_dir_path))
    foo_location = Location(str(foo_dir_path), foo_group)
    bar_location = Location(str(bar_dir_path), bar_group)
    baz_location = Location(str(baz_dir_path), baz_group)
    abc_location = Location(str(abc_dir_path), abc_group)
    actual = get_playlist(
        [foo_location, bar_location, baz_location, abc_location],
        watched_list=[
            ('foo 1.mkv', foo_group.name),
            ('bar 1.mkv', bar_group.name),
            ('baz 1.mkv', baz_group.name),
            ('foo 2.mkv', foo_group.name),
            ('bar 2.mkv', bar_group.name),
            ('baz 2.mkv', baz_group.name),
        ])
    expected = [
        PlaylistEntry(str(abc_dir_path / 'abc 1.mkv'), abc_location, abc_group),
        PlaylistEntry(str(foo_dir_path / 'foo 3.mkv'), foo_location, foo_group),
        PlaylistEntry(str(bar_dir_path / 'bar 3.mkv'), bar_location, bar_group),
        PlaylistEntry(str(baz_dir_path / 'baz 3.mkv'), baz_location, baz_group),
        PlaylistEntry(str(abc_dir_path / 'abc 2.mkv'), abc_location, abc_group),
        PlaylistEntry(str(foo_dir_path / 'foo 4.mkv'), foo_location, foo_group),
        PlaylistEntry(str(bar_dir_path / 'bar 4.mkv'), bar_location, bar_group),
        PlaylistEntry(str(baz_dir_path / 'baz 4.mkv'), baz_location, baz_group),
    ]
    assert actual == expected


def test_get_playlist_using_cache_with_existing_after_update(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    get_playlist([location], watched_list=[])
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv', 'hooplah.mkv']})
    actual = get_playlist([location], watched_list=[], use_cache=True)
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'bar.mkv'), location, group),
    ]
    assert set(actual) == set(expected)


def test_get_playlist_using_cache_after_refreshing_cache_after_update(mocker):
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv']})
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    group = Group(A_DIR)
    location = Location(A_DIR, group)
    get_playlist([location], watched_list=[])
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv', 'hooplah.mkv']})
    actual = get_playlist([location], watched_list=[], use_cache=False)
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'bar.mkv'), location, group),
        PlaylistEntry(str(A_DIR_PATH / 'hooplah.mkv'), location, group),
    ]
    assert set(actual) == set(expected)
    mock_listdir(mocker, {A_DIR: ['foo.mkv', 'bar.mkv', 'hooplah.mkv', 'wow.mkv']})
    actual = get_playlist([location], watched_list=[], use_cache=True)
    assert set(actual) == set(expected)


def test_get_playlist_with_additional(mocker):
    additional_a_dir_path = pathlib.Path('/a/dir/additional/A')  # sorts first
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv'],
        str(additional_a_dir_path): ['foo 2.mkv']
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    ag = Group(A_DIR)
    al = Location(A_DIR, ag, additional=[str(additional_a_dir_path)])
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, ag),
        PlaylistEntry(str(additional_a_dir_path / 'foo 2.mkv'), al, ag),
    ]
    assert actual == expected


def test_get_playlist_with_additional_with_groups(mocker):
    additional_a_dir_path = pathlib.Path('/a/dir/additional/A')  # sorts first
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
        str(additional_a_dir_path): ['foo 2.mkv', 'bar 2.mkv']
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo', priority=2)
    bar_group = Group('bar', priority=1)
    ag = Group(A_DIR)
    al = Location(
        A_DIR,
        ag,
        additional=[str(additional_a_dir_path)],
        regex='(?P<group>[a-z]+).*\\.mkv',
        groups=[foo_group, bar_group]
    )
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(additional_a_dir_path / 'bar 2.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(additional_a_dir_path / 'foo 2.mkv'), al, foo_group),
    ]
    assert actual == expected


def test_get_playlist_with_additional_with_groups_interleaved(mocker):
    additional_a_dir_path = pathlib.Path('/a/dir/additional/A')  # sorts first
    mock_listdir(mocker, {
        A_DIR: ['foo 1.mkv', 'bar 1.mkv'],
        str(additional_a_dir_path): ['foo 2.mkv', 'bar 2.mkv']
    })
    mocker.patch('os.path.isfile', return_value=True)
    get_mock_open(mocker, {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT})

    foo_group = Group('foo')
    bar_group = Group('bar')
    ag = Group(A_DIR)
    al = Location(
        A_DIR,
        ag,
        additional=[str(additional_a_dir_path)],
        regex='(?P<group>[a-z]+).*\\.mkv',
    )
    actual = get_playlist([al], watched_list=[])
    expected = [
        PlaylistEntry(str(A_DIR_PATH / 'bar 1.mkv'), al, bar_group),
        PlaylistEntry(str(A_DIR_PATH / 'foo 1.mkv'), al, foo_group),
        PlaylistEntry(str(additional_a_dir_path / 'bar 2.mkv'), al, bar_group),
        PlaylistEntry(str(additional_a_dir_path / 'foo 2.mkv'), al, foo_group),
    ]
    assert actual == expected
