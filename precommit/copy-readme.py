#    Interleave Playlist
#    Copyright (C) 2022 Thomas Sweeney
#    This file is part of Interleave Playlist.
#    Interleave Playlist is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    Interleave Playlist is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import shutil
from pathlib import Path


def is_different(a: Path, b: Path) -> bool:
    if not a.exists() or not b.exists():
        return True
    with open(a, 'r') as af:
        with open(b, 'r') as bf:
            return af.read() != bf.read()


def main() -> None:
    project_dir = Path(os.path.sep.join(Path(__file__).parts[:-2]))
    readme = project_dir / 'README.md'
    doc_index = project_dir / 'docs' / 'index.md'
    if is_different(readme, doc_index):
        shutil.copy(readme, doc_index)
        exit(1)


if __name__ == '__main__':
    main()
