from database import DB
from post import Post

class Article:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def all():
        with DB() as db:
            rows = db.execute('SELECT *  FROM articles').fetchall()
            return [Article(*row) for row in rows]

    @staticmethod
    def find(id):
        with DB() as db:
            row = db.execute('SELECT * FROM articles WHERE id = ?', (id,)).fetchone()
            if not row:
                return Article(0, "No article")
            return Article(*row)

    def create(self):
        with DB() as db:
            values = (self.name,)
            db.execute('''
                INSERT INTO articles (name)
                VALUES (?)''', values)
            return self

    def delete(self):
        with DB() as db:
            db.execute('DELETE FROM articles WHERE id = ?', (self.id,))
            db.execute(
                '''UPDATE posts
                SET article_id = 0 WHERE article_id = ?
                ''', (self.id,)
            )

    def posts(self):
        return Post.find_by_article(self)