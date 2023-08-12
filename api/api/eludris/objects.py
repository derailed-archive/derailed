from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, Self, Type, TypeVar

from ..controllers.dbs import DB
from ..utils import MISSING, Maybe, commit
from .flags import (
    ChannelTypes,
    Features,
    MessageFlags,
    Permissions,
    Status,
    Theme,
    UserFlags,
)
from .models import (
    ChannelData,
    GuildData,
    MemberData,
    MessageData,
    MessageReactionData,
    SettingsData,
    UserData,
)

T = TypeVar("T", bound=dict[str, Any])
BSO = TypeVar("BSO", bound="BaseObject")


class BaseObject:
    """Represents a mutable Derailed object."""

    _table: str
    _props: dict[str, Any]

    @property
    def __object__(self) -> Any:
        mapping: dict[str, Any] = {}

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

        return self.convert_obj(mapping)

    @classmethod
    def load(cls: Type[Self], map: dict[str, Any]) -> Self:
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

    def convert_obj(self, obj: Any) -> Any:
        return obj

    async def insert(self, db: DB) -> None:
        pass

    async def save(self, db: DB) -> None:
        changes: list[tuple[str, Any]] = []

        for k, v in self._props.copy().items():
            attr = getattr(self, k)

            if attr != v:
                if v is MISSING:
                    self._props[k] = v
                    continue
                self._props[k] = v
                changes.append((k, v))

        for change in changes:
            await commit(f"UPDATE {self._table} SET {change[0]} = $1;", db, change[1])

    def cold_save(self) -> None:
        for k, v in self._props.copy().items():
            attr = getattr(self, k)

            if attr != v:
                if v is MISSING:
                    continue
                self._props[k] = v

    @classmethod
    async def from_id(cls, id: int) -> Self:
        raise NotImplementedError


class NeedsDelete(BaseObject):
    async def delete(self, id: int, db: DB, delete_key: str | None = "id") -> None:
        await commit(f"DELETE FROM {self._table} WHERE {delete_key} = $1", db, id)


class ObjectList(list[BaseObject]):
    def representable(self) -> list[Any]:
        return [obj.__object__ for obj in self]


class Counter(BaseObject):
    async def incr(self, field: str, db: DB, identifier_name: str) -> None:
        await commit(
            f"UPDATE {self._table} SET {field} + 1 WHERE {identifier_name} = $1",
            db,
            getattr(self, identifier_name),
        )

    async def decr(self, field: str, db: DB, identifier_name: str) -> None:
        await commit(
            f"UPDATE {self._table} SET {field} - 1 WHERE {identifier_name} = $1",
            db,
            getattr(self, identifier_name),
        )


@dataclass(kw_only=True)
class User(NeedsDelete, BaseObject):
    _table = "users"

    id: int
    username: str
    flags: UserFlags
    bot: bool
    display_name: str | None
    avatar: str | None
    email: Maybe[str] = MISSING
    password: Maybe[str] = MISSING

    def parse_obj(self) -> None:
        self.flags = UserFlags(self.flags)
        self.cold_save()

    def convert_obj(self, obj: UserData) -> UserData:
        obj["flags"] = int(self.flags)
        return obj


@dataclass(kw_only=True)
class Settings(NeedsDelete, BaseObject):
    _table = "user_settings"

    user_id: int
    theme: Theme
    status: Status

    def parse_obj(self) -> None:
        self.theme = Theme(self.theme)
        self.status = Status(self.status)
        self.cold_save()

    def convert_obj(self, obj: SettingsData) -> SettingsData:
        obj["theme"] = str(self.theme)
        obj["status"] = int(self.status)
        return obj


@dataclass(kw_only=True)
class Guild(NeedsDelete, BaseObject):
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

    def parse_obj(self) -> None:
        if self.permissions:
            self.permissions = Permissions(self.permissions)
        self.features = [Features(v) for v in self.features]
        self.cold_save()

    def convert_obj(self, obj: GuildData) -> GuildData:
        if self.permissions:
            obj["permissions"] = int(self.permissions)
        obj["features"] = [str(f) for f in self.features]
        return obj


@dataclass(kw_only=True)
class Member(BaseObject):
    _table = "guild_members"

    user_id: int
    guild_id: int
    nick: str | None
    joined_at: datetime
    deaf: bool
    mute: bool

    def parse_obj(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self.joined_at, str)
        self.joined_at = datetime.fromisoformat(self.joined_at)
        self.cold_save()

    def convert_obj(self, obj: MemberData) -> MemberData:
        if isinstance(self.joined_at, datetime):
            obj["joined_at"] = self.joined_at.isoformat("minutes")
        return obj

    async def delete(self, db: DB) -> None:
        await commit(
            f"DELETE FROM {self._table} WHERE user_id = $1 AND guild_id = $2",
            db,
            self.user_id,
            self.guild_id,
        )


@dataclass(kw_only=True)
class Device(BaseObject):
    _table = "devices"

    id: int
    user_id: int


@dataclass(kw_only=True)
class Role(NeedsDelete, BaseObject):
    _table = "roles"

    id: int
    guild_id: int
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


@dataclass(kw_only=True)
class Channel(NeedsDelete, BaseObject):
    _table = "channels"

    id: int
    type: ChannelTypes
    guild_id: Maybe[int | None] = MISSING
    name: Maybe[str | None] = MISSING
    position: Maybe[int] = MISSING
    topic: Maybe[str | None] = MISSING
    last_message_id: int | None
    parent_id: Maybe[int | None] = MISSING

    def parse_obj(self) -> None:
        self.type = ChannelTypes(self.type)
        self.cold_save()

    def convert_obj(self, obj: ChannelData) -> ChannelData:
        obj["type"] = int(self.type)
        return obj


# TODO: delete
@dataclass(kw_only=True)
class ChannelMention(BaseObject):
    _table = "message_channel_mentions"

    message_id: int
    channel_id: int


# TODO: delete
@dataclass(kw_only=True)
class UserMention(BaseObject):
    _table = "message_channel_mentions"

    message_id: int
    user_id: int


@dataclass(kw_only=True)
class Message(BaseObject):
    _table = "messages"

    id: int
    channel_id: int
    author_id: int
    bucket_id: Maybe[int] = MISSING
    content: str
    timestamp: datetime
    edited_timestamp: datetime | None
    mention_everyone: bool
    pinned: bool
    pinned_at: Maybe[datetime] = MISSING
    referenced_message_id: int | None
    flags: MessageFlags

    def parse_obj(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self.timestamp, str)
            assert (
                isinstance(self.edited_timestamp, str) or self.edited_timestamp is None
            )

        self.flags = MessageFlags(self.flags)
        self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.edited_timestamp:
            self.edited_timestamp = datetime.fromisoformat(self.edited_timestamp)
        self.cold_save()

    def convert_obj(self, obj: MessageData) -> MessageData:
        obj["flags"] = int(self.flags)
        obj["timestamp"] = self.timestamp.isoformat("minutes")
        if self.edited_timestamp:
            obj["edited_timestamp"] = self.edited_timestamp.isoformat("minutes")
        return obj


@dataclass(kw_only=True)
class ReadState(Counter):
    _table = "read_states"

    user_id: int
    channel_id: int
    mentions: int
    last_message_id: int


@dataclass(kw_only=True)
class MessageReactionCounter(Counter):
    _table = "message_reaction_counters"

    message_id: int
    emoji: str
    count: int


@dataclass(kw_only=True)
class MessageReaction(BaseObject):
    _table = "message_reactions"

    message_id: int
    user_id: int
    bucket_id: int
    created_at: datetime
    emoji: str

    def parse_obj(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(self.created_at, str)

        self.created_at = datetime.fromisoformat(self.created_at)

    def convert_obj(self, obj: MessageReactionData) -> MessageReactionData:
        obj["created_at"] = self.created_at.isoformat()
        return obj
