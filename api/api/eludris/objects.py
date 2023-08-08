from dataclasses import dataclass
from datetime import datetime
from typing import Any, Generic, Literal, Self, Type, TypeVar

from api.api.eludris.models import ChannelData, MessageReactionData, SettingsData

from ..controllers.dbs import DB
from ..scylla import ScyllaDB
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
    ChannelMentionData,
    DeviceData,
    GuildData,
    GuildPreviewData,
    MemberData,
    MessageData,
    MessageReactionCounterData,
    MessageReactionData,
    ReadStateData,
    RoleData,
    SettingsData,
    UserData,
)
from .parsers import parse_to_flag

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

        return self.convert_obj(mapping)

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

    def convert_obj(self, obj: T) -> T:
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

    async def delete(self, id: int, db: DB, delete_key: str = "id") -> None:
        await commit(f"DELETE FROM {self._table} WHERE {delete_key} = $1", db, id)


# TODO: implement this before messages.
class ScyllaObject(BaseObject[T]):
    _keyspace: str = ""


class ObjectList(list[BaseObject]):
    def representable(self) -> list[dict[str, Any]]:
        return [obj.__dict__ for obj in self]


class Counter(ScyllaObject[T]):
    async def incr(self, field: str, db: ScyllaDB, identifier_name: str) -> None:
        await db.execute(
            self._keyspace,
            f"UPDATE {self._table} SET {field} + 1 WHERE {identifier_name} = $1",
            (getattr(self, identifier_name)),
        )

    async def decr(self, field: str, db: ScyllaDB, identifier_name: str) -> None:
        await db.execute(
            self._keyspace,
            f"UPDATE {self._table} SET {field} - 1 WHERE {identifier_name} = $1",
            (getattr(self, identifier_name)),
        )


@dataclass(kw_only=True)
class User(BaseObject[UserData]):
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
        self.flags = parse_to_flag(UserFlags, self.flags)
        self.cold_save()

    def convert_obj(self, obj: UserData) -> UserData:
        obj["flags"] = int(self.flags)
        return obj


@dataclass(kw_only=True)
class Settings(BaseObject[SettingsData]):
    _table = "user_settings"

    user_id: int
    theme: Theme
    status: Status

    def parse_obj(self) -> None:
        self.theme = parse_to_flag(Theme, self.theme)
        self.status = parse_to_flag(Status, self.status)
        self.cold_save()

    def convert_obj(self, obj: SettingsData) -> SettingsData:
        obj["theme"] = str(self.theme)
        obj["status"] = int(self.status)
        return obj


@dataclass(kw_only=True)
class Guild(BaseObject[GuildData | GuildPreviewData]):
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
            self.permissions = parse_to_flag(Permissions, self.permissions)
        self.features = [parse_to_flag(Features, v) for v in self.features]
        self.cold_save()

    def convert_obj(self, obj: GuildData) -> GuildData:
        if self.permissions:
            obj["permissions"] = int(self.permissions)
        obj["features"] = [str(f) for f in self.features]
        return obj


@dataclass(kw_only=True)
class Member(BaseObject[MemberData]):
    _table = "guild_members"

    user_id: int
    guild_id: int
    nick: str | None
    joined_at: datetime
    deaf: bool
    mute: bool

    def parse_obj(self) -> None:
        self.joined_at = datetime.fromisoformat(self.joined_at)
        self.cold_save()

    def convert_obj(self, obj: MemberData) -> MemberData:
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
class Device(BaseObject[DeviceData]):
    _table = "devices"

    id: int
    user_id: int


@dataclass(kw_only=True)
class Role(BaseObject[RoleData]):
    _table = "roles"

    id: int
    guild_id: int
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


@dataclass(kw_only=True)
class Channel(BaseObject[ChannelData]):
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
        self.type = parse_to_flag(ChannelTypes, self.type)
        self.cold_save()

    def convert_obj(self, obj: ChannelData) -> ChannelData:
        obj["type"] = int(self.type)
        return obj


# ↓ ScyllaDB-related objects.


@dataclass(kw_only=True)
class ChannelMention(ScyllaObject[ChannelMentionData]):
    _table = "message_channel_mentions"
    _keyspace = "messages"

    message_id: int
    channel_id: int


@dataclass(kw_only=True)
class UserMention(ScyllaObject[ChannelMentionData]):
    _table = "message_channel_mentions"
    _keyspace = "messages"

    message_id: int
    user_id: int


@dataclass(kw_only=True)
class Message(ScyllaObject[MessageData]):
    _table = "messages"
    _keyspace = "messages"

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
        self.flags = parse_to_flag(MessageFlags, self.flags)
        self.timestamp = datetime.fromisoformat(self.timestamp)
        if self.edited_timestamp:
            self.edited_timestamp = datetime.fromisoformat(self.edited_timestamp)
        self.cold_save()

    def convert_obj(self, obj: ChannelData) -> ChannelData:
        obj["flags"] = int(self.flag)
        obj["timestamp"] = self.timestamp.isoformat("minutes")
        if self.edited_timestamp:
            obj["edited_timestamp"] = self.edited_timestamp.isoformat("minutes")
        return obj


@dataclass(kw_only=True)
class ReadState(Counter[ReadStateData]):
    _table = "read_states"
    _keyspace = "messages"

    user_id: int
    channel_id: int
    mentions: int
    last_message_id: int


@dataclass(kw_only=True)
class MessageReactionCounter(Counter[MessageReactionCounterData]):
    _table = "message_reaction_counters"
    _keyspace = "messages"

    message_id: int
    emoji: str
    count: int


@dataclass(kw_only=True)
class MessageReaction(ScyllaObject[MessageReactionData]):
    _table = "message_reactions"
    _keyspace = "messages"

    message_id: int
    user_id: int
    bucket_id: int
    created_at: datetime
    emoji: str

    def parse_obj(self) -> None:
        self.created_at = datetime.fromisoformat(self.created_at)

    def convert_obj(self, obj: MessageReactionData) -> MessageReactionData:
        obj["created_at"] = self.created_at.isoformat()
        return obj
