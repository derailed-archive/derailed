"""Provides interop with the "synchronous" ScyllaDB wrapper."""


import asyncio
import os
import platform
import threading
from typing import TypeVar

from cassandra.cluster import Cluster, ResultSet
from cassandra.io.libevreactor import LibevConnection
from cassandra.query import dict_factory

T = TypeVar("T")


class _Scyx(threading.Thread):
    def __init__(self, *, daemon: bool | None = None, **kwargs) -> None:
        super().__init__(daemon=daemon, **kwargs)
        plat = platform.system()
        # we can only use the Libev connection on Linux/MacOS.
        if plat == "Windows":
            self.cluster = Cluster(os.environ["SCYLLA_URI"].split(","))
        else:
            self.cluster = Cluster(
                os.environ["SCYLLA_URI"].split(","), connection_class=LibevConnection
            )
        self.session = None

    def run(self) -> None:
        self.session = self.cluster.connect()
        self.session.row_factory = dict_factory

    def _execute(self, query: str, args: tuple, keyspace: str) -> ResultSet:
        stmt = self.session.prepare(query, keyspace=keyspace)
        return self.session.execute(stmt, args, timeout=30)

    def one(self, query: str, args: tuple, keyspace: str, type: T) -> T | None:
        return self._execute(query, args, keyspace).one()

    def all(self, query: str, args: tuple, keyspace: str, type: T) -> list[T]:
        return self._execute(query, args, keyspace).all()


class ScyllaDB:
    def __init__(self) -> None:
        self._started = False
        self._thread = _Scyx()

    def connect(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    async def all(
        self, keyspace: str, query: str, type: T, args: tuple = ()
    ) -> list[T]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._thread, self._thread.all, query, args, keyspace, type
        )

    async def one(
        self, keyspace: str, query: str, type: T, args: tuple = ()
    ) -> T | None:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._thread, self._thread.one, query, args, keyspace, type
        )


SCYX = ScyllaDB()
