#    Interleave Playlist
#    Copyright (C) 2021-2022 Thomas Sweeney
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

import sys
from typing import TypeVar

T = TypeVar('T')
_MARGIN = 10e-6


def interleave(a: list[T], b: list[T]) -> list[T]:
    smaller, larger = sorted([a, b], key=lambda ab: len(ab))
    if not smaller:
        return larger
    group_count = len(smaller) + 1
    group_size = len(larger) // group_count + 1
    surplus = len(larger) - group_count * (group_size - 1)
    surplus_per_group = surplus / group_count
    result = []
    larger_idx = 0

    def _append_larger() -> None:
        nonlocal larger_idx
        use_surplus = surplus_per_group and (group_idx+1+_MARGIN) % (1/surplus_per_group) < 1
        surplus_offset = 1 if use_surplus else 0
        for i in range(group_size - 1 + surplus_offset):
            result.append(larger[larger_idx])
            larger_idx += 1

    group_idx = 0
    for smaller_idx in range(len(smaller)):
        _append_larger()
        result.append(smaller[smaller_idx])
        group_idx += 1
    _append_larger()
    return result


# Sort by minimum group size difference
def interleave_all(groups: list[list[T]]) -> list[T]:
    groups = [group for group in groups if group]  # just make debugging easier
    sorted_groups = sorted(groups, key=lambda l: len(l))
    while len(sorted_groups) > 1:
        min_diff: int = sys.maxsize
        min_i: int = -1
        for i, (left, right) in enumerate(zip(sorted_groups, sorted_groups[1:])):
            diff: int = abs(len(left) - len(right))
            if min_diff > diff:
                min_diff = diff
                min_i = i
        a: list[T] = sorted_groups.pop(min_i)  # smaller or equal
        b: list[T] = sorted_groups.pop(min_i)
        i = 0
        while i < len(sorted_groups):  # interleave smaller groups to reduce size diff
            if abs(len(sorted_groups[i]) + len(a) - len(b)) <= abs(len(a) - len(b)):
                a = interleave(a, sorted_groups.pop(i))
            else:
                i += 1
        interleaved = interleave(a, b)
        len_before_insert = len(sorted_groups)
        for i, elem in enumerate(sorted_groups):
            if len(elem) > len(interleaved):
                sorted_groups.insert(i, interleaved)
                break
        if len_before_insert == len(sorted_groups):
            sorted_groups.append(interleaved)
    return sorted_groups[0] if len(sorted_groups) > 0 else []
