import re
from os import path, listdir

from core.interleave import interleave_all
from persistence.input_ import Location


def get_playlist(locations: list[Location], watched_list: list[str]) -> iter:
    data = []
    for loc in locations:
        if loc.regex is not None:
            regex = re.compile(loc.regex)
        else:
            regex = re.compile('')
        items = filter(
            lambda i: (path.basename(i) not in watched_list
                       and _matches_whitelist(i, loc.whitelist)
                       and regex.match(i)),
            map(lambda i: loc.name + '/' + i, listdir(loc.name)))
        grouped_items = {}
        for item in items:
            match = regex.match(item)
            match_dict = match.groupdict()
            if 'group' in match_dict:
                group = grouped_items.setdefault(path.basename(match.group('group')), list())
            else:
                group = grouped_items.setdefault('all', list())
            group.append(item)
        for k, v in grouped_items.items():
            grouped_items[k] = sorted(v)
        data.append(interleave_all(list(grouped_items.values())))
    return interleave_all(data)


def _matches_whitelist(s: str, whitelist: list[str]):
    if whitelist is None:
        return True
    for white in whitelist:
        if white in s:
            return True
    return False
