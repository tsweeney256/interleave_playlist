#    Interleave Playlist
#    Copyright (C) 2021-2024 Thomas Sweeney
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
from dataclasses import dataclass, field
from typing import TypeVar, Iterator, cast, Generic

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
    sorted_groups = sorted(groups, key=lambda group: len(group))
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


@dataclass(order=True)
class _Weighted(Generic[T]):
    group: list[T] = field(compare=False)
    weight: int = field(compare=True)
    iter: Iterator[T] = cast(Iterator[T], field(default=None, compare=False))

    def __post_init__(self) -> None:
        self.iter = iter(self.group)


def _weighted_weave(larger: _Weighted[T], smaller: _Weighted[T]) -> list[T]:
    result = []
    total_weight = larger.weight + smaller.weight
    larger_weight_share = larger.weight / total_weight
    smaller_weight_share = smaller.weight / total_weight

    def append(a: Iterator, b: Iterator) -> bool:
        try:
            result.append(next(a))
            return True
        except StopIteration:
            result.extend(b)
            return False

    i = 1
    continue_processing = True
    while continue_processing:
        if i % (larger_weight_share/smaller_weight_share + 1) >= 1:
            continue_processing = append(larger.iter, smaller.iter)
        else:
            continue_processing = append(smaller.iter, larger.iter)
        i += 1
    return result


def interleave_weighted(groups: list[tuple[list[T], int]]) -> list[T]:
    weights: list[_Weighted[T]] = [_Weighted(*g) for g in groups if g[1] != 0]
    zero_weight_groups: list[list[T]] = [g[0] for g in groups if g[1] == 0]
    weights.sort(reverse=True)

    result = []
    while len(weights) > 1:
        smaller: _Weighted[T] = weights.pop()
        larger: _Weighted[T] = weights.pop()
        new_group = _weighted_weave(larger, smaller)
        weights.append(_Weighted(new_group, larger.weight + smaller.weight))

    if weights:
        result.extend(weights.pop().group)
    for g in zero_weight_groups:
        result.extend(g)

    return result
