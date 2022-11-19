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
from _pytest.mark import param

from interleave_playlist.core.interleave import interleave_all, interleave, interleave_weighted
from tests.interleave_playlist.core.interleave_helper import interleave_testdata, combinations


@pytest.mark.parametrize("groups,expected", interleave_testdata)
def test_interleave(groups: list[list[str]], expected: list[list[str]]) -> None:
    a, b = groups
    actual = interleave(a, b)
    assert actual == expected


@pytest.mark.parametrize("groups,expected", interleave_testdata)
def test_interleave_all_acts_same_as_interleave_with_two_inputs(
        groups: list[list[str]], expected: list[list[str]]) -> None:
    actual = interleave_all(groups)
    assert actual == expected


# We don't care so much about what the actual result of the interleaving here is.
# We only care that the result contains all the elements of the input with nothing added or removed
# and that the items within each group retain their ordering.
# The actual quality of the interleaving is measured outside unit tests.
# There is no absolute correct way of determining how to interleave more than two asymmetric lists
@pytest.mark.parametrize("groups", combinations)
def test_interleave_all(groups: list[list[str]]) -> None:
    expected_counts = {}
    for group in groups:
        if group:
            expected_counts[group[0][0]] = len(group)
    actual = interleave_all(groups)
    actual_last_seen: dict[str, str] = {}
    actual_counts: dict[str, int] = {}
    for item in actual:
        key = item[0]
        count = actual_counts.get(key, 0)
        actual_counts[key] = count + 1
        if key in actual_last_seen:
            # this will stop working the moment there's 10 or more items in a group
            # use natural comparisons if it comes to that
            assert actual_last_seen[key] < item
        actual_last_seen[key] = item
    assert actual_counts == expected_counts


@pytest.mark.parametrize(
    "groups,expected",
    [
        param([],
              "",
              id="interleave_weighted_with_zero_groups_of_none"),
        param([("", 1)],
              "",
              id="interleave_weighted_with_one_group_of_none"),
        param([("a", 1)],
              "a",
              id="interleave_weighted_with_one_group_of_one"),
        param([("aaaaa", 1)],
              "aaaaa",
              id="interleave_weighted_with_one_group_of_many"),
        param([("", 1), ("", 1)],
              "",
              id="interleave_weighted_with_equal_weights_of_two_groups_of_none"),
        param([("", 1), ("", 2)],
              "",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_none"),
        param([("a", 1), ("b", 1)],
              "ab",
              id="interleave_weighted_with_equal_weights_of_two_groups_of_one"),
        param([("a", 2), ("b", 1)],
              "ab",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_one"),
        param([("a", 1), ("b", 2)],
              "ba",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_one_sorting_by_weight"),
        param([("aaaaa", 1), ("bbbbb", 1)],
              "ababababab",
              id="interleave_weighted_with_equal_weights_of_two_groups_of_many_with_equal_sizes"),
        param([("aaaaa", 1), ("bb", 1)],
              "ababaaa",
              id="interleave_weighted_with_equal_weights_of_two_groups_of_many_with_unequal_sizes"),
        param([("aaaaa", 1), ("bbbbb", 2)],
              "bbabbabaaa",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_many_with_equal_sizes"),
        param([("aaaaaaaaaa", 1), ("bbbbbbbbbb", 2)],
              "bbabbabbabbabbaaaaaa",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_many_with_equal_sizes_and_avoiding_rounding_errors"),  # noqa
        param([("aaaaa", 1), ("bbb", 2)],
              "bbabaaaa",
              id="interleave_weighted_with_unequal_weights_of_two_groups_of_many_with_unequal_sizes"),  # noqa
        param([("", 1), ("", 1), ("", 1)],
              "",
              id="interleave_weighted_with_equal_weights_of_three_groups_of_none"),
        param([("", 1), ("", 2), ("", 3)],
              "",
              id="interleave_weighted_with_unequal_weights_of_three_groups_of_none"),
        param([("a", 1), ("b", 1), ("c", 1)],
              "abc",
              id="interleave_weighted_with_equal_weights_of_three_groups_of_one"),
        param([("a", 1), ("b", 2), ("c", 3)],
              "cba",
              id="interleave_weighted_with_unequal_weights_of_three_groups_of_one"),
        param([("aaa", 1), ("bbb", 1), ("ccc", 1)],
              "abcabcabc",
              id="interleave_weighted_with_equal_weights_of_three_groups_of_many_with_equal_sizes"),
        param([("aaaa", 1), ("bb", 1), ("c", 1)],
              "abcabaa",
              id="interleave_weighted_with_equal_weights_of_three_groups_of_many_with_unequal_sizes"),  # noqa
        param([("aaa", 1), ("bbb", 2), ("ccc", 3)],
              "cbccbabaa",
              id="interleave_weighted_with_unequal_weights_of_three_groups_of_many_with_equal_sizes"),  # noqa
        param([("a", 1), ("bbb", 2), ("ccccc", 3)],
              "cbccbacbc",
              id="interleave_weighted_with_unequal_weights_of_three_groups_of_many_with_unequal_sizes"),  # noqa
        param([("aaa", 0)],
              "aaa",
              id="interleave_weighted_with_zer)weight_of_one_group"),
        param([("aaa", 0), ("bbb", 0)],
              "aaabbb",
              id="interleave_weighted_with_0 weight_of_two_groups"),
        param([("aaa", 0), ("bbb", 0), ("ccc", 0)],
              "aaabbbccc",
              id="interleave_weighted_with_zero_weight_of_three_group"),
        param([("aaa", 0), ("bbb", 1)],
              "bbbaaa",
              id="interleave_weighted_with_two_groups_of_zero_weight_and_non-zero_weight"),
        param([("aaa", 0), ("bbb", 1), ("ccc", 2)],
              "ccbcbbaaa",
              id="interleave_weighted_with_three_groups_of_zero_weight_and_non-zero_weight"),
    ]
)
def test_interleave_weighted(groups: list[tuple[str, int]], expected: str) -> None:
    groups_transformed: list[tuple[list[str], int]] = [
        ([c for c in g[0]], g[1]) for g in groups
    ]
    actual = interleave_weighted(groups_transformed)
    expected_transformed: list[str] = [c for c in expected]
    assert actual == expected_transformed
