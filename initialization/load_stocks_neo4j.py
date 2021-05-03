from neo4j import GraphDatabase
import pandas as pd


class loadStocks:
    '''
    load statistics of the stocks into the database.
    The input of this class should be a dictionary of stocks.
    key: symbol
    attributes: symbol, beta, 52WeekChange, ...
    '''

    def __init__(self, stocks, clear=False):
        '''
        make connection to the database.
        '''
        uri = "bolt://127.0.0.1:7687"
        user = "neo4j"
        password = "fourtune1234"
        self.stocks = stocks
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        if clear:
            self.clear_stocks()
        self.create_stocks()

    def create_stock(self, tx, symbol, most_recent_quarter, shares_outstanding,
                     payout_ratio, profit_margin, operating_margin,
                     return_on_assets, return_on_equity, revenue_per_share,
                     quarterly_revenue_growth, ebitda, diluted_eps,
                     quarterly_earnings_growth, total_cash_per_share,
                     total_debt_to_equity, current_ratio, operating_cash_flow):
        '''
        it defines the format of the stock node, for example how many attributes are used.
        '''
        tx.run("CREATE (:stock {symbol:$symbol, most_recent_quarter:$most_recent_quarter, shares_outstanding:$shares_outstanding, payout_ratio:$payout_ratio, profit_margin:$profit_margin, operating_margin:$operating_margin, return_on_equity:$return_on_equity, return_on_assets:$return_on_assets, revenue_per_share:$revenue_per_share, quarterly_revenue_growth:$quarterly_revenue_growth, ebitda:$ebitda, diluted_eps:$diluted_eps, quarterly_earnings_growth:$quarterly_earnings_growth, total_cash_per_share:$total_cash_per_share, total_debt_to_equity:$total_debt_to_equity, current_ratio:$current_ratio, operating_cash_flow:$operating_cash_flow})",
               symbol=symbol,
               most_recent_quarter=most_recent_quarter,
               shares_outstanding=shares_outstanding,
               payout_ratio=payout_ratio,
               profit_margin=profit_margin,
               operating_margin=operating_margin,
               return_on_assets=return_on_assets,
               return_on_equity=return_on_equity,
               revenue_per_share=revenue_per_share,
               quarterly_revenue_growth=quarterly_revenue_growth,
               ebitda=ebitda, diluted_eps=diluted_eps,
               quarterly_earnings_growth=quarterly_earnings_growth,
               total_cash_per_share=total_cash_per_share,
               total_debt_to_equity=total_debt_to_equity,
               current_ratio=current_ratio,
               operating_cash_flow=operating_cash_flow)

    def create_stocks(self):
        '''
        insert all items from the dict into the database
        '''
        with self.driver.session() as session:
            for symbol, row in self.stocks.iterrows():
                session.write_transaction(
                    self.create_stock, symbol,
                    row.iloc[0],
                    row.iloc[1],
                    row.iloc[2],
                    row.iloc[3],
                    row.iloc[4],
                    row.iloc[5],
                    row.iloc[6],
                    row.iloc[7],
                    row.iloc[8],
                    row.iloc[9],
                    row.iloc[10],
                    row.iloc[11],
                    row.iloc[12],
                    row.iloc[13],
                    row.iloc[14],
                    row.iloc[15])
        self.driver.close()

    def cypher_clear_stocks(self, tx):
        '''
        remove all the stacks in the database. This option can fail if there are too many nodes.
        Then try: rm -rf data/graph.db
        '''
        tx.run("MATCH (n:stock) DELETE n")

    def clear_stocks(self):
        '''
        remove all the stacks in the database. This option can fail if there are too many nodes.
        Then try: rm -rf data/graph.db
        '''
        with self.driver.session() as session:
            session.write_transaction(self.cypher_clear_stocks)
        self.driver.close()


def convert(s):
    '''
    convert the element in csv into floats
    '''
    if '-' not in s:  # date
        return float(s)
    else:
        return s


if __name__ == '__main__':
    '''
    this step depends on the format of the stocks
    '''
    stocks = pd.read_csv("data/all_stats_clean_small.zip", index_col=[0])
    lds = loadStocks(stocks, False)
