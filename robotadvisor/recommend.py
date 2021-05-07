import numpy as np
import sys
import random
from .neo4j_db_utils import execute_query

def recommend(symbol_list, n = 3, n_label = 5):
    """
    first pull stocks with the targeted label into a pool from the stock with the largest volume to the leaset volume.
    then, recommend stock from the largest volume stock to the least

    parameter:
    ----------
    symbol_list, a list of symbols of stocks in the current portfolio
    n, an integer, number of stocks to be recommended

    return
    ----------
    a list of stock symbols, the last n elements are the newly added stocks
    """
    current_num_stocks = len(symbol_list)
    status_counter_array = np.zeros(n_label)
    # count the number of stocks in each label group
    for stock in symbol_list:
        row = execute_query("MATCH (n:stock) WHERE n.symbol = '%s' return n.label"%(stock))
        try:
            label = int(row[0].data()['n.label']) # unwrap the return of neo4j query
        except:
            # randomly assign a label when the stock is not clustered
            label = random.randint(0, n_label - 1)
        status_counter_array[label] = status_counter_array[label] + 1
    # start to fill stocks into the minimum label group
    while(n > 0):
        label_to_get = np.argmin(status_counter_array)
        rows = execute_query("MATCH (n:stock) WHERE n.label = %s AND n.volume > 0 return n.symbol order by n.volume DESC limit 200"%(label_to_get))
        unique_stock_added = False
        while(not unique_stock_added):
            row = rows.pop(0)
            symbol = row.data()['n.symbol']
            if symbol not in symbol_list:
                unique_stock_added = True
                symbol_list = symbol_list + [symbol]
        status_counter_array[label_to_get] = status_counter_array[label_to_get] + 1
        n = n - 1
    return symbol_list

if __name__ == '__main__':
    test_symbol_list = ['XOM', 'BP', 'CVX', 'TOT', 'SLB']
    print(recommend(test_symbol_list))
