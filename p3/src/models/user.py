#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

from tortoise import Model, fields

from .flags import ActivityTypes


class User(Model):
    __field_comp__ = {
        "public": [
            "id",
            "display_name",
            "username",
            "disabled",
            "bio",
            "flags",
            "system_flags",
        ],
        "private": [
            "id",
            "display_name",
            "username",
            "disabled",
            "bio",
            "flags",
            "system_flags",
            "email",
        ],
    }

    id = fields.BigIntField(pk=True)
    display_name = fields.TextField(null=True, default=None)
    username = fields.TextField(unique=True, index=True)
    email = fields.TextField(unique=True)
    disabled = fields.BooleanField(default=False)
    password = fields.BinaryField()
    bio = fields.TextField(default="")
    flags = fields.IntField(default=3)
    system_flags = fields.IntField(default=0)


class Settings(Model):
    __field_comp__ = ["user_id", "theme"]

    user_id = fields.ForeignKeyField("models.User", "id")
    theme = fields.TextField(default="dark")


class Activity(Model):
    __field_comp__ = ["id", "user_id", "type", "content", "created_at"]

    id = fields.BigIntField(pk=True)
    user_id = fields.ForeignKeyField("models.User", "id")
    type = fields.IntEnumField(ActivityTypes)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now=True)
