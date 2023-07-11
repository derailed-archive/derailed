#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#


from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends
from models.authentication import create_token
from models.error import Err
from models.flags import to_dict
from models.sf import snowflake
from models.user import Settings, User
from pydantic import BaseModel, EmailStr, Field

from ..dependency.get_user import get_user
from ..missing import MISSING, Maybe

router = APIRouter(prefix="/users")


class CreateUser(BaseModel):
    username: str = Field(regex=r"^[a-z0-9_.]+$", min_length=1, max_length=32)
    email: EmailStr
    password: str = Field(
        regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])(?!.*\s).{8,}$"
    )


class ModifyUser(BaseModel):
    username: Maybe[str] = Field(
        MISSING, regex=r"^[a-z0-9_.]+$", min_length=1, max_length=32
    )
    email: Maybe[EmailStr] = MISSING
    password: Maybe[str] = Field(
        MISSING,
        regex=r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()])(?!.*\s).{8,}$",
        max_length=120,
    )
    old_password: str = Field(max_length=120)


class DeleteUser(BaseModel):
    password: str = Field(max_length=120)


@router.post("/register")
async def register(model: CreateUser):
    try:
        user = await User.create(
            id=next(snowflake),
            username=model.username,
            email=model.email,
            password=bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14)),
        )
    # TODO: specify exception
    except:
        raise Err("username or email already used")

    await Settings.create(id=user.id)

    data = to_dict(user, "private")
    data["_token"] = create_token(user.id)
    return data


@router.get("/@me")
async def get_current_user(user: Annotated[User, Depends(get_user)]):
    return to_dict(user, "private")


@router.patch("/@me")
async def modify_current_user(
    model: ModifyUser, user: Annotated[User, Depends(get_user)]
):
    valid = bcrypt.checkpw(model.old_password.encode(), user.password)

    if not valid:
        raise Err("incorrect password")

    user.username = model.username or user.username
    user.email = model.email or user.email

    if model.password:
        enc = bcrypt.hashpw(model.password.encode(), bcrypt.gensalt(14))

        user.password = enc

    await user.save()

    return to_dict(user, "private")


@router.delete("/@me", status_code=204)
async def delete_current_user(
    model: DeleteUser, user: Annotated[User, Depends(get_user)]
):
    valid = bcrypt.checkpw(model.password.encode(), user.password)

    if not valid:
        raise Err("incorrect password")

    try:
        await user.delete()
    except:
        raise Err("restricted relation kept, must be removed first")

    return ""
