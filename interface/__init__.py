import os
import platform
import subprocess

from PySide6.QtWidgets import QMessageBox

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
    try:
        with open(settings.get_watched_file_name(), 'r') as f:
            watched_list = [line.strip() for line in f]
        playlist = list(get_playlist(settings.get_locations(),  watched_list))
        return dict(zip(map(os.path.basename, playlist), playlist))
    except FileNotFoundError:
        QMessageBox(text="Input yml file not found: {}\n\n"
                         "Please create or find file and open it"
                    .format(settings.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    except settings.InvalidInputFile:
        QMessageBox(text="Unable to parse input yml file. Please fix it and try again\n\n{}"
                    .format(settings.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    return {}


def _get_temp_file_name():
    return settings.get_watched_file_name() + '.tmp'
