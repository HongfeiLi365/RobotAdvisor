from datetime import datetime
from flaskblog import login_manager
from flask_login import UserMixin
from .neo4j_db_utils import execute_query
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
        #print(user_id, email, username)
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
        #print("Inside update")
        execute_query(
            "MATCH (n:user {{id: {}}}) ".format(self.id) +
            "SET n.username='{}', n.email='{}', n.image_file='{}'".format(self.username, self.email, self.image_file),
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
        self.date_posted = datetime.strptime(row['date_posted'], '%Y-%m-%d %H:%M:%S.%f')
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
        print(rows)
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
        #print("+++++++++++++++++++++")
        #print("post update is called")
        #print("+++++++++++++++++++++")
        execute_query(
            "MATCH (p:portafolio) WHERE p.id = %s SET p.title = '%s', p.content = '%s'"%(
                self.id, self.title, self.content),
                fetch=False)

class Portfolio():
    id = None
    name = None
    user_id = None
    owner = None
    member = None

    def __repr__(self):
        return f"Portfolio('{self.name}', '{self.owner.username}', '{self.member}')"

    def _load_row(self, row, stockQuery = None):
        """
        set attributes of current object

        Parameters
        ----------
        row : dict
            a record from database
        stockQuery: list of neo4j objects
            contains the symbols of the stocks
        """
        self.id = row['id']
        self.name = row['name']
        self.user_id = row['user_id']
        self.owner = User().get(user_id= row['user_id'])
        self.member = []
        if stockQuery:
            for each in stockQuery:
                self.member = self.member + [Stock().get(symbol = each.data()['n.symbol'])]

    @classmethod
    def query_all(cls):
        """return all portfolios in database

        Returns
        -------
        list of portafolio objects
        """
        rows = execute_query('MATCH (n:portfolio) RETURN n')
        #print(rows)
        portfolios = []
        for row in rows:
            row = row.data()['n']
            stocks = execute_query('MATCH (p:portfolio)-[:contains]->(n:stock) WHERE p.id=%s RETURN n.symbol'%(row['id']))
            p = cls()
            p._load_row(row, stocks)
            portfolios.append(p)
        return portfolios
    
    @classmethod
    def query_all_by_user(cls, user = User().get(1)):
        """return all portfolios in database of a specific user
        Parameters
        -------
        user object

        Returns
        -------
        list of portafolio objects
        """
        rows = execute_query('MATCH (n:portfolio) WHERE n.user_id = %s RETURN n'%(user.id))
        #print(rows)
        portfolios = []
        for row in rows:
            row = row.data()['n']
            stocks = execute_query('MATCH (p:portfolio)-[:contains]->(n:stock) WHERE p.id=%s RETURN n.symbol'%(row['id']))
            p = cls()
            p._load_row(row, stocks)
            portfolios.append(p)
        return portfolios

    @classmethod
    def add_portfolio(cls, name, user):
        """save a new portafolio to database
        The query first checks that whether the relationship exits
        Parameters
        ----------
        name : str
          name of the portafolio
        user : User object
          user who created this portafolio
        """
        max_id = execute_query('MATCH (n:portfolio) RETURN max(n.id) as maxid')[0]['maxid']
        if max_id == None:
            max_id = 0
            execute_query("CREATE CONSTRAINT IF NOT EXISTS ON (n:portfolio) ASSERT n.name IS UNIQUE", fetch=False)
            execute_query("CREATE CONSTRAINT IF NOT EXISTS ON (n:portfolio) ASSERT n.id IS UNIQUE", fetch=False)

        execute_query("CREATE (:portfolio {id: %s, name: '%s', user_id: %s})" %(max_id + 1, name, user.id),fetch=False)
        if execute_query("MATCH (a:user)-[:owns]->(p:portfolio) WHERE p.id = %s AND a.id = %s AND p.user_id = %s RETURN p"%(max_id + 1, user.id, user.id)) == []:
            execute_query("MATCH (a:user), (p:portfolio) WHERE p.id = %s AND a.id = %s AND p.user_id = %s CREATE (a)-[:owns]->(p)"%(max_id + 1, user.id, user.id))

    @classmethod
    def delete_portfolio(cls, portfolio):
      """delete a portfolio from database

      Parameters
      ----------
      portfolio : Portfolio object
         the portfolio to be deleted
      """
      execute_query("MATCH (a:user)-[o:owns]->(p:portfolio) WHERE p.id=%s DELETE o"%(portfolio.id), fetch=False)
      execute_query("MATCH (p:portfolio)-[c:contains]->(s:stock) WHERE p.id=%s DELETE c"%(portfolio.id), fetch=False)
      execute_query("MATCH (p:portfolio) WHERE p.id=%s DELETE p"%(portfolio.id), fetch=False)

    @classmethod
    def add_stock(cls, portfolio=None, stock=None):
      """
      add the relationship between the portafolio and the stock
      Only execute when the relationship does not exist
      Parameters
      ----------
      portfolio: object
      stock: object

      return
      ----------
      false if the stock does not exist
      true: successfully inserted, or the stock has been inserted before insertion
      """
      try:
        if execute_query("MATCH (p:portfolio)-[:contains]->(s:stock) WHERE p.id = %s AND s.symbol = '%s' RETURN s"%(portfolio.id, stock.symbol)) == []:
            execute_query("MATCH (p:portfolio) WHERE p.id = %s CREATE (p)-[:contains]->(s:stock {symbol:'%s'})"%(portfolio.id, stock.symbol))
        return True
      except:
        print('Stock cannot be added')
        return False
        pass

    @classmethod
    def recommend_stocks(cls, n=3):
        """
        return stocks based on current stocks in the portfolio
        parameter
        ---------
        number of stocks to be returned

        return
        ---------
        list of stocks objects
        """
        return [Stock().get('AAPL'), Stock().get('MSFT'), Stock().get('AMZN'), Stock().get('GOOG'), Stock().get('FB')][:n]

    @classmethod
    def delete_stock(cls, portfolio=None, stock=None):
        """
        delete the relationship between the portafolio and the stock
        Parameters
        ----------
        portfolio: object
        stock: object
        """
        execute_query("MATCH (p:portfolio {id:%s})-[r:contains]->(s:stock {symbol:'%s'}) DELETE r"%(portfolio.id, stock.symbol))

    def update_portfolio(self):
        """
        Update portfolio in database by current attribute values
        """
        execute_query("MATCH (p:portfolio) WHERE p.id = %s SET p.name = '%s', p.user_id = %s"%(self.id, self.name, self.user_id), fetch=False)

    def get(self, portfolio_id=None):
        """
        Retrieve a portafolio from database by id.
        Return None if such a post does not exist in database.

        Returns
        -------
        Post object
            retrieved portafolio
        """
        try:
            row = execute_query("MATCH (p:portfolio) WHERE p.id=%s return p"%(portfolio_id))
            #print(row)
            row = row[0].data()['p']
            stocks = execute_query('MATCH (p:portfolio)-[:contains]->(n:stock) WHERE p.id=%s RETURN n.symbol'%(portfolio_id))
            self._load_row(row, stocks)
            return self
        except IndexError:
            return None

    def get_or_404(self, portfolio_id, description=None):
        p = self.get(portfolio_id)
        if p is None:
            abort(404, description=description)
        return p

class Stock():
   symbol = None
   return_on_assets = None
   total_debt_to_equity = None
   operating_cash_flow = None
   revenue_per_share = None
   operating_margin = None
   shares_outstanding = None
   current_ratio = None
   ebitda = None
   quarterly_revenue_growth = None
   most_recent_quarter = None
   quarterly_earnings_growth = None
   return_on_equity = None
   profit_margin = None
   diluted_eps = None
   payout_ratio = None
   total_cash_per_share = None

   def __repr__(self):
      return f"Stock('{self.symbol}', '{self.revenue_per_share}')"

   def _load_row(self, row):
      """
      set attributes of current object

      Parameters
      ----------
      row : dict
          a record from database
      """
      self.symbol = row['symbol']
      try:
         self.return_on_assets = row['return_on_assets']
         self.total_debt_to_equity = row['total_debt_to_equity']
         self.operating_cash_flow = row['operating_cash_flow']
         self.revenue_per_share = row['revenue_per_share']
         self.operating_margin = row['operating_margin']
         self.shares_outstanding = row['shares_outstanding']
         self.current_ratio = row['current_ratio']
         self.ebitda = row['ebitda']
         self.quarterly_revenue_growth = row['quarterly_revenue_growth']
         self.most_recent_quarter = row['most_recent_quarter']
         self.quarterly_earnings_growth = row['quarterly_earnings_growth']
         self.return_on_equity = row['return_on_equity']
         self.profit_margin = row['profit_margin']
         self.diluted_eps = row['diluted_eps']
         self.payout_ratio = row['payout_ratio']
         self.total_cash_per_share = row['total_cash_per_share']
      except:
         pass


   def get(self, symbol=None):
      """
      Retrieve a stock from database by symbol.
      Return None if such a post does not exist in database.

      Returns
      -------
      Stock object
          retrieved stock
      """
      try:
         row = execute_query(
            "MATCH (s:stock) WHERE s.symbol='%s' return s"%(symbol))
         row = row[0].data()['s']
         self._load_row(row)
         return self
      except IndexError:
         return None


if __name__ == '__main__':
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   print('+++++++++++++clean up database+++++++++++++++')
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   execute_query('MATCH (p:portfolio)-[r:contains]->(s:stock) DELETE r')
   execute_query('MATCH (u:user)-[r:owns]->(p:portfolio) DELETE r')
   execute_query('MATCH (p:portfolio) DELETE p')
   execute_query('MATCH (u:user) DELETE u')
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   print('+++++++++++++Test user class  +++++++++++++++')
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   u = User()
   u.add_user('haixu1', 'lhaixu1@illinois.edu', '123456')
   u.add_user('haixu2', 'lhaixu2@illinois.edu', '123456')
   u.add_user('haixu3', 'lhaixu3@illinois.edu', '123456')
   print(u.get(1))
   u.id = 1
   u.username = 'updated_name'
   u.update_user()
   print(u.get(1))
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   print('+++++++++++++Test portfolio class++++++++++++')
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   p = Portfolio()
   p.add_portfolio('portfolio1', User().get(1))
   p.add_stock(p.get(1), Stock().get('BOX'))
   print(p.query_all())
   p.add_portfolio('portfolio1', User().get(1))
   p.add_portfolio('portfolio2', User().get(2))
   print(p.query_all())
   print(p.query_all_by_user())
   print(p.recommend_stocks())
   print(p.add_stock(p.get(1), Stock().get('SANA')))
   p.add_stock(p.get(2), Stock().get('MSFT'))
   print(p.query_all())
   p.delete_stock(p.get(1), Stock().get('SANA'))
   print("before delete p2")
   print(p.query_all())
   p.delete_portfolio(p.get(2))
   print(p.query_all())
   print("after delete p2")
   p.id = 1
   p.name = "updated_port"
   p.update_portfolio()
   print(p.query_all())
   print(p.get(1))

   print('+++++++++++++++++++++++++++++++++++++++++++++')
   print('+++++++++++++Test stock class++++++++++++++++')
   print('+++++++++++++++++++++++++++++++++++++++++++++')
   s = Stock()
   print(s.get('SHLS'))
   print(s.get('XXXX'))
   print(s.get('BOX'))
   stocks = execute_query('MATCH (n:stock) RETURN n.symbol LIMIT 3')
   print(stocks[0].data())
