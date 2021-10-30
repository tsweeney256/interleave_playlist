import sys
from math import nan, isnan, floor

from sortedcontainers import SortedList

_MARGIN = 10e-6


def _divide(a, b) -> float:
    b = b if b != 0 else nan
    return a / b


def _get_every(larger_len: int, smaller_len: int) -> float:
    ratio: float = _divide(larger_len, smaller_len) + 1
    return ratio if not isnan(ratio) else larger_len


# Written in SIMD style just for fun. No SIMD actually used
def interleave(a: list[str], b: list[str]) -> list[str]:
    smaller, larger = sorted([a, b], key=lambda ab: len(ab))
    every: float = _get_every(len(larger), len(smaller))
    total_len: int = len(larger) + len(smaller)
    result: list[str] = [""] * total_len
    for i in range(total_len):
        use_smaller: bool = 1 > (i + floor(every) + _MARGIN) % every
        smaller_idx: int = min(len(smaller), int((i + floor(every) - 1 + _MARGIN) / every))
        larger_idx: int = i - smaller_idx
        arr: list[str] = smaller if use_smaller else larger
        idx: int = smaller_idx if use_smaller else larger_idx
        result[i] = arr[idx]
    return result


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
