import os

import asyncpg
import redis.asyncio as redis
from asyncpg.pool import PoolConnectionProxy


class DatabaseController:
    def __init__(self) -> None:
        self.pool = None
        self.redis = None

    async def maybe_setup(self) -> None:
        if self.pool is None:
            self.pool = await asyncpg.create_pool(dsn=os.environ["PG_URI"])
        if self.redis is None:
            self.redis = redis.Redis.from_url(os.environ["REDIS_URI"])


controller = DatabaseController()


DB = PoolConnectionProxy


async def use_db() -> DB:  # type: ignore
    await controller.maybe_setup()

    async with controller.pool.acquire() as session:
        try:
            yield session
        finally:
            if not session.is_closed():
                await session.close()


async def use_redis() -> redis.Redis:
    return controller.redis
