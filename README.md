# Interleave Playlist
[![PyPi Version](https://img.shields.io/pypi/v/Interleave-Playlist.svg)](https://pypi.org/project/Interleave-Playlist/)
![Python Versions](https://img.shields.io/pypi/pyversions/Interleave-Playlist.svg)
![Tests](https://github.com/tsweeney256/interleave_playlist/actions/workflows/tests.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/tsweeney256/interleave_playlist/badge.svg?kill_cache=1)](https://coveralls.io/github/tsweeney256/interleave_playlist)

## Description

Interleave episodes of the shows you watch to maximize variety when catching up

![](https://raw.githubusercontent.com/tsweeney256/interleave_playlist/e8fb44208464c2dfd65db766c9e12b267d6f8beb/docs/images/screenshot.png)

## Basic Usage (Recommended)

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

## Basic Usage (Barebones)
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
