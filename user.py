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
    def hash_password(password):
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password == hashlib.md5(password.encode('utf-8')).hexdigest()