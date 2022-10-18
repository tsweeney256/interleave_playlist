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
import typing
from threading import Lock
from time import time_ns

from PySide6.QtCore import QThread, Signal, SignalInstance


class SearchBarThreadAlreadyDeadException(BaseException):
    pass


class SearchBarThread(QThread):
    completed = typing.cast(SignalInstance, Signal(str))
    error = typing.cast(SignalInstance, Signal(BaseException))

    def __init__(self, search_value: str, delay_ms: int):
        super(SearchBarThread, self).__init__()
        if delay_ms < 0:
            raise ValueError("delay_ms can not be negative")
        if search_value is None:
            raise ValueError("value must not be null")
        self._search_value = search_value
        self._delay_ns = delay_ms * 1000 * 1000
        self._wait_until = time_ns() + self._delay_ns
        self._lock = Lock()
        self._has_run = False
        self._running = False

    def __del__(self) -> None:
        self.wait()

    @property
    def search_value(self) -> str:
        return self._search_value

    @search_value.setter
    def search_value(self, search_value: str) -> None:
        self._lock.acquire()
        if not self._running and self._has_run:
            raise SearchBarThreadAlreadyDeadException()
        try:
            self._search_value = search_value
            self._wait_until = time_ns() + self._delay_ns
        finally:
            self._lock.release()

    def run(self) -> None:
        try:
            self._run()
        except BaseException as e:
            self.error.emit(e)
            self._lock.release()

    def _run(self) -> None:
        # _running and _has_run must be set in this order!!!
        self._running = True
        self._has_run = True
        while True:
            self._lock.acquire()
            now = time_ns()
            wait_until_copy = self._wait_until
            if self._wait_until <= now:
                break
            self._lock.release()
            self.msleep((wait_until_copy - now) // 1000 // 1000)
        self.completed.emit(self._search_value)
        self._running = False
        self._lock.release()
