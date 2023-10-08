-- Derailed's 'tracks:' Twitter-like tweets, Reddit-like posts, and Discord-like threads.
-- TODO in another migration: embeds.
CREATE TABLE IF NOT EXISTS tracks (
    id BIGINT PRIMARY KEY,
    author_id BIGINT,
    guild_id BIGINT,
    origin_track_id BIGINT,
    -- 0: Original Content
    -- 1: Reply with Content
    -- In the case of type 1, `origin_track_id` is what's being replied to.
    -- 2: Retrack
    type INT NOT NULL,
    content TEXT,
    FOREIGN KEY (author_id)
        REFERENCES users (id)
        ON DELETE SET NULL,
    FOREIGN KEY (guild_id)
        REFERENCES guilds (id)
        ON DELETE CASCADE,
    FOREIGN KEY (origin_track_id)
        REFERENCES tracks (id)
        ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS track_reaction (
    user_id BIGINT,
    track_id BIGINT,
    emoji TEXT NOT NULL,
    PRIMARY KEY (user_id, track_id),
    FOREIGN KEY (user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (track_id)
        REFERENCES tracks (id)
        ON DELETE CASCADE
);