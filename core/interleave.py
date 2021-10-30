import sys
from math import nan, isnan, floor

import numpy as np
from sortedcontainers import SortedList

_MARGIN = 10e-6


def _divide(a, b) -> float:
    b = b if b != 0 else nan
    return a / b


def _get_every(larger_len: int, smaller_len: int) -> float:
    ratio: float = _divide(larger_len, smaller_len) + 1
    return ratio if not isnan(ratio) else larger_len


# Written in SIMD style just for fun
def interleave(a: list[str], b: list[str]) -> list[str]:
    smaller, larger = sorted([a, b], key=lambda ab: len(ab))
    arr = np.asarray(smaller + larger)
    every: float = _get_every(len(larger), len(smaller))
    total_len = len(a) + len(b)
    i = np.array(range(total_len))
    use_smaller = 1 > (i + floor(every) + _MARGIN) % every
    smaller_idx = np.minimum(len(smaller), ((i + floor(every) - 1 + _MARGIN) / every).astype(int))
    larger_idx = i - smaller_idx + len(smaller)
    idx = np.where(use_smaller, smaller_idx, larger_idx)
    return np.take(arr, idx).tolist()


# Sort by minimum group size difference
def interleave_all(groups: list[list[str]]) -> list[str]:
    sorted_groups = SortedList(groups, key=lambda l: len(l))
    while len(sorted_groups) > 1:
        min_diff: int = sys.maxsize
        min_i: int = -1
        for i in range(len(sorted_groups) - 1):
            diff: int = abs(len(sorted_groups[i]) - len(sorted_groups[i+1]))
            if min_diff > diff:
                min_diff = diff
                min_i = i
        a: list[str] = sorted_groups.pop(min_i)  # smaller or equal
        b: list[str] = sorted_groups.pop(min_i)
        i = 0
        while i < len(sorted_groups):  # interleave smaller groups to reduce size diff
            if abs(len(sorted_groups[i]) + len(a) - len(b)) <= abs(len(a) - len(b)):
                a = interleave(a, sorted_groups.pop(i))
            else:
                i += 1
        sorted_groups.add(interleave(a, b))
    return sorted_groups[0]
