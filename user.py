import hashlib

from database import DB
from post import Post

class User:
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email

    def create(self):
        with DB() as db:
            values = (self.username, self.password, self.email)
            db.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)''', values)
            return self
    
    @staticmethod
    def find_by_email(email):
        if not email:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE email = ?',
                (email,)
            ).fetchone()
            if row:
                return User(*row)


    @staticmethod
    def find_by_username(username):
        if not username:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT * FROM users WHERE username = ?',
                (username,)
            ).fetchone()
            if row:
                return User(*row)

    @staticmethod
    def find_by_id(id):
        if not id:
            return None
        with DB() as db:
            row = db.execute(
                'SELECT username FROM users WHERE id = ?',
                (id,)
            ).fetchone()
            if row:
                return row[0]

    @staticmethod
    def hash_password(password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password == hashlib.md5(password.encode('utf-8')).hexdigest()

    def save_username(self):
        with DB() as db:
            values = (self.username, self.id)
            db.execute('''UPDATE users SET username = ? WHERE id = ?''', values)
    
    def save_email(self):
        with DB() as db:
            values = (self.email, self.id)
            db.execute('''UPDATE users SET email = ? WHERE id = ?''', values)

    def save_password(self):
        with DB() as db:
            values = (self.password, self.id)
            db.execute('''UPDATE users SET password = ? WHERE id = ?''', values)