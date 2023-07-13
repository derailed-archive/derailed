# Copyright (C) 2021-2023 Derailed
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
