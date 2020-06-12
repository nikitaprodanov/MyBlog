import sqlite3

DB_NAME = 'blog.db'

conn = sqlite3.connect(DB_NAME)

conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS posts
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        article_id INTEGER,
        file_path TEXT,
        user_id INTEGER,
        FOREIGN KEY(article_id) REFERENCES articles(id)
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')
conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS comments
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        message TEXT,
        user_id INTEGER,
        username TEXT,
        FOREIGN KEY(post_id) REFERENCES posts(id)
    )
''')
conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS articles
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
''')
conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT
    )
''')
conn.commit()

class DB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()