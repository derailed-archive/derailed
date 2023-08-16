from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, Type, TypeVar, Union, cast

import pydantic

if TYPE_CHECKING:
    from .controllers.dbs import DB

T = TypeVar("T")
BM = TypeVar("BM", bound=pydantic.BaseModel)


class Missing(Enum):
    MISSING = None

    def __bool__(self) -> Literal[False]:
        return False


MISSING: Literal[Missing.MISSING] = Missing.MISSING


Maybe = Union[T, Missing]


def now() -> datetime:
    return datetime.now(timezone.utc)


async def commit(query: str, db: DB, *args: object) -> None:
    stmt = await db.prepare(query)
    await stmt.fetch(*args)


async def fetch(query: str, db: DB, *args: object, t: Type[T] = dict[str, Any]) -> list[T]:
    stmt = await db.prepare(query)
    return cast(T, await stmt.fetch(*args))


async def f1(query: str, db: DB, *args: object, t: Type[T] = dict[str, Any]) -> T | None:
    stmt = await db.prepare(query)
    return cast(T, await stmt.fetchrow(*args))

