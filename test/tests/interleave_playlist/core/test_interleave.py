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

from interleave_playlist.core.interleave import interleave_all, interleave
from tests.interleave_playlist.core.interleave_helper import interleave_testdata, combinations


@pytest.mark.parametrize("groups,expected", interleave_testdata)
def test_interleave(groups, expected):
    a, b = groups
    actual = interleave(a, b)
    assert(actual == expected)


@pytest.mark.parametrize("groups,expected", interleave_testdata)
def test_interleave_all_acts_same_as_interleave_with_two_inputs(groups, expected):
    actual = interleave_all(groups)
    assert(actual == expected)


# We don't care so much about what the actual result of the interleaving here is.
# We only care that the result contains all the elements of the input with nothing added or removed
# and that the items within each group retain their ordering.
# The actual quality of the interleaving is measured outside unit tests.
# There is no absolute correct way of determining how to interleave more than two asymmetric lists
@pytest.mark.parametrize("groups", combinations)
def test_interleave_all(groups: list[list[str]]):
    expected_counts = {}
    for group in groups:
        if group:
            expected_counts[group[0][0]] = len(group)
    actual = interleave_all(groups)
    actual_last_seen = {}
    actual_counts = {}
    for item in actual:
        key = item[0]
        count = actual_counts.get(key, 0)
        actual_counts[key] = count + 1
        if key in actual_last_seen:
            # this will stop working the moment there's 10 or more items in a group
            # use natural comparisons if it comes to that
            assert(actual_last_seen[key] < item)
        actual_last_seen[key] = item
    assert(actual_counts == expected_counts)
