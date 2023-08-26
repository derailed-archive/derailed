import re
from typing import Annotated

import asyncpg
import bcrypt
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field

from ..auth import create_token
from ..controllers.dbs import DB, use_db
from ..controllers.rate_limiter import UnscopedRateLimiter
from ..controllers.rpc import publish_user
from ..error import Err
from ..flags import DEFAULT_USER_FLAGS
from ..identity import make_snowflake
from ..models import User
from ..models import get_user as gusr
from ..utils import MISSING, Maybe, commit, create_update, f1, fetch

users = APIRouter(dependencies=[Depends(UnscopedRateLimiter("user", 20, 1))])


PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,100}$")
USERNAME_REGEX = re.compile(r"^[a-z0-9_.]{1,32}$")


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class ModifyUser(BaseModel):
    username: Maybe[str] = Field(MISSING)
    email: Maybe[EmailStr] = Field(MISSING)
    password: Maybe[str] = Field(MISSING)
    display_name: Maybe[str | None] = Field(MISSING, min_length=1, max_length=32)
    current_password: str = Field(min_length=8, max_length=100)


class DeleteUser(BaseModel):
    password: str = Field(min_length=8, max_length=100)


class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


@users.post("/register", status_code=201)
async def register(model: CreateUser, db: Annotated[DB, Depends(use_db)]) -> User:
    if not PASSWORD_REGEX.fullmatch(model.password):
        raise Err("password must be stronger")
    if not USERNAME_REGEX.fullmatch(model.username):
        raise Err("username is invalid")

    async with db.transaction():
        user_id = make_snowflake()

        try:
            await commit(
                "INSERT INTO users (id, username, email, password, flags, bot)"
                "VALUES ($1, $2, $3, $4, $5);",
                db,
                user_id,
                model.username,
                model.email,
                bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14)).decode(),
                int(DEFAULT_USER_FLAGS),
                False
            )
        except asyncpg.UniqueViolationError:
            raise Err("username or email already taken")

        await commit("INSERT INTO settings (user_id) VALUES ($1);", db, user_id)
        device_id = make_snowflake()
        await commit("INSERT INTO devices (id, user_id) VALUES ($1, $2);", db, device_id, user_id)

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


@users.post('/login', status_code=201)
async def login(model: Login, db: Annotated[DB, Depends(use_db)]) -> User:
    user = await f1('SELECT * FROM users WHERE email = $1;', db, model.email, t=User)

    if user is None:
        raise Err('email is not in use')

    if not bcrypt.checkpw(model.password.encode(), user['password'].encode()):
        raise Err('Invalid password', 401)

    user.pop('password')

    device_id = make_snowflake()
    await commit("INSERT INTO devices (id, user_id) VALUES ($1, $2);", db, device_id, user['id'])

    user['_token'] = create_token(user['id'], device_id)
    print(user)
    return user


@users.patch("/users/@me")
async def modify_current_user(
    model: ModifyUser,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[
        User,
        Depends(gusr),
    ],
) -> User:
    if model.password and not PASSWORD_REGEX.fullmatch(model.password):
        raise Err("password must be stronger")
    if model.username and not USERNAME_REGEX.fullmatch(model.username):
        raise Err("invalid username")

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
        item_values.append(bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14)).decode())

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
        Depends(gusr),
    ]
) -> User:
    user.pop("password")
    return user


@users.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(gusr)],
) -> User:
    user = await f1(
        "SELECT (id, username, flags, display_name, bot, avatar) FROM users WHERE id = $1;",
        db,
        user_id,
        t=User,
    )

    if user is None:
        raise Err("user does not exist", 404)

    return user


@users.post("/users/@me/delete", status_code=204)
async def delete_current_user(
    model: DeleteUser,
    db: Annotated[DB, Depends(use_db)],
    user: Annotated[User, Depends(gusr)],
):
    password_is_valid = bcrypt.checkpw(model.password.encode(), user["password"])

    if not password_is_valid:
        raise Err("incorrect password", 401)

    guilds = await fetch("SELECT id FROM guilds WHERE owner_id = $1", db, user["id"])

    if guilds != []:
        raise Err("owned guilds must be deleted first")

    async with db.transaction():
        await commit("DELETE FROM users WHERE id = $1", db, user["id"])
        await commit("DELETE FROM member_assigned_roles WHERE user_id = $1", db, user["id"])
