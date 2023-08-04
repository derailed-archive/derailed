from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict, final

from fastapi import Depends, Path

from ..auth import verify_token
from ..controllers.dbs import DB, use_db
from ..error import Err
from ..utils import fetch, fetchrow
from .flags import ALL_PERMISSIONS, Permissions


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


class UseUser:
    def __init__(self, *fields: str, optional: bool = False) -> None:
        self.fields = list(fields)
        self.fields.sort()
        self.optional = optional

    async def __call__(
        self, authorization: Annotated[str, Path()], db: Annotated[DB, Depends(use_db)]
    ) -> User | None:
        token = verify_token(authorization)

        user = await fetchrow(
            "SELECT $1 FROM users WHERE id = $2;", db, self.fields, token["user_id"]
        )

        if user is None:
            if self.optional:
                return None
            raise Err("invalid token", 401)

        device = await fetchrow(
            "SELECT id FROM devices WHERE id = $1 AND user_id = $2;"
        )

        if device is None:
            if self.optional:
                return None
            raise Err("device of token has been invalidated", 401)

        return user

    def __eq__(self, other: "UseUser") -> bool:
        return self.fields == other.fields


@final
class Settings(TypedDict):
    theme: str
    status: int


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


class UseGuild:
    def __init__(self, *fields: str) -> None:
        self.fields = fields

    async def __call__(
        self, guild_id: Annotated[str, Path()], db: Annotated[DB, Depends(use_db)]
    ) -> Guild:
        guild = await fetchrow(
            "SELECT $1 FROM guilds WHERE id = $2;", db, self.fields, guild_id
        )

        if guild is None:
            raise Err("guild does not exist", 401)

        return guild


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


@final
class Hero:
    def __init__(self, guild: Guild, member: Member, user: User) -> None:
        self.guild = guild
        self.member = member
        self.user = user


async def get_permset(hero: Hero, db: DB) -> Permissions:
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


class UseMember:
    def __init__(self, *fields: str, guild_fields: list = []) -> None:
        self.fields = fields
        self.guild_fields = guild_fields
        self.guild_fields.append("id")

    async def __call__(
        self,
        guild_id: Annotated[str, Path()],
        db: Annotated[DB, Depends(use_db)],
        user: Annotated[
            User,
            Depends(
                UseUser(
                    "id",
                    "username",
                    "email",
                    "flags",
                    "display_name",
                    "bot",
                    "avatar",
                    "password",
                )
            ),
        ],
    ) -> Hero:
        guildish = UseGuild(*self.guild_fields)
        guild = await guildish(guild_id, db)

        member = await fetchrow(
            f"SELECT $1 FROM members WHERE guild_id = $2 AND user_id = $3",
            db,
            self.fields,
            guild["id"],
            user["id"],
        )

        return Hero(guild, member, user)


@final
class Role(TypedDict):
    id: int
    guild_id: int
    name: str
    allow: int
    deny: int
    hoist: bool
    mentionable: bool


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


@final
class ChannelMention(TypedDict):
    channel_id: int
    guild_id: int


@final
class Message(TypedDict):
    id: int
    channel_id: int
    author: NotRequired[User]
    author_id: NotRequired[int]
    content: str
    timestamp: str
    edited_timestamp: NotRequired[str | None]
    user_mentions: list[User]
    channel_mentions: list[ChannelMention]
    role_mentions: list[Role]
    mention_everyone: bool
    pinned: bool
    pinned_at: NotRequired[str | None]
    reference_id: int | None
    flags: int


@final
class ReadState(TypedDict):
    channel_id: int
    mentions: int
    last_message_id: int


@final
class MessageReaction(TypedDict):
    message_id: int
    count: int
    emoji: str
