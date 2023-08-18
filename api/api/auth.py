import os
from typing import Any, TypedDict, cast

import jwt

from .error import Err
from .identity import make_snowflake
from .utils import now


class Token(TypedDict):
    user_id: int
    token_id: int
    created_at: str
    device_id: int


def verify_token(token: str) -> Token:
    try:
        ret_token: dict[str, Any] = jwt.decode(token, os.environ['TOKEN_SECRET'], ["HS256"])
    except jwt.DecodeError:
        raise Err("token invalid", 401)

    return cast(Token, ret_token)


def create_token(user_id: int) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "token_id": make_snowflake(),
            "created_at": now().isoformat(),
        },
        os.environ['TOKEN_SECRET'],
    )
