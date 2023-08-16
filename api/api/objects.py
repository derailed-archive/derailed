# NOTE this is not supported, nor used in the API. But is is nice as a DB reference for now,
# so I'm keeping it.


from __future__ import annotations
from datetime import datetime
import os
from typing import Literal
import databases
import ormar
import sqlalchemy
from .flags import ChannelTypes, MessageFlags, OverwriteType, Permissions, Status, Theme, UserFlags


database = databases.Database(os.environ['DB_URL'])
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: str = ormar.Text(primary_key=True)
    username: str = ormar.Text(index=True, unique=True)
    display_name: str = ormar.Text(nullable=True)
    avatar: str = ormar.Text(nullable=True)
    email: str = ormar.Text(unique=True, nullable=True, index=True)
    password: str = ormar.Text()
    flags: UserFlags = ormar.Enum(UserFlags)
    bot: bool = ormar.Boolean()
    _token: str = ormar.Text(pydantic_only=True)


class GuildFolder(ormar.Model):
    id: str = ormar.Text(primary_key=True)
    name: str = ormar.Text(nullable=True)
    user_id: str = ormar.Text(index=True)

    # slots
    slots: list[GuildSlot] = ormar.BaseField(pydantic_only=True)


class GuildSlot(ormar.Model):
    folder_id: str = ormar.Text(primary_key=True)
    guild_id: str = ormar.Text(primary_key=True)
    user_id: str = ormar.Text()


class Settings(ormar.Model):
    class Meta(BaseMeta):
        tablename = "user_settings"

    user_id: str = ormar.Text(primary_key=True)
    theme: Theme = ormar.Enum(Theme, default=Theme.DARK)
    status: Status = ormar.Enum(Status, default=Status.ONLINE)

    # guild-folder related
    guild_folders: list[GuildFolder] = ormar.BaseField(pydantic_only=True)


class Guild(ormar.Model):
    class Meta(BaseMeta):
        tablename = "guilds"

    id: str = ormar.Text()
    name: str = ormar.Text()
    icon: str = ormar.Text(nullable=True, default=None)
    owner_id: str = ormar.Text()
    features: list[str] = ormar.Text(pydantic_only=True)
    system_channel_id: str = ormar.Text(nullable=True)
    type: Literal["nsfw", "community"] = ormar.Text(default="community")
    max_members: int = ormar.Integer()
    permissions: int = ormar.BigInteger(minimum=0)

    # guild preview
    available: bool = ormar.Boolean(pydantic_only=True)
    presences: bool = ormar.Boolean(pydantic_only=True)

    # GUILD_CREATE - GUILD_JOIN
    channels: list[Channel] = ormar.BaseField(pydantic_only=True)
    roles: list[Role] = ormar.BaseField(pydantic_only=True)


class Member(ormar.Model):
    class Meta(BaseMeta):
        tablename = "guild_members"

    user_id: str = ormar.Text(primary_key=True)
    guild_id: str = ormar.Text(primary_key=True)
    nick: str = ormar.Text(nullable=True, default=None)
    joined_at: datetime = ormar.DateTime()
    deaf: bool = ormar.Boolean(default=False)
    mute: bool = ormar.Boolean(default=False)
    roles: list[int] = ormar.BaseField(pydantic_only=True)


class RoleAssign(ormar.Model):
    class Meta(BaseMeta):
        tablename = "member_assigned_roles"

    role_id: str = ormar.Text(primary_key=True)
    user_id: str = ormar.Text(primary_key=True)
    guild_id: str = ormar.Text()


class Device(ormar.Model):
    class Meta(BaseMeta):
        tablename = "devices"

    id: str = ormar.Text(primary_key=True)
    user_id: str = ormar.Text()


class Role(ormar.Model):
    class Meta(BaseMeta):
        tablename = "roles"

    id: str = ormar.Text(primary_key=True)
    guild_id: str = ormar.Text(index=True)
    name: str = ormar.Text()
    allow: Permissions = ormar.Enum(Permissions)
    deny: Permissions = ormar.Enum(Permissions)
    hoist: bool = ormar.Boolean(default=False)
    mentionable: bool = ormar.Boolean(default=False)


class PermissionOverwrites(ormar.Model):
    class Meta(BaseMeta):
        tablename = "permission_overwrites"

    id: str = ormar.Text(primary_key=True)
    channel_id: str = ormar.Text(primary_key=True)
    type: OverwriteType = ormar.Enum(OverwriteType)
    allow: int = ormar.Integer(minimum=0)
    deny: int = ormar.Integer(minimum=0)


class Channel(ormar.Model):
    class Meta(BaseMeta):
        tablename = "channels"

    id: str = ormar.Text(primary_key=True)
    type: ChannelTypes = ormar.Enum(ChannelTypes)
    guild_id: str = ormar.Text(index=True, nullable=True)
    name: str = ormar.Text(nullable=True)
    position: int = ormar.Integer(minimum=0, maximum=500)
    topic: str = ormar.Text(nullable=True)
    last_message_id: str = ormar.Text(nullable=True)
    parent_id: str = ormar.Text(nullable=True)


class Message(ormar.Model):
    class Meta(BaseMeta):
        tablename = "messages"

    id: str = ormar.Text(primary_key=True)
    channel_id: str = ormar.Text(index=True)
    author_id: str = ormar.Text()
    content: str = ormar.Text()
    timestamp: datetime = ormar.DateTime()
    edited_timestamp: datetime = ormar.DateTime(nullable=True)
    mention_everyone: bool = ormar.Boolean(default=True)
    pinned: bool = ormar.Boolean(default=False)
    pinned_at: datetime = ormar.DateTime(nullable=True, default=None)
    referenced_message_id: str = ormar.Text(nullable=True)
    flags: MessageFlags = ormar.Enum(MessageFlags)


class ChannelMention(ormar.Model):
    class Meta(BaseMeta):
        tablename = "channel_mentions"

    message_id: str = ormar.Text(primary_key=True)
    channel_id: str = ormar.Text(primary_key=True)

    # extra
    name: str = ormar.Text(pydantic_only=True)


class UserMention(ormar.Model):
    class Meta(BaseMeta):
        tablename = "user_mentions"

    message_id: str = ormar.Text(primary_key=True)
    user_id: str = ormar.Text(primary_key=True)

    # extra
    user: User = ormar.BaseField(pydantic_only=True)


class ReadState(ormar.Model):
    class Meta(BaseMeta):
        tablename = "read_states"

    user_id: str = ormar.Text(primary_key=True)
    channel_id: str = ormar.Text(primary_key=True)
    mentions: int = ormar.BigInteger()
    last_message_id: str = ormar.Text()


class MessageReaction(ormar.Model):
    class Meta(BaseMeta):
        tablename = "message_reactions"

    message_id: int
    user_id: int
    bucket_id: int
    created_at: str
    emoji: str
