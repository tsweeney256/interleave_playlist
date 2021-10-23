import os

import settings
from core.interleave import interleave_all


def get_playlist():
    with open('config/blacklist.txt', 'r') as f:
        blacklist = [line.strip() for line in f]

    data = []
    for item in settings.get_locations():
        data.append(sorted(filter(
            lambda i: ('.mkv' in i or '.mp4' in i),
            os.listdir(item)
        )))

    return filter(lambda d: d not in blacklist, interleave_all(data))


def main():
    for item in get_playlist():
        print(item)


if __name__ == '__main__':
    main()
