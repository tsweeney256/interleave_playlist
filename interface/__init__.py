import os
import platform
import subprocess

import settings
from core.playlist import get_playlist


# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
def open_with_default_application(filepath: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def _create_playlist_dict() -> dict[str, str]:
    with open(settings.get_watched_file_name(), 'r') as f:
        watched_list = [line.strip() for line in f]
    playlist = list(get_playlist(settings.get_locations(),  watched_list))
    return dict(zip(map(os.path.basename, playlist), playlist))


def _get_temp_file_name():
    return settings.get_watched_file_name() + '.tmp'
