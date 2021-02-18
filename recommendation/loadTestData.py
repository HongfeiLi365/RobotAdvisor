import pickle
import numpy as np
import datetime
from yahoo_fin.stock_info import get_data, tickers_sp500, tickers_nasdaq, tickers_other, get_quote_table
import stockPriceClean as sc

class load:
    '''
    load test data (SP500) to test stocks clustering.
    the data is load starts from one specific trading date to another one
    '''
    def __init__(self, savedStockDict = "sp500.p", savedStockList = "stockList.p", savedData = "stockData.p"):
        self.savedStockDictPath = savedStockDict
        self.savedStockListPath = savedStockList
        self.stockList = []
        self.stockDict = {}
        self.numberOfDays = 20 # 20 days to calculate load
        self.startDate = datetime.date(2020,1,1)
        self.endDate = self.startDate + datetime.timedelta(days = self.numberOfDays)
        self.savedSDataPath = savedData
        self.loadStockList()
        self.loadStock()
        
    def loadStockList(self):
        '''
        get the list of SP500.
        fundamentals of each stock is stored in the dictionary self.stockDict
        '''
        try:
            self.stockDict = pickle.load(open(self.savedStockDictPath, "rb"))
            #print(stockDict)
        except:
            for ticker in tickers_sp500():
                try:
                    self.stockDict[ticker] = get_quote_table(ticker)
                    print(ticker + " is added.")
                except:
                    print(ticker + " is skipped for some reason")
            pickle.dump(self.stockDict, open(self.savedStockDictPath, "wb"))
        self.stockList = list(self.stockDict.keys())
        print("#" * 40)
        print(" " * 40)
        print("Loaded fundamentals of SP 500: ")
        print(sorted(self.stockDict[self.stockList[0]].keys()))
        print(" " * 40)
        #print("#" * 40)
        
    def loadStock(self):
        '''
        load the stock data of day trading
        '''
        self.stockDataList = []
        self.stockData = np.zeros(self.numberOfDays)
        try:
            self.stockDataList = pickle.load(open(self.savedStockListPath, "rb"))
            self.stockData = pickle.load(open(self.savedSDataPath, "rb"))
            counter = len(self.stockDataList)
        except:
            print("Cannot locate the files, generating new files")
            for stock in self.stockList:
                try:
                    greppedData = sc.stockPriceClean(get_data(stock, start_date = str(self.startDate), end_date = str(self.endDate)))
                    self.stockDataList = self.stockDataList + [stock]
                    if counter == 0:
                        self.stockData = greppedData.get()
                    else:
                        self.stockData = np.vstack((self.stockData, greppedData.get()))
                    counter = counter + 1
                except:
                    print(stock + ": cannot get data")
        pickle.dump(self.stockDataList, open(self.savedStockListPath, "wb"))
        pickle.dump(self.stockData, open(self.savedSDataPath, "wb"))
        print("#" * 40)
        print(" " * 40)
        print("Loaded: Stock pricing data from " + str(self.startDate) + " to " +  str(self.endDate))
        print(" " * 40)
        print("#" * 40)
        
        #print(self.stockData)
    
    def get(self):
        '''
        Returns 3 items, 
        one dictionary of dictionary with all stock fundamentals,
        one list of stocks 
        and one numpy array of trading data
        -------
        TYPE
            STOCKS fundamentals, dictionary of dictionary
        TYPE
            STOCKS IN ORDER
        TYPE
            STOCKS CHANGES IN TERMS OF TRADING DAYS

        '''
        return self.stockDict, self.stockDataList, self.stockData

# test
if __name__ == '__main__':
    ld = load()
