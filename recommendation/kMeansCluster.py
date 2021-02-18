from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pylab as plt
import loadTestData
import RSI
import stockSectorInfo 

class stockCluster:
    '''
    cluster the stocks by different crateria:
    Price data based:
        high volatility vs low volatility (can be measured by standard deviation, realized volatility, or beta)
        momentum vs mean-reversion (can be measured by technical indicators such as relative strength index)
    Fundamental based:
        sector or industry
        small size vs big size (measured by market capitalization)
        cheap vs expensive, aka value vs growth (measured by price-to-earnings ratio and price-to-sales ratio)
    '''
    def __init__(self, stockDict, stockList, RSI, sectorDict):
        '''
        stockDict: stores the fundamental information of stocks, and beta for volatility
        stockList: list of RSI, in order
        RSI: RSI data
        sectorDict: used to check what sector is the stock in

        all the labels have value of either 0, or 1. Except for the sector label, all other labels are calcuated based on the Kmeans method
        '''
        self.stockDict = stockDict
        self.stockList = stockList
        self.RSI = RSI
        self.sectorDict = sectorDict
        self.numOfSectors = 11 # GIS sectors
        self.betaLabel = self.cluster(self.dataPrep('Beta (5Y Monthly)'))
        self.marketCapLabel = self.cluster(self.dataPrep('Market Cap'))
        self.peRatioLabel = self.cluster(self.dataPrep('PE Ratio (TTM)'))
        self.rsiLabel = self.cluster(self.RSI)
        self.sectorLabel = self.labelSector()

    def cluster(self, dataToCluster, n = 2):
        '''
        cluster the data by any data into two categories.
        For example, for beta, it will cluster high or low as 0 or 1.
        '''
        kmeans = KMeans(n_clusters=n, random_state=0).fit(dataToCluster.reshape(-1, 1))
        return kmeans.labels_
        

    def dataPrep(self, key = 'Beta (5Y Monthly)'):
        '''
        prepare a 1D data with value, replace nan with the non-nan average
        '''
        tempData = np.zeros(len(self.stockList))
        for index in range(len(self.stockList)):
            stockName = self.stockList[index]
            try:
                tempData[index] = self.stockDict[stockName][key]
            except: # assume the some of the values have B (billion) and T (trillion) in it, do the necessary conversion
                if "M" in self.stockDict[stockName][key]:
                    tempData[index] = float(self.stockDict[stockName][key][:-1]) * 1
                elif "B" in self.stockDict[stockName][key]:
                    tempData[index] = float(self.stockDict[stockName][key][:-1]) * 1000
                elif "T" in self.stockDict[stockName][key]:
                    tempData[index] = float(self.stockDict[stockName][key][:-1]) * 1000000
        nonNanAverage = np.nanmean(tempData)
        for index in range(len(self.stockList)):
            if np.isnan(tempData[index]):
                tempData[index] = nonNanAverage     
        #print(tempData)  
        return tempData

    def labelSector(self):
        '''
        create a numpy array, each row is a stock and each column is a sector. Fill the corresponding stock with 1 at the corresponding sector.
        '''
        sectorHash = {}
        counter = 0 # used to label the sectors
        tempData = np.zeros((len(self.stockList), self.numOfSectors))
        for index in range(len(self.stockList)):
            stock = self.stockList[index]
            try:
                sector = self.sectorDict[stock]
                if sector not in sectorHash:
                    sectorHash[sector] = counter
                    counter = counter + 1
                tempData[index, sectorHash[sector]] = 1 # fill in the corresponding sector
            except:
                pass # some ticker cannot be found, like the newly added/removed stock in SP500
        #print(tempData)
        return tempData

if __name__ == '__main__':
    ld = loadTestData.load()
    stockDict, stockList, stockData = ld.get()
    rsi = RSI.RSI(stockData)
    si = stockSectorInfo.sectorInfo()
    tst = stockCluster(stockDict, stockList, rsi.get(), si.get())
