from persistence.settings import _create_settings_file
from persistence.state import get_last_input_file, _create_state_file


def create_needed_files():
    _create_settings_file()
    _create_state_file()
