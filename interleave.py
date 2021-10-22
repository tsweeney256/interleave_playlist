from math import nan, isnan

groups = [
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

# groups = [
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

# groups = [
#     [
#         "a1",
#         "a2"
#     ],
#     [
#         "b1",
#         "b2"
#     ]
# ]

MARGIN = 10e-6


#  wtf I hate python now
def _divide(a, b) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        return nan


def _get_every(larger_len: int, smaller_len: int) -> int:
    ratio = _divide(larger_len, smaller_len + 1) + 1
    return ratio if not isnan(ratio) else larger_len


def interleave(a: list[str], b: list[str]) -> list[str]:
    ab = sorted([a, b], key=lambda arr: len(arr), reverse=True)
    larger, smaller = ab
    every = _get_every(len(larger), len(smaller))
    last_small_idx = int(every * len(smaller))
    total_len = len(larger) + len(smaller)
    result = [""] * total_len
    for i in range(total_len):
        which = last_small_idx >= i and 1 > (i + 1 + MARGIN) % every and len(smaller) != 0
        smaller_idx = min(len(smaller), int(i / (every)))
        larger_idx = i - smaller_idx
        result[i] = ab[which][[larger_idx, smaller_idx][which]]
    return result


def interleave_all(groups: list[list[str]]) -> list[str]:
    groups.sort(key=lambda f: len(f))
    result = []
    for group in groups:
        result = interleave(result, group)
    return result


def main():
    for item in interleave_all(groups):
        print(item)


if __name__ == '__main__':
    main()
