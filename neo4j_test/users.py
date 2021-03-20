from neo4j import GraphDatabase
import load
class users:
    '''
    create users
    query users
    this class can only be used when the load.py is ran, so the stock nodes are created
    '''
    def __init__(self):
        '''
        make connection to the database.
        '''
        uri = "bolt://172.22.152.21:7687"
        user = "neo4j"
        password = "fourtune1234"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.unique_constraint()

    def close(self):
        '''
        close driver connection
        '''
        self.driver.close()

    def cypher_unique_constraint(self, tx):
        '''
        set the constraint that each node is unique
        '''
        tx.run("CREATE CONSTRAINT ON (n:user) ASSERT n.userId IS UNIQUE")
        tx.run("CREATE CONSTRAINT ON (n:portafolio) ASSERT n.name IS UNIQUE")

    def unique_constraint(self):
        '''
        set the constraint that each node is unique
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_unique_constraint)
            except:
                print("Unique contraint is alreay in place for user and portafolio")
    def cypher_create_user(self, tx, email, userId, password):
        '''
        create a new user
        (email, id, password)
        '''
        tx.run("CREATE (:user {email: $email, userId: $userId, password: $password})", email=email, userId=userId, password=password)

    def create_user(self, email, userId, password):
        '''
        create a new user
        (email, id, password)
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_create_user, email, userId, password)
            except:
                print("cannot create user, it may already exist")
                
    def cypher_delete_user(self, tx, userId):
        '''
        remove user by userId
        '''
        tx.run("MATCH (u:user {u.userId:$userId})-[o:owns]->(:portafolio) DELETE o", userId=userId) # delete the relationship first
        tx.run("MATCH (u:user {u.userId:$userId}) DELETE u", userId=userId)

    def delete_user(self, userId):
        '''
        remove user by userId
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_delete_user, userId)
            except:
                print("user cannot be deleted")
                
    def cypher_create_portafolio(self, tx, userId, portafolio):
        '''
        create a new portafolio
        (name)
        '''
        tx.run("CREATE (:portafolio {name: $name})", name=portafolio)
        tx.run("MATCH (a:user), (b:portafolio) WHERE a.userId=$userId AND b.name=$name CREATE (a)-[:owns]->(b)", name=portafolio, userId=userId)

    def create_portafolio(self, userId, portafolio):
        '''
        create a new portafolio
        (name)
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_create_portafolio, userId, portafolio)
            except:
                print("Portafolio cannot be created, it may exist already")
                
    def cypher_delete_portafolio(self, tx, portafolio):
        '''
        delete a new portafolio
        (name)
        '''
        tx.run("MATCH (a)-[o:owns]->(p:portafolio {name:$name}) DELETE o", name=portafolio) # remove the edge
        tx.run("MATCH (p:portafolio {name:$name})-[c:contains]->(:stock) DELETE c", name=portafolio) # remove the edge
        tx.run("MATCH (p:portafolio {name:$name}) DELETE p", name=portafolio) # remove the node

    def delete_portafolio(self, portafolio):
        '''
        create a new portafolio
        (name)
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_delete_portafolio, portafolio)
            except:
                print("Portafolio cannot be deleted")
                
    def cypher_add_stock_to_portafolio(self, tx, symbol, portafolio):
        '''
        add a stock to a portafolio
        (symbol, portafolio)
        '''
        tx.run("MATCH (a:portafolio), (b:stock) WHERE a.name=$portafolio AND b.symbol=$symbol CREATE (a)-[:contains]->(b)", portafolio=portafolio, symbol=symbol)    

    def add_stock_to_portafolio(self, symbol, portafolio):
        '''
        add a stock to a portafolio
        (symbol, portafolio)
        '''
        with self.driver.session() as session:
            session.write_transaction(self.cypher_add_stock_to_portafolio, symbol, portafolio)

    def cypher_remove_stock_from_portafolio(self, tx, symbol, portafolio):
        '''
        remove a stock from a portafolio
        (symbol, portafolio)
        '''
        tx.run("MATCH (a:portafolio)-[c:contains]->(b:stock) WHERE a.name=$portafolio AND b.symbol=$symbol DELETE c", portafolio=portafolio, symbol=symbol)    

    def remove_stock_from_portafolio(self, symbol, portafolio):
        '''
        remove a stock from a portafolio
        (symbol, portafolio)
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_remove_stock_from_portafolio, symbol, portafolio)
            except:
                print("stock cannot be removed from the portafolio")

    def cypher_rename_portafolio(self, tx, portafolio, newName):
        '''
        rename a portafolio
        (portafolio, newName)
        '''
        tx.run("MATCH (a:portafolio {name:$oldName}) SET a.name=$newName", oldName=portafolio, newName=newName)    

    def rename_portafolio(self, portafolio, newName):
        '''
        rename a portafolio
        (portafolio, newName)
        '''
        with self.driver.session() as session:
            try:
                session.write_transaction(self.cypher_rename_portafolio, portafolio, newName)
            except:
                print("portafolio cannot be renamed")
    
    def cypher_get_portafolio_of_user(self, tx, userId):
        '''
        return the portafolio owned by a user.
        return value type is a list
        '''
        result = tx.run("MATCH (u:user {userId:$userId})-[:owns]->(p:portafolio) RETURN p.name AS name", userId=userId)
        try: # in case of empty query result
            return [record["name"] for record in result]
        except:
            return None
        
    def get_portafolio_of_user(self, userId):
        '''
        return the portafolio owned by a user.
        '''
        with self.driver.session() as session:
            result = session.write_transaction(self.cypher_get_portafolio_of_user, userId)
        return result

    def cypher_get_stock_of_portafolio(self, tx, name):
        '''
        return the stocks contained by a portafolio.
        the returned value is a list
        '''
        result = tx.run("MATCH (u:portafolio {name:$name})-[:contains]->(s:stock) RETURN s.symbol AS symbol", name=name)
        try: # in case of empty query result
            return [record["symbol"] for record in result]
        except:
            return None
        
    def get_stock_of_portafolio(self, name):
        '''
        return the stocks contained by a portafolio.       
        '''
        with self.driver.session() as session:
            result = session.write_transaction(self.cypher_get_stock_of_portafolio, name)
        return result
            
    def cypher_clean_database(self, tx):
        '''
        delete all the relationships first, then delete all the nodes
        '''
        tx.run("MATCH ()-[n]->() DELETE n")
        tx.run("MATCH (n) DELETE n")

    def clean_database(self):
        '''
        delete all the relationships first, then delete all the nodes
        '''
        with self.driver.session() as session:
            session.write_transaction(self.cypher_clean_database)

    def cypher_clean_portafolio(self, tx):
        '''
        delete all the relationships first, then delete all the nodes
        '''
        tx.run("MATCH ()-[n]->() DELETE n")
        tx.run("MATCH (n:portafolio) DELETE n")
        tx.run("MATCH (n:user) DELETE n")

    def clean_portafolio(self):
        '''
        delete all the relationships first, then delete all the nodes
        '''
        with self.driver.session() as session:
            session.write_transaction(self.cypher_clean_portafolio)
            
    

if __name__ == '__main__':
    u = users()
    #u.clean_database()
    #lds = load.loadStocks(stockDict)
    u.clean_portafolio()
    u.create_user('haixul2@illinois.edu', 'haixul2', '123456')
    u.create_user('haixul2@illinois.edu', 'haixul3', '123456')
    u.create_portafolio('haixul3', 'technology')
    u.create_portafolio('haixul3', 'energy')
    u.create_portafolio('haixul2', 'financial')
    print(u.get_portafolio_of_user('haixul2'))
    u.delete_portafolio('financial')
    print(u.get_portafolio_of_user('haixul2'))
    print(u.get_portafolio_of_user('haixul3'))
    u.rename_portafolio('technology', 'tech')
    print(u.get_portafolio_of_user('haixul3'))
    u.add_stock_to_portafolio('AAPL', 'technology')
    u.add_stock_to_portafolio('MSFT', 'technology')
    u.add_stock_to_portafolio('AMZN', 'technology')
    u.add_stock_to_portafolio('GOOG', 'technology')
    u.add_stock_to_portafolio('XOM', 'energy')
    u.add_stock_to_portafolio('CVX', 'energy')
    u.add_stock_to_portafolio('BP', 'energy')
    u.add_stock_to_portafolio('JPM', 'financial')
    u.add_stock_to_portafolio('BAC', 'financial')
    u.add_stock_to_portafolio('PYPL', 'financial')
    print(u.get_stock_of_portafolio('energy'))
    u.remove_stock_from_portafolio('CVX', 'energy')
    print(u.get_stock_of_portafolio('energy'))
    #u.clean_portafolio()
    u.close()
