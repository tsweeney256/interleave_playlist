#    Interleave Playlist
#    Copyright (C) 2021-2022 Thomas Sweeney
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
import sys
from datetime import datetime, timedelta

from crontab import CronTab

from interleave_playlist import util
from interleave_playlist.persistence.settings import _create_settings_file

_STATE_FILE = os.path.join(util.SCRIPT_LOC, 'config', 'state.json')


class Timed:
    def __init__(self, start: datetime, cron: CronTab, first: int,
                 amount: int, start_at_cron: bool):
        self.start = (start.astimezone()
                      if start.tzinfo is None else
                      start)
        self.cron = cron
        self.first = (first if first is not None and first > 0 else 1) - 1
        self.amount = amount if amount is not None and amount > 0 else 1
        self.start_at_cron = start_at_cron

    def __repr__(self):
        return str(self.__dict__)

    def get_current(self) -> int:
        now: datetime = datetime.now().astimezone()
        if self.start > now:
            return -1
        initial: int = self.first + (self.amount if not self.start_at_cron else 0)
        first_diff = timedelta(seconds=self.cron.next(self.start, default_utc=False))
        first_cron_amount: int = self.amount if self.start + first_diff < now else 0
        if first_cron_amount == 0 and self.start_at_cron:
            return -1
        diff = timedelta(seconds=self.cron.next(self.start + first_diff, default_utc=False))
        cron_amount = self.amount * max((now - (self.start + first_diff)) // diff, 0)
        return initial + first_cron_amount + cron_amount - 1


class Group:
    def __init__(self, name: str, priority: int, whitelist: list[str], blacklist: list[str],
                 timed: Timed):
        self.name = name
        self.priority = priority if priority is not None else sys.maxsize
        self.whitelist = whitelist
        self.blacklist = blacklist
        self.timed = timed

    def __repr__(self):
        return str(self.__dict__)


class Location:
    def __init__(self, name: str, additional: list[str], default_group: Group, regex: str,
                 groups: list[Group]):
        self.name = name
        self.additional = additional
        self.default_group = default_group
        self.regex = regex
        self.groups = groups if groups is not None else []

    def __repr__(self):
        return str(self.__dict__)


def _create_state_file():
    if not os.path.exists(_STATE_FILE):
        with open(_STATE_FILE, 'w') as f:
            f.write('{"last-input-file": "See config/input.yml.example"}')


def create_needed_files():
    _create_settings_file()
    _create_state_file()
