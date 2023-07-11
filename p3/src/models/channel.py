#
# SPDX: CPAL-1.0
#
# Copyright 2021-2023 Derailed. All rights reserved.
#

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
