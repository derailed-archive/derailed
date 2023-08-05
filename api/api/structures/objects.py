from dataclasses import dataclass
from typing import Any, Generic, Literal, Self, Type, TypeVar

from ..controllers.dbs import DB
from ..utils import MISSING, Maybe, commit
from .flags import Features, Permissions
from .models import Guild
from .parsers import parse_to_flag, parse_to_int, parse_to_str

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
        self.parse_obj()
        return self

    def parse_obj(self) -> None:
        pass

    async def insert(self, db: DB) -> None:
        pass

    async def save(self, db: DB) -> None:
        changes: list[tuple[str, Any]] = []

        for k, v in self._props.copy().items():
            attr = getattr(self, k)

            if attr != v:
                if v is MISSING:
                    continue
                self._props[k] = v
                changes.append((k, v))

        for change in changes:
            await commit(f"UPDATE {self._table} SET {change[0]} = $1;", db, change[1])

    @classmethod
    async def from_id(cls, id: int) -> Self:
        pass

    async def delete(self, id: int, db: DB, delete_key: str = "id") -> None:
        await commit(f"DELETE FROM {self._table} WHERE {delete_key} = $1", db, id)


# TODO: implement this before messages.
class ScyllaObject(BaseObject[T]):
    ...


class ObjectList(list[BaseObject]):
    def representable(self) -> list[dict[str, Any]]:
        return [obj.__dict__ for obj in self]


@dataclass(slots=True, kw_only=True)
class GuildModel(BaseObject[Guild]):
    _table = "guilds"

    id: int
    name: str
    icon: Maybe[str | None] = MISSING
    owner_id: int
    features: list[Features]
    system_channel_id: Maybe[int | None] = MISSING
    type: Maybe[Literal["nsfw", "community"]] = MISSING
    max_members: Maybe[int] = MISSING
    permissions: Maybe[Permissions] = MISSING

    parse_permissions = parse_to_int
    parse_features = parse_to_str
    convert_permissions = parse_to_flag(Permissions)
    convert_features = parse_to_flag(Features)
