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
                       and not _matches_blacklist(i, loc.blacklist)
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
            sorted_grouped_items = sorted(v)
            if loc.timed is not None:
                cur_release = loc.timed.get_current()
                if cur_release < 0:
                    continue
                sorted_grouped_items = sorted_grouped_items[loc.timed.first - 1: cur_release]
            grouped_items[k] = sorted_grouped_items
        data.append(interleave_all(list(grouped_items.values())))
    return interleave_all(data)


def _matches_whitelist(s: str, whitelist: list[str]):
    if whitelist is None:
        return True
    for white in whitelist:
        if white in s:
            return True
    return False


def _matches_blacklist(s: str, blacklist: list[str]):
    if blacklist is None:
        return False
    for black in blacklist:
        if black in s:
            return True
    return False
