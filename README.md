# Interleave Playlist
[![PyPi Version](https://img.shields.io/pypi/v/Interleave-Playlist.svg)](https://pypi.org/project/Interleave-Playlist/)
![Python Versions](https://img.shields.io/pypi/pyversions/Interleave-Playlist.svg)
![Tests](https://github.com/tsweeney256/interleave_playlist/actions/workflows/tests.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/tsweeney256/interleave_playlist/badge.svg?kill_cache=1)](https://coveralls.io/github/tsweeney256/interleave_playlist)

## Description

Interleave episodes of the shows you watch to maximize variety when catching up

![](https://raw.githubusercontent.com/tsweeney256/interleave_playlist/e8fb44208464c2dfd65db766c9e12b267d6f8beb/docs/images/screenshot.png)

## Basic Usage (`uv`, Recommended)
This requires having `uv` installed. You can get `uv` from your package manager
or you can [install it manually](https://docs.astral.sh/uv/getting-started/installation/).

This should work on any operating system!

**Pre-Install**

If you just installed `uv` and never ran this yet, make sure to do so.
You only need to run this once after installing `uv`.

```shell
uv tool update-shell
```

**Install**

```shell
uv tool install --python 3.13 interleave-playlist
```

**Run**
You can run the following from the terminal to start the application.

```shell
interleave-playlist
```

On Linux, MacOS, and other BSDs, you can find the symlink in `~/.local/bin`.

On Windows, you can find the exe in `%USERPROFILE%\.local\bin`

**Update**

```shell
uv tool upgrade interleave-playlist
```

If you wanted to upgrade your python version when you update, then you can run:
```
# python 3.13 is the max supported currently
uv tool upgrade --python 3.13 interleave-playlist
```

## Basic Usage (`venv`, Old)

Note that you can simplify this process with something like
[virtualenvwrapper](https://wiki.archlinux.org/title/Python/Virtual_environment#virtualenvwrapper)
instead of using venv directly.

**Install**

You'll need to make sure you have `venv` installed through your package manager of choice.
```shell
cd /where/I/want/to/install
python -m venv venv
source venv/bin/activate
python -m pip install Interleave-Playlist
```
**Run**

You'll want to put this in a script or make an alias to make running this more convenient
```shell
source /where/I/want/to/install/venv/bin/activate && python -m interleave_playlist
```

**Update**
```shell
source /where/I/want/to/install/venv/bin/activate
python -m pip install --upgrade Interleave-Playlist
```
If you run into the following error when updating:
> ModuleNotFoundError: No module named 'PySide6.QtWidgets'

Run the following:
```commandline
python -m pip uninstall PySide6 PySide6_Addons PySide6_Essentials
python -m pip install Interleave-Playlist
```

## Basic Usage (`pip`, Barebones)
**Install**
```shell
python -m pip install Interleave-Playlist
```
**Run**
```shell
python -m interleave_playlist
```
**Update**
```shell
python -m pip install --upgrade Interleave-Playlist
```
