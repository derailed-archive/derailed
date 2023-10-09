CREATE TABLE IF NOT EXISTS relationships (
    origin_user_id BIGINT,
    target_user_id BIGINT,
    relation INT NOT NULL,
    PRIMARY KEY (origin_user_id, target_user_id),
    FOREIGN KEY (origin_user_id)
        REFERENCES users (id)
        ON DELETE CASCADE,
    FOREIGN KEY (target_user_id)
        REFERENCES users (id)
        ON DELETE CASCADE
);