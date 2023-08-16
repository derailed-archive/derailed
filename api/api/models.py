from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict, final

from fastapi import Depends, Header, Path

from .error import Err

from .auth import verify_token

from .controllers.dbs import DB, use_db
from .utils import f1, fetch
from .flags import ALL_PERMISSIONS, Permissions


@final
class User(TypedDict):
    id: str
    username: str
    display_name: NotRequired[str | None]
    avatar: NotRequired[str | None]
    email: NotRequired[str]
    password: NotRequired[str]
    flags: int
    bot: bool
    _token: NotRequired[str]


@final
class Settings(TypedDict):
    theme: str
    status: int


@final
class GuildFolder(TypedDict):
    id: str
    name: str | None
    user_id: str

    # slots
    slots: list[GuildSlot]


@final
class GuildSlot(TypedDict):
    folder_id: str
    guild_id: str
    user_id: str


class Guild(TypedDict):
    id: str
    name: str
    icon: NotRequired[str | None]
    owner_id: NotRequired[int]
    features: NotRequired[list[str]]
    system_channel_id: NotRequired[int | None]
    type: NotRequired[Literal["nsfw", "community"]]

    max_members: NotRequired[int]
    permissions: NotRequired[int]

    member: NotRequired[Member]
    channels: NotRequired[list[Channel]]
    roles: NotRequired[list[Role]]


@final
class GuildPreview(Guild):
    available: bool
    presences: int


@final
class Member(TypedDict):
    user_id: str
    guild_id: str
    nick: str | None
    joined_at: str
    deaf: bool
    mute: bool
    roles: list[int]


@final
class Device(TypedDict):
    id: str
    user_id: str


async def get_user(
    db: Annotated[DB, Depends(use_db)],
    str_token: Annotated[str, Header(alias='Authorization')]
) -> User:
    token = verify_token(str_token)

    device = await f1('SELECT * FROM devices WHERE id = $1;', db, token['device_id'], t=Device)

    if device:
        return await f1('SELECT * FROM users WHERE id = $1;', db, device['user_id'], t=User)

    raise Err('invalid device for authorization token', 401)


async def get_guild(
    db: Annotated[DB, Depends(use_db)],
    guild_id: Annotated[str, Path()]
) -> Guild:
    guild = await f1('SELECT * FROM guilds WHERE id = $1;', db, guild_id, t=Guild)

    if guild:
        return

    raise Err('guild not found', 404)


async def get_permissions(
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(get_user)],
    guild: Annotated[Guild, Depends(get_guild)]
) -> Permissions:
    if guild["owner_id"] == user["id"]:
        return ALL_PERMISSIONS

    base = guild["permissions"]

    # NOTE: roles take precedant over guild aka @everyone.
    role_permissions = await fetch(
        "SELECT (allow, deny, position) FROM roles WHERE id IN (SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2);",
        db,
        user['id'],
        guild['id'],
        t=Role
    )

    ordered_perms: list[tuple[int, int]] = []

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
class Role(TypedDict):
    id: str
    guild_id: str
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


@final
class Channel(TypedDict):
    id: str
    type: int
    guild_id: NotRequired[int | None]
    name: NotRequired[str | None]
    position: NotRequired[int]
    topic: NotRequired[str | None]
    last_message_id: NotRequired[int | None]
    parent_id: NotRequired[int | None]


@final
class ChannelMention(TypedDict):
    message_id: str
    channel_id: str


@final
class UserMention(TypedDict):
    user_id: str
    channel_id: str


@final
class Message(TypedDict):
    id: str
    channel_id: str
    author_id: str
    content: str
    timestamp: str
    edited_timestamp: NotRequired[str | None]
    mention_everyone: bool
    pinned: bool
    pinned_at: NotRequired[str | None]
    referenced_message_id: str | None
    flags: int

    # mentions
    channel_mentions: NotRequired[list[ChannelMention]]
    user_mentions: NotRequired[list[UserMention]]


@final
class ReadState(TypedDict):
    channel_id: str
    mentions: int
    last_message_id: str


@final
class MessageReactionCounter(TypedDict):
    message_id: str
    count: int
    emoji: str


@final
class MessageReaction(TypedDict):
    message_id: str
    user_id: str
    created_at: str
    emoji: str
