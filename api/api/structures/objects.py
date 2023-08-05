import functools
import inspect
from dataclasses import dataclass
from enum import Enum, IntFlag
from typing import Any, Generic, Literal, Self, Type, TypeVar

from ..controllers.dbs import DB
from ..utils import MISSING, Maybe, commit
from .flags import Features, Permissions
from .models import Guild

T = TypeVar("T", bound=dict)
BSO = TypeVar("BSO", bound="BaseObject")


class BaseObject(Generic[T]):
    """Represents a mutable Derailed object."""

    _table: str
    _props: dict[str, Any]

    @property
    def __dict__(self) -> T:
        mapping: T = {}

        for attr, val in self._props.items():
            if val is MISSING:
                continue

            if hasattr(self, "parse_" + attr):
                func = getattr(self, "parse_" + attr)
                if isinstance(val, list):
                    nattr = []
                    for obj in val:
                        nattr.append(func(obj))
                    mapping[attr] = nattr
                else:
                    mapping[attr] = func(val)
            else:
                mapping[attr] = val

        return mapping

    @classmethod
    def load(cls: Type[BSO], map: T) -> Self:
        for k, v in map.items():
            aname = "convert_" + k

            if hasattr(cls, aname):
                attr = getattr(cls, aname)
                if isinstance(v, list):
                    nv = []
                    for i in v:
                        nv.append(attr(i))
                    map[k] = nv
                else:
                    map[k] = attr(v)

        self = cls(**map)
        self._props = map
        return self

    async def save(self, db: DB) -> None:
        changes: list[tuple[str, Any]] = []

        for k, v in self._props.copy().items():
            attr = getattr(self, k)

            if attr != v:
                self._props[k] = v
                changes.append((k, v))

        for change in changes:
            await commit(f"UPDATE {self._table} SET {change[0]} = $1;", db, change[1])

    @classmethod
    async def from_id(cls, id: int) -> Self:
        ...

    async def delete(self, id: int, db: DB, delete_key: str = "id") -> None:
        await commit(f"DELETE FROM {self._table} WHERE {delete_key} = $1", db, id)


def _parse_to_flag(f: Any, val: int) -> Any:
    return f(val)


def parse_to_flag(f: Enum):
    return functools.partial(_parse_to_flag, f)


def parse_to_int(val: Any) -> int:
    return int(val)


def parse_to_str(val: Any) -> str:
    return str(val)


def _parse_to_object(obj: Type[BSO], val: Any) -> T:
    return obj.load(val)


def parse_to_object(obj: Any) -> Any:
    return functools.partial(_parse_to_object, obj)


def _parse_id_to_object(obj: Type[BSO], val: int) -> T:
    return obj.from_id(val)


def parse_id_to_object(obj: Any) -> Any:
    return functools.partial(_parse_id_to_object, obj)


@dataclass(slots=True)
class GuildModel(BaseObject[Guild]):
    _table = "guilds"

    id: int
    name: str = MISSING
    icon: Maybe[str | None] = MISSING
    owner_id: int = MISSING
    features: list[Features]
    system_channel_id: Maybe[int | None] = MISSING
    type: Maybe[Literal["nsfw", "community"]] = MISSING
    max_members: Maybe[int] = MISSING
    permissions: Maybe[Permissions] = MISSING

    parse_permissions = parse_to_int
    parse_features = parse_to_str
    convert_permissions = parse_to_flag(Permissions)
    convert_features = parse_to_flag(Features)
