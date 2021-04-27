import labelStock
import sys
import pandas as pd
sys.path.append('../flaskblog')
import neo4j_db_utils as n4j
def main():
    """
    first run stock clustering, then populate the neo4j database with the labels
    default number of group is 5, so the labels are 0,1,2,3,4
    """
    CSV_FILE = 'features.csv'
    lb = labelStock.label()
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