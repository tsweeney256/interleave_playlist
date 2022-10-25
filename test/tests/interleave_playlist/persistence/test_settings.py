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
from contextlib import nullcontext as does_not_raise

import pytest

from interleave_playlist import CriticalUserError
from interleave_playlist.persistence import settings
from tests.helper import get_mock_open, get_mock_os_path_exists

ORIGINAL_SETTINGS_FILE = settings._SETTINGS_FILE
SETTINGS_FILENAME = 'settings.yml'
EMPTY_SETTINGS_MOCK = {settings._SETTINGS_FILE: ''}
DEFAULT_SETTINGS_CONTENT = '''font-size: 12
play-command: mpv
dark-mode: false
max-watched-remembered: 100
exclude-directories: true
'''
DEFAULT_SETTINGS_MOCK = {settings._SETTINGS_FILE: DEFAULT_SETTINGS_CONTENT}
MODIFIED_SETTINGS_MOCK = {settings._SETTINGS_FILE: '''font-size: 13
play-command: vlc
dark-mode: true
max-watched-remembered: 10
exclude-directories: false
'''}
INVALID_SETTINGS_MOCK = {settings._SETTINGS_FILE: '''font-size: thirteen
play-command: 24
dark-mode: maybe
max-watched-remembered: ten
exclude-directories: maybe
'''}
NEEDS_CONVERSION_SETTINGS_MOCK = {settings._SETTINGS_FILE: '''font-size: '13'
play-command: true
dark-mode: 'FaLsE'
max-watched-remembered: '10'
exclude-directories: 'TrUe'
'''}


@pytest.fixture(autouse=True)
def before_each():
    settings._CACHED_FILE = {}
    settings._SETTINGS_FILE = ORIGINAL_SETTINGS_FILE


@pytest.mark.parametrize(
    'open_mock_data,option,expected',
    [
        (EMPTY_SETTINGS_MOCK, settings.get_font_size, 12),
        (EMPTY_SETTINGS_MOCK, settings.get_play_command, 'mpv'),
        (EMPTY_SETTINGS_MOCK, settings.get_dark_mode, False),
        (EMPTY_SETTINGS_MOCK, settings.get_max_watched_remembered, 100),
        (EMPTY_SETTINGS_MOCK, settings.get_exclude_directories, True),

        (DEFAULT_SETTINGS_MOCK, settings.get_font_size, 12),
        (DEFAULT_SETTINGS_MOCK, settings.get_play_command, 'mpv'),
        (DEFAULT_SETTINGS_MOCK, settings.get_dark_mode, False),
        (DEFAULT_SETTINGS_MOCK, settings.get_max_watched_remembered, 100),
        (DEFAULT_SETTINGS_MOCK, settings.get_exclude_directories, True),

        (MODIFIED_SETTINGS_MOCK, settings.get_font_size, 13),
        (MODIFIED_SETTINGS_MOCK, settings.get_play_command, 'vlc'),
        (MODIFIED_SETTINGS_MOCK, settings.get_dark_mode, True),
        (MODIFIED_SETTINGS_MOCK, settings.get_max_watched_remembered, 10),
        (MODIFIED_SETTINGS_MOCK, settings.get_exclude_directories, False),

        (NEEDS_CONVERSION_SETTINGS_MOCK, settings.get_font_size, 13),
        (NEEDS_CONVERSION_SETTINGS_MOCK, settings.get_play_command, 'True'),
        (NEEDS_CONVERSION_SETTINGS_MOCK, settings.get_dark_mode, False),
        (NEEDS_CONVERSION_SETTINGS_MOCK, settings.get_max_watched_remembered, 10),
        (NEEDS_CONVERSION_SETTINGS_MOCK, settings.get_exclude_directories, True),
    ])
def test_get_setting_options(mocker, open_mock_data, option, expected):
    get_mock_open(mocker, open_mock_data)
    assert option() == expected


@pytest.mark.parametrize(
    'open_mock_data,option,expectation',
    [
        (INVALID_SETTINGS_MOCK, settings.get_font_size,
         pytest.raises(settings.InvalidSettingsYmlException)),
        (INVALID_SETTINGS_MOCK, settings.get_play_command,
         does_not_raise()),
        (INVALID_SETTINGS_MOCK, settings.get_dark_mode,
         pytest.raises(settings.InvalidSettingsYmlException)),
        (INVALID_SETTINGS_MOCK, settings.get_max_watched_remembered,
         pytest.raises(settings.InvalidSettingsYmlException)),
        (INVALID_SETTINGS_MOCK, settings.get_exclude_directories,
         pytest.raises(settings.InvalidSettingsYmlException)),
        ({settings._SETTINGS_FILE: 'exclude-directories: 13'}, settings.get_exclude_directories,
         pytest.raises(settings.InvalidSettingsYmlException))
    ]
)
def test_invalid_settings_files_raise(mocker, open_mock_data, option, expectation):
    get_mock_open(mocker, open_mock_data)
    with expectation:
        option()


@pytest.mark.parametrize(
    'open_mock_data,expectation',
    [
        (EMPTY_SETTINGS_MOCK, does_not_raise()),
        (DEFAULT_SETTINGS_MOCK, does_not_raise()),
        (INVALID_SETTINGS_MOCK, pytest.raises(CriticalUserError))
    ])
def test_validate_settings_file(mocker, open_mock_data, expectation):
    get_mock_open(mocker, open_mock_data)
    with expectation:
        settings.validate_settings_file()


def test_get_font_size_with_different_value_after_cached_returning_old_value(mocker):
    get_mock_open(mocker, DEFAULT_SETTINGS_MOCK)
    assert settings.get_font_size() == 12
    get_mock_open(mocker, MODIFIED_SETTINGS_MOCK)
    assert settings.get_font_size() == 12


def test_create_settings_file_with_not_already_existing(tmp_path):
    settings._SETTINGS_FILE = tmp_path / 'foo' / SETTINGS_FILENAME

    settings.create_settings_file()
    assert os.path.exists(settings._SETTINGS_FILE)
    with open(settings._SETTINGS_FILE, 'r') as f:
        assert f.read() == DEFAULT_SETTINGS_CONTENT


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


def test_create_settings_file_with_directory_already_existing_but_not_file(mocker, tmp_path):
    settings._SETTINGS_FILE = tmp_path / 'foo' / SETTINGS_FILENAME
    get_mock_os_path_exists(mocker, {
        settings._SETTINGS_FILE: False,
        settings._SETTINGS_FILE.parent: True
    })
    os.mkdir(settings._SETTINGS_FILE.parent)
    mkdir_mock = mocker.patch('os.mkdir')

    settings.create_settings_file()
    mkdir_mock.assert_not_called()
    with open(settings._SETTINGS_FILE, 'r') as f:
        assert f.read() == DEFAULT_SETTINGS_CONTENT
