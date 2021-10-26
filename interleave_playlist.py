from interface.PlaylistApplication import PlaylistApplication
from persistence import create_needed_files

if __name__ == "__main__":
    create_needed_files()
    PlaylistApplication([])
