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
import pytest

from interleave_playlist.persistence import settings
from tests.helper import get_mock_open, get_mock_os_path_exists

EMPTY_SETTINGS_MOCK = {settings._SETTINGS_FILE: ''}
DEFAULT_SETTINGS_MOCK = {settings._SETTINGS_FILE: '''
'font-size': 12
'play-command': 'mpv'
'dark-mode': False
'max-watched-remembered': 100
'exclude-directories': True
'''}
MODIFIED_SETTINGS_MOCK = {settings._SETTINGS_FILE: '''
'font-size': 13
'play-command': 'vlc'
'dark-mode': True
'max-watched-remembered': 10
'exclude-directories': False
'''}


@pytest.fixture(autouse=True)
def before_each():
    settings._CACHED_FILE = {}


def test_get_font_size_with_empty_settings_file(mocker):
    get_mock_open(mocker, EMPTY_SETTINGS_MOCK)
    assert settings.get_font_size() == 12


def test_get_play_command_with_empty_settings_file(mocker):
    get_mock_open(mocker, EMPTY_SETTINGS_MOCK)
    assert settings.get_play_command() == 'mpv'


def test_get_dark_mode_with_empty_settings_file(mocker):
    get_mock_open(mocker, EMPTY_SETTINGS_MOCK)
    assert settings.get_dark_mode() is False


def test_get_get_max_watched_remembered_with_empty_settings_file(mocker):
    get_mock_open(mocker, EMPTY_SETTINGS_MOCK)
    assert settings.get_max_watched_remembered() == 100


def test_get_exclude_directories_with_empty_settings_file(mocker):
    get_mock_open(mocker, EMPTY_SETTINGS_MOCK)
    assert settings.get_exclude_directories() is True


def test_get_font_size_with_default_settings_file(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_font_size() == 12


def test_get_play_command_with_default_settings_file(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_play_command() == 'mpv'


def test_get_dark_mode_with_default_settings_file(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_dark_mode() is False


def test_get_get_max_watched_remembered_with_default_settings_file(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_max_watched_remembered() == 100


def test_get_exclude_directories_with_default_settings_file(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_exclude_directories() is True


def test_get_font_size_with_modified_settings_file(mocker):
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_font_size() == 13


def test_get_play_command_with_modified_settings_file(mocker):
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_play_command() == 'vlc'


def test_get_dark_mode_with_modified_settings_file(mocker):
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_dark_mode() is True


def test_get_get_max_watched_remembered_with_modified_settings_file(mocker):
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_max_watched_remembered() == 10


def test_get_exclude_directories_with_modified_settings_file(mocker):
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_exclude_directories() is False


def test_get_font_size_with_different_value_after_cached_returning_old_value(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_font_size() == 12
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_font_size() == 12


def test_create_settings_file_with_not_already_existing(mocker):
    get_mock_os_path_exists(mocker, {
        settings._SETTINGS_FILE: False,
        settings._SETTINGS_FILE.parent: False
    })
    mkdir_mock = mocker.patch('os.mkdir')
    open_mock = get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)

    settings.create_settings_file()
    mkdir_mock.assert_called_once_with(settings._SETTINGS_FILE.parent)
    open_mock.assert_called_once_with(settings._SETTINGS_FILE, 'w')


def test_create_settings_file_with_already_existing(mocker):
    get_mock_os_path_exists(mocker, {
        settings._SETTINGS_FILE: True,
        settings._SETTINGS_FILE.parent: True
    })
    mkdir_mock = mocker.patch('os.mkdir')
    open_mock = get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)

    settings.create_settings_file()
    mkdir_mock.assert_not_called()
    open_mock.assert_not_called()


def test_create_settings_file_with_directory_already_existing_but_not_file(mocker):
    get_mock_os_path_exists(mocker, {
        settings._SETTINGS_FILE: False,
        settings._SETTINGS_FILE.parent: True
    })
    mkdir_mock = mocker.patch('os.mkdir')
    open_mock = get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)

    settings.create_settings_file()
    mkdir_mock.assert_not_called()
    open_mock.assert_called_once_with(settings._SETTINGS_FILE, 'w')
