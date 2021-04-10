import labelStock
import sys
sys.path.append('../flaskblog')
import neo4j_db_utils as n4j
def main():
    """
    first run stock clustering, then populate the neo4j database with the labels
    default number of group is 5, so the labels are 0,1,2,3,4
    """
    lb = labelStock.label()
    symbolList, labelList = lb.get()
    for i, symbol in enumerate(symbolList):
        group = str(labelList[i])
        n4j.execute_query("MATCH (n:stock) WHERE n.symbol = '%s' SET n.label = %s"%(symbol, group))

if __name__ == '__main__':
    main()