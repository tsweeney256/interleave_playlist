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
from math import nan, isnan, floor, ceil
from typing import TypeVar

T = TypeVar('T')
_MARGIN = 10e-6


def _divide(a, b) -> float:
    b = b if b != 0 else nan
    return a / b


def _get_every(larger_len: int, smaller_len: int) -> float:
    ratio: float = _divide(larger_len, smaller_len) + 1
    return ratio if not isnan(ratio) else larger_len


# This is not being maintained
# This is actually 5x slower than my "SIMD style for loop" using no SIMD lol
def interleave_simd(a: list[T], b: list[T]) -> list[T]:
    import numpy as np
    smaller, larger = sorted([a, b], key=lambda ab: len(ab))
    if not smaller:
        return larger
    arr = np.asarray(smaller + larger)  # boo >:(
    every: float = _get_every(len(larger), len(smaller))
    total_len = len(a) + len(b)
    i = np.array(range(total_len))
    use_smaller = 1 > (i + floor(every) + _MARGIN) % every
    smaller_idx = np.minimum(len(smaller), ((i + floor(every) - 1 + _MARGIN) / every).astype(int))
    larger_idx = i - smaller_idx + len(smaller)
    idx = np.where(use_smaller, smaller_idx, larger_idx)
    return np.take(arr, idx).tolist()


# Written in SIMD style just for fun. No SIMD actually used
def interleave(a: list[T], b: list[T]) -> list[T]:
    smaller, larger = sorted([a, b], key=lambda ab: len(ab))
    if not smaller:
        return larger
    every: float = _get_every(len(larger), len(smaller))
    total_len: int = len(larger) + len(smaller)
    result: list[T] = [None] * total_len
    for i in range(total_len):
        i_mod = ceil(i + every / 2)  # make smaller start in middle, not first
        use_smaller: bool = 1 > (i_mod + floor(every) + _MARGIN) % every
        smaller_idx: int = int((i_mod + floor(every) - 1 + _MARGIN) / every) - 1
        larger_idx: int = i - smaller_idx
        arr: list[str] = smaller if use_smaller else larger
        idx: int = smaller_idx if use_smaller else larger_idx
        result[i] = arr[idx]
    return result


# Sort by minimum group size difference
def interleave_all(groups: list[list[T]]) -> list[T]:
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
