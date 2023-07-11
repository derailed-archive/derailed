#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#


from typing import Annotated

from fastapi import Path
from models.authentication import from_token
from models.user import User


async def get_user(token: Annotated[str, Path(alias="authorization")]) -> User:
    return await from_token(token)
