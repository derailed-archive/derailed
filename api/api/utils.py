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


def _conv(val: Any) -> Any:
    v = dict(val)

    if len(v) == 1:
        return v.popitem()[1]

    return v


async def fetch(
    query: str, db: DB, *args: object, t: Type[T] = dict[str, Any]
) -> list[T]:
    stmt = await db.prepare(query)
    return cast(T, [_conv(v) for v in await stmt.fetch(*args)])


async def f1(
    query: str, db: DB, *args: object, t: Type[T] = dict[str, Any]
) -> T | None:
    stmt = await db.prepare(query)
    return cast(T, _conv(await stmt.fetchrow(*args)))


def create_update(table: str, start_index: int = 0, *fields: str) -> str:
    base = f"UPDATE {table} "

    n = start_index

    for field in fields:
        n += 1
        base += f"SET {field} = ${n}"

    base += " "

    return base
