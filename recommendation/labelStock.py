import numpy as np
from sklearn.cluster import KMeans
class label:
    """
    This class creates the labels for each stock based on the features.csv
    """
    def __init__(self, n_cluster = 5, source = 'features.csv'):
        self.array, self.symbol = self.load(source)
        self.labels = self.clusterWithAllLabels(n_cluster)
        self.symbolDict = self.createDict()
        print(self.labels)

    def load(self, file_name, rank_start_bit = 10):
        """
        load csv into a numpy array
        parameter:
        ----------
        fileName, string
        rank_Start_bit, an integer, the first rank_start_bit columns are not used by the labeling

        return:
        ----------
        numpy array, 1D list of symbols
        """
        f = open(file_name, 'rb')
        header = f.readline().decode('utf-8') # get a string of the first line
        header = header.strip('\r\n')
        n_col = len(header.split(',')) - rank_start_bit 
        lines = f.readlines()
        n_row = len(lines)
        print(n_row, n_col)
        array = np.zeros((n_row, n_col))
        symbol_list = []
        for row_index, line in enumerate(lines):
            line = line.decode('utf-8')
            line = line.split(',')
            symbol_list = symbol_list + [line[0]]
            for col_index, item in enumerate(line[rank_start_bit:]):
                try:
                    array[row_index, col_index] = float(item)
                except: # when the value is missing
                    array[row_index, col_index] = 0
        f.close()
        return array, symbol_list

    def clusterWithAllLabels(self, n = 5):
        '''
        use all the dimension/feature to do clustering
        parameter:
        ----------
        n, an integer, defining the number of clusters

        return
        ---------
        labels, an array of cluster indices
        '''
        kmeans = KMeans(n_clusters=n, random_state=0).fit(self.array)
        return kmeans.labels_

    def createDict(self):
        """
        create a dictionary to store the symbol as key and the corresponding index as value.

        return
        ----------
        A dictionary with stock symbol as key and the corresponding index as value
        """
        symbolDict = {}
        for i, symbol in enumerate(self.symbol):
            symbolDict[symbol] = i
        return symbolDict

    def get(self):
        """
        return
        ---------
        list of symbol, list of labels
        """
        return self.symbol, self.labels

if __name__ == '__main__':
    lb = label()
    print('Testing ...')
    print('Tech stocks')
    for stock in ['AMD', 'INTC', 'TSM', 'AAPL', 'GOOGL', 'MSFT', 'FB', 'TSLA', 'NFLX']:
        print(stock + ' is in group: ' + str(lb.labels[lb.symbolDict[stock]]))
    
    print()
    print('Energy stocks')
    for stock in ['XOM', 'BP', 'CVX', 'TOT', 'SLB']:
        print(stock + ' is in group: ' + str(lb.labels[lb.symbolDict[stock]]))

    print()
    print('Financial stocks')
    for stock in ['JPM', 'BAC', 'C', 'WFC', 'PNC']:
        print(stock + ' is in group: ' + str(lb.labels[lb.symbolDict[stock]]))

    print()
    print('Airline stocks')
    for stock in ['AAL', 'UAL', 'DAL', 'LUV', 'JBLU']:
        print(stock + ' is in group: ' + str(lb.labels[lb.symbolDict[stock]]))