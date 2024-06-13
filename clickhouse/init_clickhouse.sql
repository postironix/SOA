CREATE DATABASE IF NOT EXISTS stats;
CREATE TABLE IF NOT EXISTS stats.main
(
    `id` Int32,
    `task_id` Int32,
    `user_id` Int32 NULL,
    `type` String
)
ENGINE = MergeTree
PRIMARY KEY (id);
