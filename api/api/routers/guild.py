import random
from typing import Annotated, Literal

import bcrypt
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..controllers.dbs import DB, use_db
from ..controllers.rate_limiter import ScopedRateLimiter, UnscopedRateLimiter
from ..controllers.rpc import publish_guild, publish_user
from ..error import Err
from ..flags import ChannelTypes, MessageFlags
from ..identity import make_snowflake
from ..models import Guild, Member, Message, User
from ..models import get_guild as ggui
from ..models import get_member, get_permissions
from ..models import get_user as gusr
from ..utils import MISSING, Maybe, commit, create_update, f1, now

guilds = APIRouter(dependencies=[Depends(UnscopedRateLimiter("guild", 20, 1))])


# TODO? move to a new file possibly.
WELCOME_MESSAGES = [
    "Welcome <@{user_id}>! Make sure to bake us some yummy pasta!",
    "It's a bird, it's a plane! It's a wild <@{user_id}>",
]


class CreateGuild(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    type: Literal["nsfw", "community"] = "community"


class ModifyGuild(BaseModel):
    permissions: Maybe[int] = MISSING
    name: Maybe[str] = Field(MISSING, min_length=1, max_length=32)
    # TODO!: This requires needing to send a password.
    # owner_id
    system_channel_id: Maybe[int] = MISSING


class DeleteGuild(BaseModel):
    password: str = Field(min_length=8, max_length=100)


@guilds.get("/guilds/{guild_id}", dependencies=[Depends(ScopedRateLimiter())])
async def get_guild(
    guild: Annotated[Guild, ggui], member: Annotated[Member, get_member]
) -> Guild:
    return guild


@guilds.post(
    "/guilds", dependencies=[Depends(ScopedRateLimiter(2, 120))], status_code=201
)
async def create_guild(
    model: CreateGuild,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(gusr)],
) -> Guild:
    async with db.transaction():
        guild_id = make_snowflake()

        await commit(
            "INSERT INTO guilds (id, name, type) VALUES ($1, $2, $3);",
            db,
            guild_id,
            model.name,
            model.type,
        )

        joined_at = now().isoformat()

        await commit(
            "INSERT INTO members (user_id, guild_id, joined_at) VALUES ($1, $2, $3);",
            db,
            user["id"],
            guild_id,
            joined_at,
        )

        # generate 3 ids for category, text channel, and welcome message
        category_id, channel_id, message_id = (
            make_snowflake(),
            make_snowflake(),
            make_snowflake(),
        )

        create_channel = await db.prepare(
            "INSERT INTO channels (id, type, guild_id, name, position, parent_id, last_message_id)"
            "VALUES ($1, $2, $3, $4, $5, $6, $7)"
        )

        await create_channel.executemany(
            # category
            (
                category_id,
                int(ChannelTypes.CATEGORY_CHANNEL),
                guild_id,
                "General",
                0,
                None,
                None,
            ),
            # text channel
            (
                channel_id,
                int(ChannelTypes.TEXT_CHANNEL),
                guild_id,
                "general",
                0,
                category_id,
                message_id,
            ),
        )
        message_created = now().isoformat()
        content = random.choice(WELCOME_MESSAGES)

        await commit(
            "INSERT INTO messages (id, channel_id, author_id, flags, content, timestamp) "
            "VALUES ($1, $2, $3, $4, $5, $6);",
            db,
            message_id,
            channel_id,
            user["id"],
            int(MessageFlags.WELCOME_MESSAGE),
            content,
            message_created,
        )

        if not user["bot"]:
            pos = await f1(
                "SELECT max(position) + 1 FROM guild_slots WHERE user_id = $1 AND folder_id = $2;",
                db,
                user["id"],
                None,
            )

            await commit(
                "INSERT INTO guild_slots (user_id, folder_id, position, guild_id) VALUES ($1, $2, $3, $4)",
                db,
                user["id"],
                None,
                pos,
                guild_id,
            )

        guild: Guild = {
            "id": guild_id,
            "permissions": 0,
            "features": [],
            "name": model.name,
            "icon": None,
            "max_members": 1000,
            "owner_id": user["id"],
            "system_channel_id": channel_id,
            "type": model.type,
            "member": {
                "user_id": user["id"],
                "guild_id": guild_id,
                "deaf": False,
                "joined_at": joined_at,
                "mute": False,
                "nick": None,
            },
            "channels": [
                # category
                {
                    "id": category_id,
                    "guild_id": guild_id,
                    "name": "General",
                    "parent_id": None,
                    "position": 0,
                    "topic": None,
                    "type": int(ChannelTypes.CATEGORY_CHANNEL),
                },
                # channel
                {
                    "id": channel_id,
                    "guild_id": guild_id,
                    "name": "general",
                    "last_message_id": message_id,
                    "parent_id": category_id,
                    "position": 0,
                    "topic": None,
                    "type": int(ChannelTypes.TEXT_CHANNEL),
                },
            ],
            "roles": [],
        }
        message: Message = {
            "id": message_id,
            "author_id": user["id"],
            "flags": int(MessageFlags.WELCOME_MESSAGE),
            "channel_id": channel_id,
            "channel_mentions": [],
            "content": content,
            "edited_timestamp": None,
            "mention_everyone": False,
            "pinned": False,
            "pinned_at": None,
            "referenced_message_id": None,
            "role_mentions": [],
            "timestamp": message_created,
            "channel_mentions": [],
            "user_mentions": [],
        }

        await publish_user(user["id"], "GUILD_CREATE", guild)
        await publish_user(user["id"], "MESSAGE_CREATE", message)

        return guild


@guilds.patch("/guilds/{guild_id}", dependencies=[Depends(ScopedRateLimiter())])
async def modify_guild(
    model: ModifyGuild,
    db: Annotated[DB, Depends(use_db)],
    guild: Annotated[DB, Depends(ggui)],
    permissions: Annotated[DB, Depends(get_permissions)],
) -> Guild:
    if not permissions.MANAGE_GUILD:
        raise Err("invalid permissions", 403)

    changed_fields = []
    field_values = []

    if model.name:
        guild["name"] = model.name
        changed_fields.append("name")
        field_values.append(model.name)

    if model.permissions:
        guild["permissions"] = model.permissions
        changed_fields.append("permissions")
        field_values.append(model.permissions)

    if model.system_channel_id:
        row = await f1(
            "SELECT (id) FROM channels WHERE id = $1 AND type = $2;",
            db,
            model.system_channel_id,
            int(ChannelTypes.TEXT_CHANNEL),
        )

        if row is None:
            raise Err("system_channel_id is not a valid text channel")

        guild["system_channel_id"] = model.system_channel_id
        changed_fields.append("system_channel_id")
        field_values.append(model.system_channel_id)

    await commit(
        create_update("guilds", 1, changed_fields) + "WHERE id = $1",
        db,
        guild["id"],
        *field_values
    )

    await publish_guild(guild["id"], "GUILD_UPDATE", guild)

    return guild


@guilds.delete("/guilds/{guild_id}", dependencies=[Depends(ScopedRateLimiter(5, 120))])
async def delete_guild(
    model: DeleteGuild,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(gusr)],
    guild: Annotated[Guild, Depends(ggui)],
) -> Guild:
    if user["id"] != guild["owner_id"]:
        raise Err("you must be owner to delete a guild", 403)

    valid_pswd = bcrypt.checkpw(model.password.encode(), user["password"].encode())

    if not valid_pswd:
        raise Err("incorrect password", 403)

    trans = db.transaction()
    await trans.start()

    # these don't have foreign keys directly.
    await commit("DELETE FROM guilds WHERE id = $1", db, guild["id"])

    await trans.commit()

    return ""
