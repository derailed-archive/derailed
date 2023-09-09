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
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.Text(), index=True, unique=True, nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True, default=None),
        sa.Column("avatar", sa.Text(), nullable=True, default=None),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("flags", sa.BIGINT, nullable=False),
        sa.Column("bot", sa.Boolean(), nullable=False, default=False),
        sa.Column("system", sa.Boolean(), nullable=False, default=False)
    )
    op.create_table(
        "settings",
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("theme", sa.Text(), default="dark", nullable=False),
        sa.Column("status", sa.Integer(), default=1, nullable=False),
    )
    op.create_table(
        "guilds",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("icon", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.BigInteger(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column("system_channel_id", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.Text(), default="community", nullable=False),
        sa.Column("max_members", sa.Integer(), default=1000, nullable=False),
        sa.Column("permissions", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "guild_features",
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("feature", sa.Text(), primary_key=True),
    )

    op.create_table(
        "guild_members",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("nick", sa.Text(), nullable=True),
        sa.Column("joined_at", sa.TIMESTAMP, nullable=False),
        sa.Column("deaf", sa.Boolean(), nullable=False),
        sa.Column("mute", sa.Boolean(), nullable=False),
    )
    op.create_table(
        "member_assigned_roles",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("role_id", sa.BigInteger(), primary_key=True),
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("allow", sa.BigInteger(), nullable=False),
        sa.Column("deny", sa.BigInteger(), nullable=False),
        sa.Column("hoist", sa.Boolean(), default=False, nullable=False),
        sa.Column("mentionable", sa.Boolean(), default=False, nullable=False),
    )
    op.create_table(
        "guild_folders",
        sa.Column("id", sa.BigInteger(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
    )
    op.create_table(
        "guild_slots",
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "folder_id",
            sa.BigInteger(),
            sa.ForeignKey("guild_folders.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("type", sa.Integer(), nullable=False),
        sa.Column(
            "guild_id",
            sa.BigInteger(),
            sa.ForeignKey("guilds.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("topic", sa.Text(), nullable=True),
        # relations are shit. hence why I don't have a girlfriend :(
        sa.Column("last_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "parent_id",
            sa.BigInteger(),
            sa.ForeignKey("channels.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("sync_parent_permissions", sa.Boolean(), default=False, nullable=True),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "channel_id",
            sa.BigInteger(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            index=True,
            nullable=False
        ),
        sa.Column(
            "author_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.TIMESTAMP, nullable=False),
        sa.Column("edited_timestamp", sa.TIMESTAMP, nullable=True),
        sa.Column("mention_everyone", sa.Boolean(), nullable=False),
        sa.Column("pinned", sa.Boolean(), nullable=False),
        sa.Column("pinned_at", sa.TIMESTAMP, nullable=True),
        sa.Column("referenced_message_id", sa.BigInteger(), nullable=True),
        sa.Column("flags", sa.BigInteger(), nullable=False, default=0),
    )
    op.create_table(
        "message_channel_mentions",
        sa.Column("channel_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "message_id",
            sa.BigInteger(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "message_user_mentions",
        sa.Column("user_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "message_id",
            sa.BigInteger(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "message_role_mentions",
        sa.Column("role_id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "message_id",
            sa.BigInteger(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "read_states",
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "channel_id",
            sa.BigInteger(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("mentions", sa.BigInteger(), nullable=False),
        sa.Column("last_message_id", sa.BigInteger(), nullable=True),
    )
    op.create_table(
        "permission_overwrites",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "channel_id",
            sa.BigInteger(),
            sa.ForeignKey("channels.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("type", sa.Integer(), nullable=False),
        sa.Column("allow", sa.BigInteger(), nullable=False),
        sa.Column("deny", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "message_reactions",
        sa.Column(
            "message_id",
            sa.BigInteger(),
            sa.ForeignKey("messages.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("emoji", sa.Text(), primary_key=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False),
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
