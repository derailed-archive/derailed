from __future__ import annotations

from typing import Annotated, Literal, NotRequired, final

from fastapi import Depends, Header, Path
from typing_extensions import TypedDict

from .auth import verify_token
from .controllers.dbs import DB, use_db
from .error import Err
from .flags import ALL_PERMISSIONS, Permissions
from .utils import f1, fetch


@final
class User(TypedDict):
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
class Settings(TypedDict):
    theme: str
    status: int


@final
class GuildFolder(TypedDict):
    id: int
    name: str | None
    user_id: str

    # slots
    slots: list[GuildSlot]


@final
class GuildSlot(TypedDict):
    folder_id: int
    guild_id: int
    position: int


class Guild(TypedDict):
    id: int
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
    user_id: int
    guild_id: int
    nick: str | None
    joined_at: str
    deaf: bool
    mute: bool
    roles: list[int]


@final
class Device(TypedDict):
    id: int
    user_id: int


async def get_user(
    db: Annotated[DB, Depends(use_db)],
    str_token: Annotated[str, Header(alias="Authorization")],
) -> User:
    token = verify_token(str_token)

    device = await f1(
        "SELECT * FROM devices WHERE id = $1;", db, token["device_id"], t=Device
    )

    if device:
        return await f1(
            "SELECT * FROM users WHERE id = $1;", db, device["user_id"], t=User
        )

    raise Err("invalid device for authorization token", 401)


async def get_guild(
    db: Annotated[DB, Depends(use_db)], guild_id: Annotated[int, Path()]
) -> Guild:
    guild = await f1("SELECT * FROM guilds WHERE id = $1;", db, guild_id, t=Guild)

    if guild is None:
        raise Err("guild not found", 404)

    guild["features"] = await fetch(
        "SELECT feature FROM guild_features WHERE guild_id = $1", db, guild_id
    )

    return guild


async def get_member(
    db: Annotated[DB, Depends(use_db)],
    guild: Annotated[Guild, Depends(get_guild)],
    user: Annotated[User, Depends(get_user)],
) -> Member:
    member = await f1(
        "SELECT * FROM guild_members WHERE guild_id = $1 AND user_id = $2",
        db,
        guild["id"],
        user["id"],
        t=Member,
    )

    if member is None:
        raise Err("you are not a member of this guild", 403)

    member["roles"] = await fetch(
        "SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2;",
        db,
        member["user_id"],
        member["guild_id"],
        t=str,
    )

    return member


async def get_permissions(
    db: Annotated[DB, Depends(use_db)],
    member: Annotated[Member, Depends(get_member)],
    guild: Annotated[Guild, Depends(get_guild)],
) -> Permissions:
    if guild["owner_id"] == member["user_id"]:
        return ALL_PERMISSIONS

    base = guild["permissions"]

    # NOTE: roles take precedant over guild aka @everyone.
    role_permissions = await fetch(
        "SELECT (allow, deny, position) FROM roles WHERE id IN (SELECT role_id FROM member_assigned_roles WHERE user_id = $1 AND guild_id = $2);",
        db,
        member["user_id"],
        guild["id"],
        t=Role,
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
    id: int
    guild_id: int
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


class Overwrite(TypedDict):
    id: int
    channel_id: int
    type: int
    allow: int
    deny: int


@final
class Channel(TypedDict):
    id: int
    type: int
    guild_id: NotRequired[int | None]
    name: NotRequired[str | None]
    position: NotRequired[int]
    topic: NotRequired[str | None]
    last_message_id: NotRequired[int | None]
    parent_id: NotRequired[int | None]
    sync_parent_permissions: NotRequired[bool]

    permission_overwrites: NotRequired[Overwrite]


async def get_channel(
    db: Annotated[DB, Depends(use_db)], channel_id: Annotated[str, Path()]
) -> Channel:
    channel = await f1(
        "SELECT * FROM channels WHERE id = $1", db, channel_id, t=Channel
    )

    if channel is None:
        raise Err("channel not found", 404)

    channel["permission_overwrites"] = await fetch(
        "SELECT (id, type, allow, deny) FROM permission_overwrites WHERE channel_id = $1;",
        db,
        channel_id,
        t=Overwrite,
    )

    return channel


@final
class ChannelMention(TypedDict):
    message_id: int
    channel_id: int


@final
class UserMention(TypedDict):
    user_id: int
    channel_id: int


@final
class Message(TypedDict):
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

    # mentions
    channel_mentions: NotRequired[list[int]]
    user_mentions: NotRequired[list[int]]
    role_mentions: NotRequired[list[int]]


async def get_message(
    db: Annotated[DB, Depends(use_db)], message_id: Annotated[int, Path()]
) -> Message:
    message = await f1(
        "SELECT * FROM messages WHERE id = $1;", db, message_id, t=Message
    )

    if message is None:
        raise Err("message not found", 404)

    message["channel_mentions"] = await fetch(
        "SELECT channel_id FROM message_channel_mentions WHERE message_id = $1;",
        db,
        message_id,
        t=ChannelMention,
    )
    message["user_mentions"] = await fetch(
        "SELECT user_id FROM message_user_mentions WHERE message_id = $1;",
        db,
        message_id,
        t=UserMention,
    )
    message["role_mentions"] = await fetch(
        "SELECT role_id FROM message_role_mentions WHERE message_id = $1;",
        db,
        message_id,
        t=UserMention,
    )

    return message


async def get_messages(db: DB, channel_id: int, limit: int = 25) -> list[Message]:
    messages = await f1(
        f"SELECT * FROM messages WHERE channel_id = $1 LIMIT {limit};",
        db,
        channel_id,
        t=Channel,
    )

    message_ids = [message["id"] for message in messages]

    channel_mentions = await fetch(
        "SELECT * FROM message_channel_mentions WHERE message_id IN $1;",
        db,
        message_ids,
        t=ChannelMention,
    )
    user_mentions = await fetch(
        "SELECT * FROM message_user_mentions WHERE message_id IN $1;", db, message_ids
    )

    added_content = {
        message_id: {"channel_mentions": [], "user_mentions": []}
        for message_id in message_ids
    }

    for cm in channel_mentions:
        added_content[cm["message_id"]]["channel_mentions"].append(cm["channel_id"])

    for um in user_mentions:
        added_content[um["message_id"]]["user_mentions"].append(um["user_id"])

    for message in messages:
        message["user_mentions"] = added_content[message["id"]]["user_mentions"]
        message["channel_mentions"] = added_content[message["id"]]["channel_mentions"]

    return messages


@final
class ReadState(TypedDict):
    channel_id: int
    mentions: int
    last_message_id: int


async def get_channel_read_state(
    channel: Annotated[Channel, Depends(get_channel)],
    user: Annotated[User, Depends(get_user)],
    db: Annotated[DB, Depends(use_db)],
) -> ReadState:
    read_state = await f1(
        "SELECT (mentions, last_message_id) FROM read_states WHERE user_id = $1 AND channel_id = $2;",
        db,
        user["id"],
        channel["id"],
        t=ReadState,
    )

    if read_state is None:
        raise Err("Read State for channel does not exist", 404)

    return read_state


@final
class MessageReaction(TypedDict):
    message_id: int
    user_id: int
    created_at: str
    emoji: str
