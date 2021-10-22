from math import nan, isnan

data = [
    [
        "a1",
        "a2",
        "a3",
        "a4",
        "a5",
    ],
    [
        "b1",
    ],
    [
        "c1",
        "c2",
        "c3",
        "c4",
    ],
    [
        "d1",
        "d2",
        "d3",
    ]
]

# data = [
#     [
#         "a1",
#         "a2"
#     ],
#     [
#         "d1",
#         "d2",
#         "d3",
#         "d4",
#         "d5",
#         "d6",
#         # "d7"
#     ]
# ]

# data = [
#     [
#         "a1",
#         "a2"
#     ],
#     [
#         "b1",
#         "b2"
#     ]
# ]

MARGIN: float = 10e-6


#  wtf I hate python now
def _divide(a, b) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        return nan


def _get_every(larger_len: int, smaller_len: int) -> float:
    ratio: float = _divide(larger_len, smaller_len + 1) + 1
    return ratio if not isnan(ratio) else larger_len


def interleave(a: list[str], b: list[str]) -> list[str]:
    larger, smaller = sorted([a, b], key=lambda ab: len(ab), reverse=True)
    every: float = _get_every(len(larger), len(smaller))
    total_len: int = len(larger) + len(smaller)
    result: list[str] = [""] * total_len
    for i in range(total_len):
        use_smaller: bool = 1 > (i + 1 + MARGIN) % every
        smaller_idx: int = min(len(smaller), int(i / every))
        larger_idx: int = i - smaller_idx
        arr: list[str] = smaller if use_smaller else larger
        idx: int = smaller_idx if use_smaller else larger_idx
        result[i] = arr[idx]
    return result


def interleave_all(groups: list[list[str]]) -> list[str]:
    groups.sort(key=lambda f: len(f))
    result: list[str] = []
    for group in groups:
        result = interleave(result, group)
    return result


def main():
    for item in interleave_all(data):
        print(item)


if __name__ == '__main__':
    main()
