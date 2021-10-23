import subprocess, os, platform
from core.playlist import get_playlist


# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
def open_with_default_application(filepath: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def _create_playlist_dict():
    playlist = list(get_playlist())
    return dict(zip(map(os.path.basename, playlist), playlist))