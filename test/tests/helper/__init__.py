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
from pytest_mock import MockerFixture


class ListdirMock:

    def __init__(self, data: dict[str, list[str]]):
        self.data = data

    def listdir(self,  input_: str):
        if input_ in self.data:
            return self.data[input_]
        raise FileNotFoundError(f'Location {input_} does not exist')


def mock_listdir(mocker: MockerFixture, data: dict[str, list[str]]):
    mocker.patch('os.listdir', side_effect=ListdirMock(data).listdir)


def get_mock_open(mocker: MockerFixture, files: dict[str, str]):
    def open_mock(filename, *args, **kwargs):
        if filename in files:
            return mocker.mock_open(read_data=files[filename]).return_value
        raise FileNotFoundError('(mock) Unable to open {filename}')
    return mocker.patch('builtins.open', side_effect=open_mock)
