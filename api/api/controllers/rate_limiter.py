import hashlib
from typing import Annotated

import redis.asyncio as redlib
from fastapi import Depends, Path, Request, Response

from ..error import Err
from .dbs import use_redis


class UnscopedRateLimiter:
    GLOBAL_LIMIT = 80
    PER = 60

    def __init__(
        self, bucket: str, limit: int, per: int, global_scope: bool = False
    ) -> None:
        self.limit = limit
        self.per = per
        self.bucket = bucket
        self.global_scope = global_scope

    async def __call__(
        self,
        user: Annotated[User | None, Depends(UseUser(["id"], optional=True))],
        redis: Annotated[redlib.Redis, Depends(use_redis)],
    ) -> None:
        if user is None:
            return

        unserialized_bucket_id = f"{self.bucket}:{user['id']}"
        bucket_id = hashlib.md5(unserialized_bucket_id.encode()).hexdigest()

        bucket = await redis.get(bucket_id)

        if bucket is None:
            remaining = self.limit - 1
            await redis.set(bucket_id, remaining, ex=self.per)
        else:
            remaining = await redis.decr(bucket_id)

        reset_after = await redis.ttl(bucket_id)

        if remaining == 0:
            raise Err(
                {
                    "message": "You have been rate limited.",
                    "retry_after": reset_after,
                    "global": self.global_scope,
                },
                429,
            )


class ScopedRateLimiter:
    def __init__(self, limit: int = 10, per: int = 1) -> None:
        self.limit = limit
        self.per = per

    async def __call__(
        self,
        channel_id: Annotated[int | None, Path(None)],
        guild_id: Annotated[int | None, Path(None)],
        redis: Annotated[redlib.Redis, Depends(use_redis)],
        user: Annotated[User | None, Depends(UseUser(["id"], optional=True))],
        request: Request,
        response: Response,
    ) -> None:
        # cannot be applied to non-users
        if user is None:
            return

        unserialized_bucket_id = (
            f"{user['id']}:{channel_id}:{guild_id}:{request.url.path}:{request.method}"
        )
        bucket_id = hashlib.md5(unserialized_bucket_id.encode()).hexdigest()

        bucket = await redis.get(bucket_id)

        if bucket is None:
            remaining = self.limit - 1
            await redis.set(bucket_id, remaining, ex=self.per)
        else:
            remaining = await redis.decr(bucket_id)

        reset_after = await redis.ttl(bucket_id)

        response.headers["X-RateLimit-Bucket"] = bucket_id
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Reset-After"] = str(reset_after)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        if remaining == 0:
            raise Err(
                {
                    "detail": "You have been rate limited.",
                    "retry_after": reset_after,
                    "global": False,
                },
                429,
            )
