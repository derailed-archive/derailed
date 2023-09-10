-- The Initial Derailed Migrations script.
-- This adds the most basic tables and indexes from Derailed.
CREATE TABLE IF NOT EXISTS users (
    id BIGINT NOT NULL PRIMARY KEY,
    username VARCHAR(32) UNIQUE NOT NULL,
    display_name VARCHAR(2048) DEFAULT NULL,
    avatar TEXT DEFAULT NULL,
    password TEXT NOT NULL,
    flags BIGINT NOT NULL,
    bot BOOLEAN NOT NULL,
    system BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS user_settings (
    user_id BIGINT PRIMARY KEY,
    theme TEXT NOT NULL,
    status INT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS devices (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    icon TEXT NOT NULL,
    owner_id BIGINT NOT NULL,
    type TEXT NOT NULL,
    max_members INT NOT NULL DEFAULT 1000,
    permissions BIGINT NOT NULL,
    FOREIGN KEY (owner_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS guild_features (
    id BIGINT NOT NULL,
    feature TEXT NOT NULL,
    PRIMARY KEY (id, feature),
    FOREIGN KEY (id)
        REFERENCES guilds (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS guild_members (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    nick VARCHAR(32),
    joined_at TIMESTAMP NOT NULL,
    deaf BOOLEAN NOT NULL,
    mute BOOLEAN NOT NULL,
    PRIMARY KEY (user_id, guild_id),
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS roles (
    id BIGINT PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    name VARCHAR(32) NOT NULL,
    allow BIGINT NOT NULL,
    deny BIGINT NOT NULL,
    hoist BOOLEAN NOT NULL,
    mentionable BOOLEAN NOT NULL,
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADe
);
CREATE TABLE IF NOT EXISTS member_assigned_roles (
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, guild_id, role_id),
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADE,
    FOREIGN KEY (role_id)
        REFERENCES roles (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS guild_folders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name VARCHAR(32) NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS guild_slots (
    guild_id BIGINT,
    user_id BIGINT,
    folder_id BIGINT,
    position INT NOT NULL,
    PRIMARY KEY (guild_id, user_id),
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (folder_id)
        REFERENCES guild_folders (id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS channels (
    id BIGINT PRIMARY KEY,
    type INT NOT NULL,
    guild_id BIGINT,
    name VARCHAR(32),
    position INT,
    topic VARCHAR(2048),
    last_message_id BIGINT,
    parent_id BIGINT,
    sync_parent_permissions BOOLEAN,
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADE,
    FOREIGN KEY (parent_id)
        REFERENCES channels (id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    author_id BIGINT,
    content VARCHAR(4096),
    timestamp TIMESTAMP NOT NULL,
    edited_timestamp TIMESTAMP,
    mention_everyone BOOLEAN NOT NULL,
    pinned BOOLEAN NOT NULL,
    pinned_at TIMESTAMP,
    referenced_message_id BIGINT,
    flags BIGINT NOT NULL DEFAULT 0,
    FOREIGN KEY (channel_id)
        REFERENCES channels (id)
        ON DELETE CASCADE,
    FOREIGN KEY (author_id)
        REFERENCES users (id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS read_states (
    user_id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    mentions BIGINT NOT NULL DEFAULT 0,
    last_message_id BIGINT,
    PRIMARY KEY (user_id, channel_id),
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (channel_id)
        REFERENCES channels (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS permission_overwrites (
    id BIGINT NOT NULL,
    channel_id BIGINT NOT NULL,
    type INT NOT NULL,
    allow BIGINT NOT NULL,
    deny BIGINT NOT NULL,
    PRIMARY KEY (id, channel_id),
    FOREIGN KEY (channel_id)
        REFERENCES channels (id)
        ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS message_reactions (
    message_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    PRIMARY KEY (message_id, user_id, emoji),
    FOREIGN KEY (message_id)
        REFERENCES messages (id)
        ON DELETE CASCADE,
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);