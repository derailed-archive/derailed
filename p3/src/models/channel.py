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

from .flags import ChannelTypes


class Channel(Model):
    # TODO: subjugate based on channel type
    __field_comp__ = [
        "id",
        "guild_id",
        "name",
        "type",
        "last_message_id",
        "parent_id",
        "position",
    ]

    id = fields.BigIntField(pk=True)
    guild_id = fields.ForeignKeyField("models.Guild", "id", null=True)
    name = fields.TextField(null=True)
    type = fields.IntEnumField(ChannelTypes)
    last_message_id = fields.ForeignKeyField(
        "models.Message", "id", null=True, default=None, on_delete=fields.SET_NULL
    )
    parent_id = fields.ForeignKeyField(
        "models.Channel", "id", null=True, default=None, on_delete=fields.SET_NULL
    )
    position = fields.IntField(null=True)


class ReadState(Model):
    __field_comp__ = ["user_id", "channel_id", "last_message_id", "mentions"]

    user_id = fields.ForeignKeyField("models.User", "id", pk=True)
    channel_id = fields.ForeignKeyField("models.Channel", "id", pk=True)
    last_message_id = fields.ForeignKeyField(
        "models.Message", "id", null=True, default=None, on_delete=fields.SET_NULL
    )
    mentions = fields.IntField()


class Message(Model):
    __field_comp__ = [
        "id",
        "channel_id",
        "content",
        "author_id",
        "timestamp",
        "edited_timestamp",
    ]

    id = fields.BigIntField(pk=True)
    channel_id = fields.ForeignKeyField("models.Channel", "id", index=True)
    content = fields.TextField()
    author_id = fields.ForeignKeyField("models.User", "id")
    timestamp = fields.DatetimeField(auto_now_add=True)
    edited_timestamp = fields.DatetimeField(auto_now=True)
    referenced_message_id = fields.ForeignKeyField("models.Message", "id", null=True, on_delete=fields.SET_DEFAULT, default=0)
