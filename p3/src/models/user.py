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
