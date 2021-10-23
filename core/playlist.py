import os
from os import path

import settings
from core.interleave import interleave_all


def get_playlist(use_blacklist: bool = True) -> iter:
    if use_blacklist:
        with open('config/blacklist.txt', 'r') as f:
            blacklist = [line.strip() for line in f]
    else:
        blacklist = []

    data = []
    for loc in settings.get_locations():
        data.append(sorted(filter(
            lambda i: ('.mkv' in i or '.mp4' in i),
            map(lambda i: loc + '/' + i, os.listdir(loc))
        )))

    return filter(lambda d: path.basename(d) not in blacklist, interleave_all(data))


def main():
    for item in get_playlist():
        print(item)


if __name__ == '__main__':
    main()
