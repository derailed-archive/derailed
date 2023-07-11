#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

import os
from datetime import datetime
from typing import TypedDict

import jwt

from .error import Err
from .sf import snowflake
from .user import User

secret = os.environ["TOKEN_SECRET"]


class Token(TypedDict):
    user_id: int
    token_id: int
    created_at: str


def verify_token(token: str) -> Token:
    try:
        token: Token = jwt.decode(token, secret, ["HS256"])
    except jwt.DecodeError:
        raise Err("token is invalid", 401)

    return token


def create_token(user_id: int) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "token_id": hex(next(snowflake)),
            "created_at": datetime.utcnow().isoformat(),
        },
        secret,
    )


async def from_token(token: str) -> User:
    contents = verify_token(token)

    user_id = contents["user_id"]

    user = await User.get_or_none(id=user_id)

    if user is None or user.disabled is True:
        raise Err("invalid or expired token")

    return user
