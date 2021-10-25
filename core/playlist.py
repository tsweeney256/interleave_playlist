import os
from os import path

from core.interleave import interleave_all


def get_playlist(locations: list[str], watched_list: list[str]) -> iter:
    data = []
    for loc in locations:
        data.append(sorted(filter(
            lambda i: (path.basename(i) not in watched_list and ('.mkv' in i or '.mp4' in i)),
            map(lambda i: loc + '/' + i, os.listdir(loc))
        )))

    return interleave_all(data)
