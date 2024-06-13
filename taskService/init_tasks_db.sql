CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    author_id INT,
    title VARCHAR(128) NOT NULL,
    deadline TIMESTAMP,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    is_completed BOOLEAN DEFAULT FALSE
);