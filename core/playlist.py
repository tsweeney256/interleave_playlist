import os
from os import path

from core.interleave import interleave_all
from persistence.input_ import Location


def get_playlist(locations: list[Location], watched_list: list[str]) -> iter:
    data = []
    for loc in locations:
        data.append(sorted(filter(
            lambda i: (path.basename(i) not in watched_list and _matches_filter(i, loc.filters)),
            map(lambda i: loc.name + '/' + i, os.listdir(loc.name))
        )))

    return interleave_all(data)


def _matches_filter(s: str, filters: list[str]):
    for filter_ in filters:
        if filter_ in s:
            return True
    return False
