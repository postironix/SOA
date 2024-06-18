CREATE DATABASE IF NOT EXISTS stats;
CREATE TABLE IF NOT EXISTS stats.main
(
    `task_id` Int32,
    `user_id` Int32 NULL,
    `type` String
)
ENGINE = MergeTree
ORDER BY (task_id)
PARTITION BY (task_id);

CREATE TABLE IF NOT EXISTS stats.authors
(
    `author` String,
    `user_id` Int32,
    `task_id` Int32
)
ENGINE = MergeTree
ORDER BY (author)
PARTITION BY (author);
