import inspect
from dataclasses import dataclass
from typing import Any, Generic, Literal, Self, TypeVar

from ..utils import Maybe
from .flags import Permissions
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

            mapping[attr] = realattr

        return mapping

    @classmethod
    def load(cls, map: dict[str, Any]) -> Self:
        return cls(**map)


@dataclass
class GuildModel(BaseObject[Guild]):
    id: int
    name: str
    icon: str | None
    owner_id: int
    features: list[str]
    system_channel_id: Maybe[int | None]
    type: Maybe[Literal["nsfw", "community"]]
    max_members: Maybe[int]
    permissions: Maybe[Permissions]
