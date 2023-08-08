from __future__ import annotations

from typing import Literal, NotRequired, TypedDict, final

from ..controllers.dbs import DB
from ..utils import fetch
from .flags import ALL_PERMISSIONS, Permissions


@final
class UserData(TypedDict):
    id: int
    username: str
    display_name: NotRequired[str | None]
    avatar: NotRequired[str | None]
    email: NotRequired[str]
    password: NotRequired[str]
    flags: int
    bot: bool
    _token: NotRequired[str]


@final
class SettingsData(TypedDict):
    theme: str
    status: int


class GuildData(TypedDict):
    id: int
    name: str
    icon: NotRequired[str | None]
    owner_id: NotRequired[int]
    features: NotRequired[list[str]]
    system_channel_id: NotRequired[int | None]
    type: NotRequired[Literal["nsfw", "community"]]
    max_members: NotRequired[int]
    permissions: NotRequired[int]
    member: NotRequired[MemberData]
    channels: NotRequired[list[ChannelData]]
    roles: NotRequired[list[RoleData]]


@final
class GuildPreviewData(GuildData):
    available: bool
    presences: int


@final
class MemberData(TypedDict):
    user_id: int
    guild_id: int
    nick: str | None
    joined_at: str
    deaf: bool
    mute: bool
    roles: list[int]


@final
class DeviceData(TypedDict):
    id: int
    user_id: int


async def get_permset(hero, db: DB) -> Permissions:
    if hero.guild["owner_id"] == hero.user["id"]:
        return ALL_PERMISSIONS

    base = hero.guild["permissions"]

    # NOTE: roles take precedant over guild aka @everyone.
    role_permissions = await fetch(
        "SELECT (allow, deny, position) FROM roles WHERE id IN $1;",
        db,
        hero.member["roles"],
    )

    ordered_perms = []

    # higher = more power
    for role_perm in role_permissions:
        ordered_perms.insert(
            role_perm["position"], (role_perm["allow"], role_perm["deny"])
        )

    for permission in ordered_perms:
        base &= permission[1]

        base |= permission[0]

    permset = Permissions(base)

    if permset.ADMINISTRATOR:
        return ALL_PERMISSIONS

    return permset


@final
class RoleData(TypedDict):
    id: int
    guild_id: int
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


@final
class ChannelData(TypedDict):
    id: int
    type: int
    guild_id: NotRequired[int | None]
    name: NotRequired[str | None]
    position: NotRequired[int]
    topic: NotRequired[str | None]
    last_message_id: NotRequired[int | None]
    parent_id: NotRequired[int | None]


# ↓ ScyllaDB-related models.


@final
class ChannelMentionData(TypedDict):
    channel_id: int
    guild_id: int


@final
class MessageData(TypedDict):
    id: int
    channel_id: int
    author_id: int
    content: str
    timestamp: str
    edited_timestamp: NotRequired[str | None]
    mention_everyone: bool
    pinned: bool
    pinned_at: NotRequired[str | None]
    referenced_message_id: int | None
    flags: int


@final
class ReadStateData(TypedDict):
    channel_id: int
    mentions: int
    last_message_id: int


@final
class MessageReactionCounterData(TypedDict):
    message_id: int
    count: int
    emoji: str


@final
class MessageReactionData(TypedDict):
    message_id: int
    user_id: int
    bucket_id: int
    created_at: str
    emoji: str
