CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    access_token TEXT
);

CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    access_level TEXT NOT NULL,
    type TEXT NOT NULL,
    column TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
