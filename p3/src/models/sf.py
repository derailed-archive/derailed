# Copyright (C) 2021-2023 Derailed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import threading
import time

__all__ = "snowflake"


Snowflake = int


class SnowflakeGenerator:
    """Pythonic generator for Snowflakes, using the thread ident
    and os process id as the worker and process id.

    Parameters
    ----------
    epoch: :class:`int`
        A UNIX epoch to use for generating snowflakes.
    """

    def __init__(self, epoch: int = 1649325271415) -> None:
        self.epoch = epoch
        """The epoch date this Snowflake generator should aim for."""

        self.incr = 0
        """Amount of Snowflakes generated by this generator."""

    def __generate(self) -> Snowflake:
        current_ms = int(time.time() * 1000)

        # timestamp: 63-22
        epoch = current_ms - self.epoch << 22

        # worker id: 21-17
        epoch |= (threading.current_thread().ident % 32) << 17
        # process id: 16-12
        epoch |= (os.getpid() % 32) << 12

        # increment: 11-0
        epoch |= self.incr % 4096

        # increment incr to make next snowflake generated, even with the same timestamp
        self.incr += 1

        return epoch

    def __next__(self) -> Snowflake:
        return self.__generate()

    def __iter__(self):
        yield next(self)


snowflake = SnowflakeGenerator()
