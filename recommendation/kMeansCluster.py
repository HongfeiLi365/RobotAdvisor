from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pylab as plt
import loadTestData
import RSI
import stockSectorInfo 
import random

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
        self.numberOfGroups = 5 # divide the stocks into 5 groups
        self.betaLabel = self.cluster(self.dataPrep('Beta (5Y Monthly)'))
        self.marketCapLabel = self.cluster(self.dataPrep('Market Cap'))
        self.peRatioLabel = self.cluster(self.dataPrep('PE Ratio (TTM)'))
        self.rsiLabel = self.cluster(self.RSI)
        self.sectorLabel = self.labelSector()
        self.featureLabel = self.mergeLabels()
        self.label = self.clusterWithAllLabels(self.numberOfGroups)
        self.groupDict = self.groupStocks()

    def cluster(self, dataToCluster, n = 2):
        '''
        cluster the data by any data into two categories.
        For example, for beta, it will cluster high or low as 0 or 1.
        '''
        kmeans = KMeans(n_clusters=n, random_state=0).fit(dataToCluster.reshape(-1, 1))
        return kmeans.labels_
    
    def clusterWithAllLabels(self, n = 5):
        '''
        use all the dimension/feature to do clustering
        '''
        kmeans = KMeans(n_clusters=n, random_state=0).fit(self.featureLabel)
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

    def mergeLabels(self):
        '''
        merge all available labels together
        '''
        tempData = np.vstack((self.betaLabel, self.rsiLabel))
        tempData = np.vstack((tempData, self.marketCapLabel))
        tempData = np.vstack((tempData, self.peRatioLabel))
        tempData = np.transpose(tempData)
        tempData = np.hstack((tempData, self.sectorLabel))
        return tempData

    def groupStocks(self):
        '''
        group the stocks into a dictionary based on the cluster number
        '''
        tempDict = {}
        for index in range(len(self.stockList)):
            clusterNumber = self.label[index]
            stock = self.stockList[index]
            if clusterNumber not in tempDict.keys():
                tempDict[clusterNumber] = [stock]
            else:
                tempDict[clusterNumber] = tempDict[clusterNumber] + [stock]
        return tempDict

    def recommend(self, stockList, n = 5):
        '''
        it takes a list of stocks as input,
        first it figures out what are the group/cluster number of the current stocks, 
        then it recommend n stocks to balance the stocks in each group
        '''
        groupWeight = np.zeros(self.numberOfGroups) # value of each element should be as close as possible
        returnList = []
        for stock in stockList:
            groupNumber = self.label[self.stockList.index(stock)] # find the group number of the stock
            groupWeight[groupNumber] = groupWeight[groupNumber] + 1
        for i in range(n):
            groupToRecommend = self.getGroupNumber(groupWeight)
            recommendedStock = self.pickStock(groupToRecommend)
            print(groupWeight)
            if recommendedStock not in stockList and recommendedStock not in returnList:
                returnList = returnList + [recommendedStock]
                groupWeight[groupToRecommend] = groupWeight[groupToRecommend] + 1
            else:
                i = i - 1 # back one step
        return returnList
    
    def getGroupNumber(self, groupWeight):
        '''
        return a groupNumber to recommend stock based on the objective to optimizing group balancing (minimizing variance)
        '''
        optimalGroupNumber = 0
        currentVar = 9999
        for index in range(len(groupWeight)):
            tempWeight = np.copy(groupWeight)
            tempWeight[index] = tempWeight[index] + 1
            if np.var(tempWeight) < currentVar:
                optimalGroupNumber = index
                currentVar = np.var(tempWeight)
        return optimalGroupNumber

    def pickStock(self, groupToRecommend):
        '''
        recommend a stock randomly from a group
        '''
        poolOfStock = self.groupDict[groupToRecommend]
        return poolOfStock[random.randint(0, len(poolOfStock) - 1)]


if __name__ == '__main__':
    ld = loadTestData.load()
    stockDict, stockList, stockData = ld.get()
    rsi = RSI.RSI(stockData)
    si = stockSectorInfo.sectorInfo()
    tst = stockCluster(stockDict, stockList, rsi.get(), si.get())
    existingStock = ['AMZN', 'JPM']
    print("Existing stock: ", existingStock)
    recommendedStock = tst.recommend(existingStock)
    print("Recommended 5 stocks are: ", recommendedStock)
    print("Stock     Sector                   Beta    Marketcap   PE_ratio    RSI")
    for stock in existingStock + recommendedStock:
        print(stock + " "*(10 - len(stock)) + tst.sectorDict[stock] + " "*(25 - len(tst.sectorDict[stock])) + str(stockDict[stock]['Beta (5Y Monthly)']) + " "*(8 - len(str(stockDict[stock]['Beta (5Y Monthly)']))) + str(stockDict[stock]['Market Cap']) + " "*(10 - len(str(stockDict[stock]['Market Cap']))) + str(stockDict[stock]['PE Ratio (TTM)']) + " "*5 + str(int(tst.RSI[stockList.index(stock)])))
