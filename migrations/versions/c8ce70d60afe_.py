"""The initial Derailed database migration.

Revision ID: c8ce70d60afe
Revises: everything?
Create Date: 2023-08-17 17:51:15.161592
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8ce70d60afe"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("username", sa.Text(), index=True, unique=True),
        sa.Column("display_name", sa.Text(), nullable=True, default=None),
        sa.Column("avatar", sa.Text(), nullable=True, default=None),
        sa.Column("email", sa.Text(), unique=True, index=True),
        sa.Column("password", sa.Text()),
        sa.Column("flags", sa.BIGINT),
        sa.Column("bot", sa.Boolean(), default=False),
    )
    op.create_table(
        "settings",
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("theme", sa.Text(), default="dark"),
        sa.Column("status", sa.Integer(), default=1),
    )
    op.create_table(
        "guilds",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text()),
        sa.Column("icon", sa.Text()),
        sa.Column("owner_id", sa.Text()),
        sa.Column("system_channel_id", sa.Text()),
        sa.Column("type", sa.Text(), default="community"),
        sa.Column("max_members", sa.Integer(), default=1000),
        sa.Column("permissions", sa.BigInteger()),
    )
    op.create_table(
        "guild_features",
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("feature", sa.Text(), primary_key=True),
    )

    op.create_table(
        "guild_members",
        sa.Column("user_id", sa.Text(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("nick", sa.Text()),
        sa.Column("joined_at", sa.TIMESTAMP),
        sa.Column("deaf", sa.Boolean()),
        sa.Column("mute", sa.Boolean()),
    )
    op.create_table(
        "member_assigned_roles",
        sa.Column("user_id", sa.Text(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("role_id", sa.Text(), primary_key=True),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
        ),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column("name", sa.Text()),
        sa.Column("allow", sa.BigInteger()),
        sa.Column("deny", sa.BigInteger()),
        sa.Column("hoist", sa.Boolean(), default=False),
        sa.Column("mentionable", sa.Boolean(), default=False),
    )
    op.create_table(
        "guild_folders",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("user_id", sa.Text(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("name", sa.Text()),
    )
    op.create_table(
        "guild_slots",
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "folder_id",
            sa.Text(),
            sa.ForeignKey("guild_folders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("position", sa.Integer()),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("type", sa.Integer()),
        sa.Column(
            "guild_id",
            sa.Text(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("topic", sa.Text(), nullable=True),
        sa.Column("last_message_id", sa.Text(), nullable=True),
        sa.Column(
            "parent_id",
            sa.Text(),
            sa.ForeignKey("channels.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sync_parent_permissions", sa.Boolean(), default=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "channel_id",
            sa.Text(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            index=True,
        ),
        sa.Column(
            "author_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("content", sa.Text()),
        sa.Column("timestamp", sa.TIMESTAMP),
        sa.Column("edited_timestamp", sa.TIMESTAMP, nullable=True),
        sa.Column("mention_everyone", sa.Boolean()),
        sa.Column("pinned", sa.Boolean()),
        sa.Column("pinned_at", sa.TIMESTAMP, nullable=True),
        sa.Column("referenced_message_id", sa.Text(), nullable=True),
        sa.Column("flags", sa.BigInteger()),
    )
    op.create_table(
        "message_channel_mentions",
        sa.Column("channel_id", sa.Text(), primary_key=True),
        sa.Column(
            "message_id",
            sa.Text(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "message_user_mentions",
        sa.Column("user_id", sa.Text(), primary_key=True),
        sa.Column(
            "message_id",
            sa.Text(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "message_role_mentions",
        sa.Column("role_id", sa.Text(), primary_key=True),
        sa.Column(
            "message_id",
            sa.Text(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "read_states",
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "channel_id",
            sa.Text(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("mentions", sa.BigInteger()),
        sa.Column("last_message_id", sa.Text()),
    )
    op.create_table(
        "permission_overwrites",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column(
            "channel_id",
            sa.Text(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("type", sa.Integer()),
        sa.Column("allow", sa.BigInteger()),
        sa.Column("deny", sa.BigInteger()),
    )
    op.create_table(
        "message_reactions",
        sa.Column(
            "message_id",
            sa.Text(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.Text(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("emoji", sa.Text(), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("settings")
    op.drop_table("guilds")
    op.drop_table("guild_features")
    op.drop_table("guild_members")
    op.drop_table("member_assigned_roles")
    op.drop_table("devices")
    op.drop_table("roles")
    op.drop_table("guild_folders")
    op.drop_table("guild_slots")
    op.drop_table("channels")
    op.drop_table("messages")
    op.drop_table("message_channel_mentions")
    op.drop_table("message_user_mentions")
    op.drop_table("message_role_mentions")
    op.drop_table("read_states")
    op.drop_table("permission_overwrites")
    op.drop_table("message_reactions")
