import os
import platform
import subprocess
from math import log10, ceil

from PySide6.QtWidgets import QMessageBox

import persistence
from core.playlist import get_playlist
# https://stackoverflow.com/questions/434597/open-document-with-default-os-application-in-python-both-in-windows-and-mac-os
from persistence import input_


def open_with_default_application(filepath: str):
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', filepath))
    elif platform.system() == 'Windows':    # Windows
        os.startfile(filepath)
    else:                                   # linux variants
        subprocess.call(('xdg-open', filepath))


def _create_playlist_dict() -> dict[str, str]:
    try:
        with open(input_.get_watched_file_name(), 'r') as f:
            watched_list = [line.strip() for line in f]
        playlist = list(get_playlist(input_.get_locations(), watched_list))
        return dict(zip(map(os.path.basename, playlist), playlist))
    except FileNotFoundError:
        QMessageBox(text="Input yml file not found: {}\n\n"
                         "Please create or find file and open it"
                    .format(persistence.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    except input_.InvalidInputFile as e:
        QMessageBox(text="Error reading yml file. Please fix it and try again\n{}\n{}"
                    .format(e, persistence.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    except input_.LocationNotFound as e:
        QMessageBox(text="Location from input file not found. Please fix it and try again\n{}\n{}"
                    .format(e, persistence.get_last_input_file()),
                    icon=QMessageBox.Warning).exec()
    return {}


def _get_temp_file_name():
    return input_.get_watched_file_name() + '.tmp'


def _get_duration_str(ms: int, override_ms: int):
    hours, remainder = divmod(ms, 1000 * 60 * 60)
    minutes, remainder = divmod(remainder, 1000 * 60)
    seconds, remainder = divmod(remainder, 1000)
    hours_override = ms / (1000 * 60 * 60)
    hours_len = 2 if hours_override <= 0 else max(ceil(log10(hours_override)), 2)
    hours_fmt = '{' + ':0{}d'.format(hours_len) + '}'
    return (hours_fmt + ':{:02d}:{:02d}').format(hours, minutes, seconds)
