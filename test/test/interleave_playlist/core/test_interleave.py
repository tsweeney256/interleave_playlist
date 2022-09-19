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

from interleave_playlist.core.interleave import interleave


def transform_testdata_definition(a, b, expected, k) -> tuple[list[str], list[str], list[str]]:
    return pytest.param(["w"] * a, ["U"] * b, [c for c in expected], id=f'{k=} {(a, b, expected)}')


def reverse_testdata_arguments(a, b, expected) -> tuple[int, int, str]:
    r_expected = ["w" if c == "U" else "U" for c in expected]
    return b, a, "".join(r_expected)


t = transform_testdata_definition
r = reverse_testdata_arguments

interleave_testdata_definition = [
    (0, 0, ""),
    (0, 1, "U"),
    (0, 2, "UU"),
    (0, 3, "UUU"),
    (0, 4, "UUUU"),
    (0, 5, "UUUUU"),
    (0, 6, "UUUUUU"),
    (0, 7, "UUUUUUU"),
    (0, 8, "UUUUUUUU"),
    (0, 9, "UUUUUUUUU"),
    (0, 10, "UUUUUUUUUU"),
    (1, 1, "wU"),
    (1, 2, "UwU"),
    (1, 3, "UwUU"),
    (1, 4, "UUwUU"),
    (1, 5, "UUwUUU"),
    (1, 6, "UUUwUUU"),
    (1, 7, "UUUwUUUU"),
    (1, 8, "UUUUwUUUU"),
    (1, 9, "UUUUwUUUUU"),
    (1, 10, "UUUUUwUUUUU"),
    (2, 2, "wUwU"),
    (2, 3, "UwUwU"),
    (2, 4, "UwUwUU"),
    (2, 5, "UwUUwUU"),
    (2, 6, "UUwUUwUU"),
    (2, 7, "UUwUUwUUU"),
    (2, 8, "UUwUUUwUUU"),
    (2, 9, "UUUwUUUwUUU"),
    (2, 10, "UUUwUUUwUUUU"),
    (3, 3, "wUwUwU"),
    (3, 4, "UwUwUwU"),
    (3, 5, "UwUwUwUU"),
    (3, 6, "UwUUwUwUU"),
    (3, 7, "UwUUwUUwUU"),
    (3, 8, "UUwUUwUUwUU"),
    (3, 9, "UUwUUwUUwUUU"),
    (3, 10, "UUwUUUwUUwUUU"),
    (4, 4, "wUwUwUwU"),
    (4, 5, "UwUwUwUwU"),
    (4, 6, "UwUwUwUwUU"),
    (4, 7, "UwUwUUwUwUU"),
    (4, 8, "UwUUwUwUUwUU"),
    (4, 9, "UwUUwUUwUUwUU"),
    (4, 10, "UUwUUwUUwUUwUU"),
    (5, 5, "wUwUwUwUwU"),
    (5, 6, "UwUwUwUwUwU"),
    (5, 7, "UwUwUwUwUwUU"),
    (5, 8, "UwUwUUwUwUwUU"),
    (5, 9, "UwUUwUwUUwUwUU"),
    (5, 10, "UwUUwUUwUwUUwUU"),
    (6, 6, "wUwUwUwUwUwU"),
    (6, 7, "UwUwUwUwUwUwU"),
    (6, 8, "UwUwUwUwUwUwUU"),
    (6, 9, "UwUwUwUUwUwUwUU"),
    (6, 10, "UwUwUUwUwUUwUwUU"),
    (7, 7, "wUwUwUwUwUwUwU"),
    (7, 8, "UwUwUwUwUwUwUwU"),
    (7, 9, "UwUwUwUwUwUwUwUU"),
    (7, 10, "UwUwUwUUwUwUwUwUU"),
    (8, 8, "wUwUwUwUwUwUwUwU"),
    (8, 9, "UwUwUwUwUwUwUwUwU"),
    (8, 10, "UwUwUwUwUwUwUwUwUU"),
    (9, 9, "wUwUwUwUwUwUwUwUwU"),
    (10, 10, "wUwUwUwUwUwUwUwUwUwU"),
]

interleave_testdata = []
i = 0
for d in interleave_testdata_definition:
    interleave_testdata.append(t(*d, i))
    i += 1
    if d[0] != d[1]:
        interleave_testdata.append(t(*r(*d), i))
        i += 1


@pytest.mark.parametrize("a,b,expected", interleave_testdata)
def test_interleave(a, b, expected):
    actual = interleave(a, b)
    assert(actual == expected)
