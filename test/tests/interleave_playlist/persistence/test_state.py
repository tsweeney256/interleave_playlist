#    Interleave Playlist
#    Copyright (C) 2022-2025 Thomas Sweeney
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
import json
import os
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from interleave_playlist.persistence import state
from tests.helper import get_mock_open

EMPTY_STATE_CONTENT = '{}'
DEFAULT_STATE_CONTENT = '{"last-input-file": ""}'
EXISTING_STATE_CONTENT = '{"last-input-file": "/foo/bar/input.yml"}'
ORIGINAL_STATE_FILE = state._STATE_FILE
EMPTY_STATE_MOCK = {state._STATE_FILE: EMPTY_STATE_CONTENT}
DEFAULT_STATE_MOCK = {state._STATE_FILE: DEFAULT_STATE_CONTENT}
EXISTING_STATE_MOCK = {state._STATE_FILE: EXISTING_STATE_CONTENT}


@pytest.fixture(autouse=True)
def before_each() -> None:
    state._STATE_FILE = ORIGINAL_STATE_FILE
    state._CACHED_STATE = {}


def test_create_state_file_when_file_not_exists_and_folder_not_exists(tmp_path: Path) -> None:
    state._STATE_FILE = tmp_path / 'state' / 'state.json'
    state.create_state_file()
    with open(state._STATE_FILE, 'r') as f:
        assert f.read() == DEFAULT_STATE_CONTENT


def test_create_state_file_when_file_not_exists_and_folder_exists(tmp_path: Path) -> None:
    state._STATE_FILE = tmp_path / 'state' / 'state.json'
    os.mkdir(state._STATE_FILE.parent)
    state.create_state_file()
    with open(state._STATE_FILE, 'r') as f:
        assert f.read() == DEFAULT_STATE_CONTENT


def test_create_state_file_when_file_exists_and_folder_exists(tmp_path: Path) -> None:
    state._STATE_FILE = tmp_path / 'state' / 'state.json'
    os.mkdir(state._STATE_FILE.parent)
    with open(state._STATE_FILE, 'w') as f:
        f.write(EXISTING_STATE_CONTENT)
    state.create_state_file()
    with open(state._STATE_FILE, 'r') as f:
        assert f.read() == EXISTING_STATE_CONTENT


def test_get_last_input_path(mocker: MockerFixture) -> None:
    get_mock_open(mocker, EXISTING_STATE_MOCK)
    assert state.get_last_input_file() == Path('/foo/bar/input.yml')


def test_get_last_input_path_with_empty_state_file(mocker: MockerFixture) -> None:
    get_mock_open(mocker, EMPTY_STATE_MOCK)
    assert state.get_last_input_file() is None


def test_set_last_input_path(tmp_path: Path) -> None:
    state._STATE_FILE = tmp_path / 'state' / 'state.json'
    state.create_state_file()
    expected = '/foo/bar/input.yml'
    state.set_last_input_file(Path(expected))
    with open(state._STATE_FILE, 'r') as f:
        actual = json.load(f)
        assert Path(actual[state._KEYS.LAST_INPUT_FILE]) == Path('/foo/bar/input.yml')
