import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

sys.path.append('../flaskblog')
import neo4j_db_utils as n4j

class Label:
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


def main():
    """
    first run stock clustering, then populate the neo4j database with the labels
    default number of group is 5, so the labels are 0,1,2,3,4
    """
    CSV_FILE = 'data/features.csv'
    lb = Label(source=CSV_FILE)
    symbolList, labelList = lb.get()
    for i, symbol in enumerate(symbolList):
        group = str(labelList[i])
        n4j.execute_query("MATCH (n:stock) WHERE n.symbol = '%s' SET n.label = %s"%(symbol, group))

    # load the volume attribute into the neo4j database
    loaded_feature = pd.read_csv(CSV_FILE)
    for index, entry in loaded_feature.iterrows():
        symbol = entry['symbol']
        volume = entry['volume']
        try:
            volume = int(volume)
        except:
            print('Error: Volume of stock ' + symbol + ' cannot be converted into integer.')
        n4j.execute_query("MATCH (n:stock) WHERE n.symbol = '%s' SET n.volume = %s"%(symbol, volume))

if __name__ == '__main__':
    main()
