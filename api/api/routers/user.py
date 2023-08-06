from typing import Annotated

import asyncpg
import bcrypt
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from ..auth import create_token
from ..controllers.dbs import DB, use_db
from ..controllers.rate_limiter import UnscopedRateLimiter
from ..controllers.rpc import publish_user
from ..eludris.flags import DEFAULT_USER_FLAGS
from ..eludris.models import User, UseUser
from ..error import Err
from ..identity import make_snowflake
from ..utils import MISSING, Maybe, commit, create_update, fetch, fetchrow

users = APIRouter(dependencies=[Depends(UnscopedRateLimiter("guild", 20, 1))])


class CreateUser(BaseModel):
    username: str = Field(regex=r"^[a-z0-9_.]+$", min_length=1, max_length=32)
    email: EmailStr
    password: str = Field(regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,100}$")


class ModifyUser(BaseModel):
    username: Maybe[str] = Field(
        MISSING, regex=r"^[a-z0-9_.]+$", min_length=1, max_length=32
    )
    email: Maybe[EmailStr] = Field(MISSING)
    password: Maybe[str] = Field(
        MISSING, regex=r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,100}$"
    )
    display_name: Maybe[str | None] = Field(MISSING, min_length=1, max_length=32)
    current_password: str = Field(min_length=8, max_length=100)


class DeleteUser(BaseModel):
    password: str = Field(min_length=8, max_length=100)


@users.post("/register", include_in_schema=False, status_code=201)
async def register(model: CreateUser, db: Annotated[DB, Depends(use_db)]) -> User:
    trans = db.transaction()
    await trans.start()

    user_id = make_snowflake()

    try:
        await commit(
            "INSERT INTO users (id, username, email, password, flags)"
            "VALUES ($1, $2, $3, $4, $5);",
            db,
            user_id,
            model.username,
            model.email,
            bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14)),
            int(DEFAULT_USER_FLAGS),
        )
    except asyncpg.UniqueViolationError:
        raise Err("username or email already taken")

    await commit("INSERT INTO settings (user_id) VALUES ($1);", db, user_id)

    await trans.commit()

    return {
        "id": user_id,
        "username": model.username,
        "email": model.email,
        "flags": int(DEFAULT_USER_FLAGS),
        "display_name": None,
        "bot": False,
        "avatar": None,
        "_token": create_token(user_id),
    }


@users.patch("/users/@me")
async def modify_current_user(
    model: ModifyUser,
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
) -> User:
    changed_items = []
    item_values = []

    password_is_valid = bcrypt.checkpw(
        model.current_password.encode(), user["password"]
    )

    if not password_is_valid:
        raise Err("incorrect password", 401)

    user.pop("password")

    if model.username:
        changed_items.append("username")
        item_values.append(model.username)
        user["username"] = model.username

    if model.email:
        changed_items.append("email")
        item_values.append(model.email)
        user["email"] = model.email

    if model.password:
        changed_items.append("password")
        item_values.append(bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14)))

    if model.display_name:
        changed_items.append("display_name")
        item_values.append(model.display_name)
        user["display_name"] = model.display_name

    await commit(
        create_update("users", 1, changed_items) + "WHERE id = $1",
        db,
        user["id"],
        *item_values
    )

    await publish_user(user["id"], "USER_UPDATE", user)

    return user


@users.get("/users/@me")
async def get_current_user(
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
            )
        ),
    ]
) -> User:
    return user


@users.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Annotated[DB, Depends(use_db)],
    _user: Annotated[User, Depends(UseUser("id"))],
) -> User:
    user = await fetchrow(
        "SELECT (id, username, flags, display_name, bot, avatar) FROM users WHERE id = $1;",
        db,
        user_id,
    )

    if user is None:
        raise Err("user does not exist", 404)

    return user


@users.delete("/users/@me")
async def delete_current_user(
    model: DeleteUser,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(UseUser("id", "password"))],
) -> str:
    password_is_valid = bcrypt.checkpw(
        model.current_password.encode(), user["password"]
    )

    if not password_is_valid:
        raise Err("incorrect password", 401)

    await fetch("DELETE FROM users WHERE id = $1;", db, user["id"])

    return ""
