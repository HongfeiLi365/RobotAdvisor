from neo4j import GraphDatabase
import load
class users:
    '''
    create users
    query users
    '''
    def __init__(self):
        '''
        make connection to the database.
        '''
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "123456"
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        '''
        close driver connection
        '''
        self.driver.close()

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
            session.write_transaction(self.cypher_create_user, email, userId, password)

    def cypher_delete_user(self, tx, userId):
        '''
        remove user by userId
        '''
        tx.run("MATCH (u:user {userId:$userId}) DELETE u", userId=userId)

    def delete_user(self, userId):
        '''
        remove user by userId
        '''
        with self.driver.session() as session:
            session.write_transaction(self.cypher_delete_user, userId)
        
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
            session.write_transaction(self.cypher_create_portafolio, userId, portafolio)

    
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

    

if __name__ == '__main__':
    csvFile = "all_stats.csv"
    stockDict = {}
    with open(csvFile, 'r') as fin:
        lines = fin.readlines()
        for index,line in enumerate(lines):
            if index == 0:
                continue
            else:
                items = line.split(",")
                symbol = items[0]
                try:
                    beta = float(items[1])
                except:
                    beta = 0
                try:
                    weekChange = float(items[2].strip("%"))
                except:
                    weekChange = 0
                stockDict[symbol] = [beta, weekChange]
    
    u = users()
    u.clean_database()
    lds = load.loadStocks(stockDict)
    u.create_user('haixul2@illinois.edu', 'haixul2', '123456')
    u.create_user('haixul2@illinois.edu', 'haixul3', '123456')
    u.create_portafolio('haixul3', 'technology')
    u.create_portafolio('haixul3', 'energy')
    u.create_portafolio('haixul2', 'financial')
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
    u.close()
