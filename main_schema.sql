CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

CREATE TABLE likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (comment_id) REFERENCES comments (id)
);

INSERT INTO posts (content) VALUES ('post 1');
INSERT INTO posts (content) VALUES ('post 2');
INSERT INTO posts (content) VALUES ('post 3');
INSERT INTO comments (post_id, content) VALUES (1, 'content 1');
INSERT INTO comments (post_id, content) VALUES (2, 'content 2');
INSERT INTO comments (post_id, content) VALUES (3, 'content 3');
INSERT INTO likes (comment_id, user_id) VALUES (1, 'user_id1');
INSERT INTO likes (comment_id, user_id) VALUES (2, 'user_id2');
INSERT INTO likes (comment_id, user_id) VALUES (3, 'user_id3');
