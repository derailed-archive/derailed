#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

from datetime import datetime
from enum import IntEnum, IntFlag
from typing import Any

from tortoise import Model


class UserFlags(IntFlag):
    staff = 0
    admin = 1
    verified = 2
    early_supporter = 3


class SystemFlags(IntFlag):
    bot = 0
    system = 1


class ChannelTypes(IntEnum):
    TEXT_CHANNEL = 0
    CATEGORY_CHANNEL = 1


class ActivityTypes(IntEnum):
    CUSTOM_STATUS = 0


def to_dict(model: Model, filter: str | None = None, **filters: str) -> dict[str, Any]:
    d = dir(model)
    obj = {}

    for o in d:
        obj[o] = getattr(model, o)

    real_mapping = {}

    if filter:
        lookout = model.__field_comp__[filter]
    else:
        lookout = model.__field_comp__

    for name in lookout:
        object = obj[name]

        real_mapping[name] = object

        if isinstance(object, int):
            if object > 2_147_483_647:
                real_mapping[name] = str(object)
        elif isinstance(object, datetime):
            real_mapping[name] = object.isoformat()
        elif isinstance(object, Model):
            real_mapping[name] = to_dict(object, filters.get(name))
        elif isinstance(object, IntEnum):
            real_mapping[name] = int(object)

    return real_mapping
