import os

import asyncpg
import redis.asyncio as redis
from asyncpg.pool import PoolConnectionProxy


class DatabaseController:
    def __init__(self) -> None:
        self.pool = asyncpg.create_pool(dsn=os.environ["PG_URI"])
        self.redis = redis.Redis.from_url(os.environ["REDIS_URI"])


controller = DatabaseController()


DB = PoolConnectionProxy


async def use_db() -> DB:  # type: ignore
    return await controller.pool.acquire()


async def use_redis() -> redis.Redis:
    return controller.redis
