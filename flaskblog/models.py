from datetime import datetime
from flaskblog import login_manager
from flask_login import UserMixin
from .db_utils import execute_query
from flask import abort

@login_manager.user_loader
def load_user(user_id):
    return  User().get(user_id = int(user_id))

class User(UserMixin):
    id = None
    username = None
    email = None
    image_file = 'default.jpg'
    password = None
    posts = None

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

    def _load_row(self, row):
        self.id = row['id']
        self.username = row['username']
        self.email = row['email']
        self.password = row['password']
        self.image_file = row['image_file']

    def get(self, user_id=None, email=None, username=None):
        try:
            if user_id is not None:
                row = execute_query(
                    "SELECT * FROM user WHERE id='{}'".format(user_id))[0]
            elif email is not None:
                row = execute_query(
                    "SELECT * FROM user WHERE email='{}'".format(email))[0]
            elif username is not None:
                row = execute_query(
                    "SELECT * FROM user WHERE username='{}'".format(username))[0]
            self._load_row(row)
            return self
        except IndexError:
            return None


    @classmethod
    def add_user(cls, username, email, password):
        max_id = execute_query("SELECT max(id) FROM user")[0]['max(id)']
        if max_id == None:
            max_id = 0
        execute_query(
            "INSERT INTO user (id, username, email, image_file, password) " +
            "VALUES('{}', '{}', '{}', '{}', '{}')".format(
                max_id+1, username, email, 'default.jpg', password),
                fetch=False)

    def update_user(self):
        execute_query(
            "UPDATE user " +
            "SET username='{}', email='{}', image_file='{}' WHERE id='{}'".format(
                self.username, self.email, self.image_file, self.id),
                fetch=False)


class Post():
    id = None
    title = None
    date_posted = datetime.utcnow()
    content = None
    user_id = None
    author = None

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

    def _load_row(self, row):
        self.id = row['id']
        self.title = row['title']
        self.date_posted = row['date_posted']
        self.content = row['content']
        self.user_id = row['user_id']
        self.author = User().get(user_id= row['user_id'])

    @classmethod
    def query_all(cls):
        rows = execute_query("SELECT * FROM post")
        posts = []
        for row in rows:
            p = cls()
            p._load_row(row)
            posts.append(p)
        return posts

    @classmethod
    def add_post(cls, title, content, author):
        max_id = execute_query("SELECT max(id) FROM post")[0]['max(id)']
        if max_id == None:
            max_id = 0
        execute_query(
            "INSERT INTO post (id, title, date_posted, content, user_id) " +
            "VALUES('{}', '{}', '{}', '{}', '{}')".format(
                max_id+1, title, datetime.utcnow(), content, author.id),
                fetch=False)


    @classmethod
    def delete_post(cls, post):
        execute_query("DELETE FROM post WHERE id='{}'".format(post.id),
                      fetch=False)

    def get(self, post_id=None):
        try:
            row = execute_query(
                    "SELECT * FROM post WHERE id='{}'".format(post_id))[0]
            self._load_row(row)
            return self
        except IndexError:
            return None

    def get_or_404(self, post_id, description=None):
        p = self.get(post_id)
        if p is None:
            abort(404, description=description)
        return p

    def update_post(self):
        execute_query(
            "UPDATE post " +
            "SET title='{}', content='{}' WHERE id='{}'".format(
                self.title, self.content, self.id),
                fetch=False)
