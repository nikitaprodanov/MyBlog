from database import DB
from comment import Comment

class Post:
    def __init__(self, id, name, description, article, file_path, user_id):
        self.id = id
        self.name = name
        self.description = description
        self.article = article
        self.file_path = file_path
        self.user_id = user_id

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT * FROM posts').fetchall()
            return [Post(*row) for row in rows]

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
            return Post(*row)

    @staticmethod
    def find_by_article(article):
        with DB() as db:
            rows = db.execute(
                'SELECT * FROM posts WHERE article_id = ?',
                (article.id,)
            ).fetchall()
            return [Post(*row) for row in rows]        

    @staticmethod
    def find_by_user_id(user_id):
        with DB() as db:
            rows = db.execute(
                'SELECT * FROM posts WHERE user_id = ?',
                (user_id,)
            ).fetchall()
            return [Post(*row) for row in rows]

    def create(self):
        with DB() as db:
            values = (self.name, self.description, self.article.id, self.file_path, self.user_id)
            db.execute('''INSERT INTO
                posts (name, description, article_id, file_path, user_id)
                VALUES (?, ?, ?, ?, ?)''', values)
            return self

    def save(self):
        with DB() as db:
            values = (
                self.name,
                self.description,
                self.article.id,
                self.file_path,
                self.user_id,
                self.id
            )
            db.execute('''UPDATE posts SET 
            name = ?, description = ?, article_id = ?, file_path = ?, user_id =? WHERE id = ?''', values)
            return self

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM posts WHERE id = ?', (self.id,))

    def comments(self):
        return Comment.find_by_post(self)