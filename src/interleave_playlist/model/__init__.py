#    Interleave Playlist
#    Copyright (C) 2022-2025 Thomas Sweeney
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
import sys
import typing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Any
from uuid import uuid4

from crontab import CronTab


class Timed:
    def __init__(self, start: datetime, cron: CronTab, first: Optional[int] = None,
                 amount: Optional[int] = None, start_at_cron: Optional[bool] = False):
        self.start = (start.astimezone()
                      if start.tzinfo is None else
                      start)
        self.cron = cron
        self.first = (first if first is not None and first > 0 else 1) - 1
        self.amount = amount if amount is not None and amount > 0 else 1
        self.start_at_cron = start_at_cron

    def __repr__(self) -> str:
        return str(self.__dict__)

    def get_current(self) -> int:
        now: datetime = datetime.now().astimezone()
        if self.start > now:
            return -1
        initial: int = self.first + (self.amount if not self.start_at_cron else 0)
        if self.start_at_cron and self.cron.test(self.start):
            first_diff = timedelta(seconds=0)
        else:
            first_diff = timedelta(seconds=self.cron.next(self.start, default_utc=False))
        first_cron_amount: int = self.amount if self.start + first_diff <= now else 0
        if first_cron_amount == 0 and self.start_at_cron:
            return -1
        diff = timedelta(seconds=self.cron.next(self.start + first_diff, default_utc=False))
        cron_amount = self.amount * max((now - (self.start + first_diff)) // diff, 0)
        return initial + first_cron_amount + cron_amount - 1


@dataclass(frozen=True)
class Weight:
    name: str = field(hash=True)
    weight: int

    def __lt__(self, other: Any) -> bool:
        if self.weight < other.weight:
            return True
        if self.name > other.name:
            return True
        return False

    def __gt__(self, other: Any) -> bool:
        if self.weight > other.weight:
            return True
        if self.name < other.name:
            return True
        return False

    def __le__(self, other: Any) -> bool:
        return typing.cast(bool, self > other or self == other)

    def __ge__(self, other: Any) -> bool:
        return typing.cast(bool, self > other or self == other)


@dataclass(unsafe_hash=True)
class Group:
    name: str = field(hash=True)
    location_name: str = field(default="", hash=True)
    priority: int = field(default=sys.maxsize, hash=False, compare=False)
    whitelist: list[str] = field(default_factory=list, hash=False, compare=False)
    blacklist: list[str] = field(default_factory=list, hash=False, compare=False)
    timed: Optional[Timed] = field(default=None, hash=False, compare=False)
    exact: Optional[bool] = field(default=False)
    weight: Weight = field(default=Weight(str(uuid4()), 0))

    def __post_init__(self) -> None:
        if self.priority is None:
            self.priority = sys.maxsize
        if self.whitelist is None:
            self.whitelist = []
        if self.blacklist is None:
            self.blacklist = []


@dataclass(unsafe_hash=True)
class Location:
    name: str = field(hash=True)
    default_group: Group = field(hash=False)
    additional: list[str] = field(default_factory=list, hash=False)
    regex: Optional[str] = field(default=None, hash=False)
    groups: list[Group] = field(default_factory=list, hash=False)

    def __post_init__(self) -> None:
        if self.groups is None:
            self.groups = []
        if self.additional is None:
            self.additional = []
