from neo4j import GraphDatabase

class loadStocks:
    '''
    load statistics of the stocks into the database.
    The input of this class should be a dictionary of stocks.
    key: symbol
    attributes: symbol, beta, 52WeekChange, ...
    '''
    def __init__(self, stockDict):
        '''
        make connection to the database.
        '''
        uri = "bolt://localhost:7687"
        user = "neo4j"
        password = "123456"
        self.stockDict = stockDict
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.create_stocks()

    def create_stock(self, tx, symbol, beta, weekChange):
        '''
        it defines the format of the stock node, for example how many attributes are used.
        '''
        tx.run("CREATE (:stock {symbol: $symbol, beta: $beta, weekChange: $weekChange})",symbol=symbol, beta=beta, weekChange=weekChange)

    def create_stocks(self):
        '''
        insert all items from the dict into the database
        '''
        with self.driver.session() as session:
            for symbol in self.stockDict.keys():
                session.write_transaction(self.create_stock, symbol, self.stockDict[symbol][0], self.stockDict[symbol][1])
        self.driver.close()

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
    
    lds = loadStocks(stockDict)
                            
