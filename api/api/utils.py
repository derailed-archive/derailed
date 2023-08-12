from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

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


async def fetch(query: str, db: DB, *args: object) -> list[dict[str, Any]]:
    stmt = await db.prepare(query)
    return cast(list[dict[str, Any]], await stmt.fetch(*args))


async def f1(query: str, db: DB, *args: object) -> dict[str, Any] | None:
    stmt = await db.prepare(query)
    return cast(dict[str, Any] | None, await stmt.fetchrow(*args))


def create_update(table: str, start_index: int = 0, *fields: str) -> str:
    base = f"UPDATE {table} "

    n = start_index

    for field in fields:
        n += 1
        base += f"SET {field} = ${n}"

    base += " "

    return base
