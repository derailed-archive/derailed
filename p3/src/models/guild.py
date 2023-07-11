#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

from tortoise import Model, fields


class Guild(Model):
    __field_comp__ = ["id", "name", "owner_id", "flags", "default_permissions"]

    id = fields.BigIntField(pk=True)
    name = fields.TextField()
    owner_id = fields.ForeignKeyField("models.User", "id", on_delete=fields.RESTRICT)
    flags = fields.IntField(default=0)
    default_permissions = fields.BigIntField()


class Invite(Model):
    __field_comp__ = ["id", "guild_id", "created_at", "author_id"]

    id = fields.TextField(pk=True)
    guild_id = fields.ForeignKeyField("models.Guild", "id")
    created_at = fields.DatetimeField(auto_now_add=True)
    author_id = fields.ForeignKeyField("models.User", "id")


class Member(Model):
    __field_comp__ = ["guild_id", "user_id", "nick", "joined_at"]

    guild_id = fields.ForeignKeyField("models.Guild", "id", pk=True)
    user_id = fields.ForeignKeyField("models.User", "id", pk=True)
    nick = fields.TextField()
    joined_at = fields.DatetimeField(auto_now_add=True)


class RoleAssign(Model):
    __field_comp__ = ["guild_id", "user_id", "role_id"]

    guild_id = fields.ForeignKeyField("models.Guild", "id", pk=True)
    user_id = fields.ForeignKeyField("models.User", "id", pk=True)
    role_id = fields.ForeignKeyField("models.Role", "id")


class Role(Model):
    __field_comp__ = ["id", "guild_id", "name", "allow", "disallow", "position"]

    id = fields.BigIntField(pk=True)
    guild_id = fields.ForeignKeyField("models.Guild", "id", pk=True)
    name = fields.TextField()
    allow = fields.BigIntField()
    disallow = fields.BigIntField()
    position = fields.IntField()
