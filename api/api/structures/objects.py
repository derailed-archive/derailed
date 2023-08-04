from enum import IntFlag
import functools
import inspect
from dataclasses import dataclass
from typing import Any, Generic, Literal, Self, TypeVar

from ..utils import MISSING, Maybe
from .flags import Features, Permissions
from .models import Guild

T = TypeVar("T", bound=dict)


class BaseObject(Generic[T]):
    """Represents a mutable Derailed object."""

    @property
    def __dict__(self) -> T:
        attrs = dir(self)

        mapping: T = {}

        for attr in attrs:
            realattr = getattr(self, attr)

            if inspect.isfunction(realattr):
                continue
            elif inspect.isclass(realattr):
                continue
            elif inspect.ismethod(realattr):
                continue
            elif isinstance(realattr, property):
                continue
            elif realattr is MISSING:
                continue

            if hasattr(self, "parse_" + attr):
                mapping[attr] = getattr(self, "parse_" + attr)(realattr)
            else:
                mapping[attr] = realattr

        return mapping

    @classmethod
    def load(cls, map: dict[str, Any]) -> Self:
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

def _parse_to_flag(f: Any, val: int) -> Any:
    return f(val)


def parse_to_flag(f: IntFlag) -> IntFlag:
    return functools.partial(_parse_to_flag, f)


def parse_to_int(val: Any) -> int:
    return int(val)


@dataclass(slots=True)
class GuildModel(BaseObject[T]):
    id: int
    name: str
    icon: str | None
    owner_id: int
    features: list[Features]
    system_channel_id: Maybe[int | None]
    type: Maybe[Literal["nsfw", "community"]]
    max_members: Maybe[int]
    permissions: Maybe[Permissions]

    parse_permissions = parse_to_int
    convert_features = parse_to_flag
