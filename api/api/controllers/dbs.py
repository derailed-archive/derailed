import os
from typing import Any

import asyncpg
import redis.asyncio as redis
from asyncpg.pool import PoolConnectionProxy
from asyncpg import Record


class DatabaseController:
    def __init__(self) -> None:
        self.pool = asyncpg.create_pool(dsn=os.environ["PG_URI"])
        self.redis = redis.Redis.from_url(os.environ["REDIS_URI"])


controller = DatabaseController()


DB = PoolConnectionProxy


async def use_db() -> DB[Record]:
    return await controller.pool.acquire()


async def use_redis() -> redis.Redis[Any]:
    return controller.redis
