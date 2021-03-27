from datetime import datetime
#from flaskblog import login_manager
from flask_login import UserMixin
from neo4j_db_utils import execute_query
from flask import abort

#@login_manager.user_loader
#def load_user(user_id):
#    return  User().get(user_id = int(user_id))

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
        """
        set attributes of itself by values in row

        Parameters
        ----------
        row : dict
            a record from database
        """
        self.id = row['id']
        self.username = row['username']
        self.email = row['email']
        self.password = row['password']
        self.image_file = row['image_file']

    def get(self, user_id=None, email=None, username=None):
        """
        Retrieve a user from database by either user_id, email, or username.
        Return None if such a user does not exist in database.

        Returns
        -------
        User object
            retrieved user
        """
        try:
            if user_id is not None:
                row = execute_query(
                    "MATCH (n:user) WHERE n.id={} RETURN n".format(user_id))[0]
            elif email is not None:
                row = execute_query(
                    "MATCH (n:user) WHERE n.email='{}' RETURN n".format(email))[0]
            elif username is not None:
                row = execute_query(
                    "MATCH (n:user) WHERE n.username='{}' RETURN n".format(username))[0]
            row = row.data()['n'] # force the neo4j output to be a list of dictionaries, it works fine with only one output
            self._load_row(row)
            return self
        except IndexError:
            return None


    @classmethod
    def add_user(cls, username, email, password):
        """Save a new user to database"""
        max_id = execute_query("MATCH (n:user) return max(n.id) as maxid")[0]['maxid']
        print('max_id:', max_id)
        if max_id == None:
            max_id = 0
            execute_query("CREATE CONSTRAINT ON (n:user) ASSERT n.id IS UNIQUE", fetch=False)
            execute_query("CREATE CONSTRAINT ON (n:user) ASSERT n.username IS UNIQUE", fetch=False)
        execute_query("CREATE (:user {id: %s, username: '%s', email: '%s', image_file: '%s', password: '%s'})" % (str(max_id+1), username, email, 'default.jpg', password), fetch=False)

    def update_user(self):
        """Update a user in database by current attribute values"""
        execute_query(
            "MATCH (n:user {id: %s}) " +
            "SET n.username='%s', n.email='%s', n.image_file='%s'" %(str(self.id), self.username, self.email, self.image_file),
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
        """set attributes of current object

        Parameters
        ----------
        row : dict
            a record from database
        """
        self.id = row['id']
        self.title = row['title']
        self.date_posted = row['date_posted']
        self.content = row['content']
        self.user_id = row['user_id']
        self.author = User().get(user_id= row['user_id'])

    @classmethod
    def query_all(cls):
        """return all posts in database

        Returns
        -------
        list of portafolio objects
        """
        rows = execute_query('MATCH (n:portafolio) RETURN n')
        posts = []
        for row in rows:
            row = row.data()['n']
            p = cls()
            p._load_row(row)
            posts.append(p)
        return posts

    @classmethod
    def add_post(cls, title, content, author):
        """save a new portafolio to database

        Parameters
        ----------
        title : str
            name of the portafolio
        content : str
            not sure what is it for now
        author : User object
            user who created this portafolio
        """
        max_id = execute_query('MATCH (n:portafolio) RETURN max(n.id) as maxid')[0]['maxid']
        if max_id == None:
            max_id = 0
            execute_query("CREATE CONSTRAINT IF NOT EXISTS ON (n:portafolio) ASSERT n.title IS UNIQUE", fetch=False)
            execute_query("CREATE CONSTRAINT IF NOT EXISTS ON (n:portafolio) ASSERT n.id IS UNIQUE", fetch=False)
            
        execute_query("CREATE (:portafolio {id: %s, title: '%s', date_posted: '%s', content: '%s', user_id: %s})" %(max_id + 1, title, datetime.utcnow(), content, author.id),fetch=False)
        execute_query("MATCH (a:user), (p:portafolio) WHERE p.id = %s AND a.id = %s AND p.user_id = %s CREATE (a)-[:owns]->(p)"%(max_id + 1, author.id, author.id))


    @classmethod
    def delete_post(cls, post):
        """delete a post from database

        Parameters
        ----------
        post : Post object
            the post to be deleted
        """
        execute_query("MATCH (a:user)-[o:owns]->(p:portafolio) WHERE p.id=%s DELETE o"%(post.id), fetch=False)
        execute_query("MATCH (p:portafolio) WHERE p.id=%s DELETE p"%(post.id), fetch=False)

    @classmethod
    def add_stock(cls, post_id=None, stock=None):
        """
        add the relationship between the portafolio and the stock
        Parameters
        ----------
        post_id: id of the portafolio
        stock: symbol of a stock
        """
        execute_query("MATCH (p:portafolio) WHERE p.id = %s CREATE (p)-[:contains]->(s:stock {symbol:'%s'})"%(post_id, stock))

    @classmethod
    def delete_stock(cls, post_id=None, stock=None):
        """
        delete the relationship between the portafolio and the stock
        Parameters
        ----------
        post_id: id of the portafolio
        stock: symbol of a stock
        """
        execute_query("MATCH (p:portafolio {id:%s})-[r:contains]->(s:stock {symbol:'%s'}) DELETE r"%(post_id, stock))
        
    def get(self, post_id=None):
        """
        Retrieve a portafolio from database by id.
        Return None if such a post does not exist in database.

        Returns
        -------
        Post object
            retrieved portafolio
        """
        try:
            row = execute_query(
                    "MATCH (p:portafolio) WHERE p.id=%s return p"%(post_id))
            print(row)
            row = row[0].data()['p']
            self._load_row(row)
            return self
        except IndexError:
            return None

    def get_or_404(self, post_id, description=None):
        """
        Retrieve a post from database, raise NotFound error if post does
        not exist

        Parameters
        ----------
        post_id : int
            'id' in post table
        description : str, optional
            Message to display in NotFound Error, by default None

        Returns
        -------
        Post object
            retrieved post
        """
        p = self.get(post_id)
        if p is None:
            abort(404, description=description)
        return p

    def update_post(self):
        """
        Update post title and content in database by current attribute values
        """
        execute_query(
            "MATCH (p:portafolio) WHERE p.id = %s SET p.title = '%s', p.content = '%s'"%(
                self.title, self.content, self.id),
                fetch=False)

if __name__ == '__main__':
    u = User()
    u.add_user('haixu1', 'lhaixu1@illinois.edu', '123456')
    u.add_user('haixu2', 'lhaixu2@illinois.edu', '123456')
    u.add_user('haixu3', 'lhaixu3@illinois.edu', '123456')
    print(u.get(1))
    p = Post()
    p.add_post("tech", "APPL", u.get(1))
    p.add_post("energy", "xom", u.get(1))
    #p.delete_post(p.get(2))
    p.add_stock(1, "APPL")
    p.add_post("tech", "APPL", u.get(1))
    print(p.get(1))
    print(p.query_all())
