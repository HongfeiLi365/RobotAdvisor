import yahoo_fin.stock_info as si
import pandas as pd
import time
import os


class YahooReader():
    """
    Collect and format data from Yahoo finance using yahoo_fin.
    https://github.com/atreadw1492/yahoo_fin
    """

    def _try_request(self, func, ticker, max_tries=3):
        """
        Handle HTTP errors
        """
        n = 0
        df = None
        while n < max_tries:
            try:
                df = func(ticker)
                break
            except ValueError:
                # Likely invalid symbol so skip ahead
                print('Yahoo Reader failed to read: ' + ticker)
                break
            except:
                # Likely failed to connect to Yahoo
                print('Failed to connect to Yahoo.' +
                      ' Retry for the {} time.'.format(n+1))
                time.sleep(3)
                n += 1
                if n == max_tries:
                    raise Exception('Could not connect to Yahoo.')
        return df

    def request_stats(self, tickers):
        """
        Requests and reformats key statistics. 
        """
        all_stats = []
        for ticker in tickers:
            stats = self._try_request(si.get_stats, ticker=ticker)
            if stats is None:
                continue
            stats.index = stats['Attribute']
            all_stats.append(stats.drop(['Attribute'], axis=1).rename(
                columns={'Value': ticker}))
        all_stats = pd.concat(all_stats, axis=1)
        return all_stats

    def request_financials(self, tickers):
        """
        Requests and reformats financial statements. Creates the following
        class attributes: income_stmt_qtr, income_stmt_annual, 
        balance_sheet_qtr, balance_sheet_annual, cash_flow_qtr, 
        cash_flow_annual.
        """
        stmt_dict = {
            'quarterly_income_statement': [],
            'quarterly_balance_sheet': [],
            'quarterly_cash_flow': [],
            'yearly_income_statement': [],
            'yearly_balance_sheet': [],
            'yearly_cash_flow': []
        }
        for ticker in tickers:
            stmts = self._try_request(si.get_financials, ticker=ticker)
            if stmts is None:
                continue
            for stmt_type in stmts.keys():
                df = stmts[stmt_type].T
                df.index = pd.MultiIndex.from_product([[ticker], df.index])
                stmt_dict[stmt_type].append(df)

        def _concat_and_fmt(stmt_type):
            df = pd.concat(stmt_dict[stmt_type])
            df.index.names = ['symbol', 'date']
            df.columns.name = 'field'
            return df.sort_index(level=1).sort_index(level=0)

        income_stmt_qtr = _concat_and_fmt('quarterly_income_statement')
        income_stmt_annual = _concat_and_fmt('yearly_income_statement')
        balance_sheet_qtr = _concat_and_fmt('quarterly_balance_sheet')
        balance_sheet_annual = _concat_and_fmt('yearly_balance_sheet')
        cash_flow_qtr = _concat_and_fmt('quarterly_cash_flow')
        cash_flow_annual = _concat_and_fmt('yearly_cash_flow')

        financials_qtr = pd.concat(
            [income_stmt_qtr,
             balance_sheet_qtr,
             cash_flow_qtr],
            axis=1)

        financials_annual = pd.concat(
            [income_stmt_annual,
             balance_sheet_annual,
             cash_flow_annual],
            axis=1)
        return financials_qtr, financials_annual

    def request_prices(self, tickers):
        """
        Get prices data, including date, open, high, low, close, adjclose, 
        volume, and symbol.
        """
        all_prices = []
        for ticker in tickers:
            prices = self._try_request(si.get_data, ticker=ticker)
            if prices is None:
                continue
            prices = prices.reset_index().rename(
                {'index': 'date', 'ticker': 'symbol'}, axis=1)
            all_prices.append(prices)
        all_prices = pd.concat(all_prices)
        return all_prices

    def save_stats_if_not_exist(self, tickers,
                                folder_path='.',
                                force_refresh=False):
        file_name = os.path.join(folder_path, "stats.csv")
        if force_refresh or not os.path.isfile(file_name):
            self.key_stats = self.request_stats(tickers)
            self.key_stats.transpose().to_csv(file_name)

    def save_prices_if_not_exist(self, tickers,
                                 folder_path='.',
                                 force_refresh=False):

        file_name = os.path.join(folder_path, "prices.csv")
        if force_refresh or not os.path.isfile(file_name):
            self.prices = self.request_prices(tickers)
            self.prices.to_csv(file_name, index=False)

    def save_financials_if_not_exist(self, tickers,
                                     folder_path='.',
                                     force_refresh=False):
        qtr_file_name = os.path.join(folder_path, "financials_qtr.csv")
        if force_refresh or not os.path.isfile(qtr_file_name):
            self.financials_qtr, self.financials_annual = self.request_financials(
                tickers)
            self.financials_qtr.to_csv(file_name)
            yr_file_name = os.path.join(folder_path, "financials_annual.csv")
            financials_annual.to_csv(yr_file_name)

    def save_data(self, tickers, key_stats=True, financials=True, prices=True,
                  folder_path='.', force_refresh=False):

        os.makedirs(folder_path, exist_ok=True)
        if key_stats:
            self.collect_stats_if_not_exist(tickers,
                                            folder_path, force_refresh)
        if financials:
            self.collect_financials_if_not_exist(tickers,
                                                 folder_path, force_refresh)
        if prices:
            self.collect_prices_if_not_exist(tickers,
                                             folder_path, force_refresh)


def main():
    # get key stats, financial statements, and prices data of SP500 stocks
    yr = YahooReader(si.tickers_sp500())
    yr.collect_data(folder_path='data_sp500')
    print("All Done!")


def test():
    # Test cases
    pd.set_option('display.max_rows', 5)
    tickers = ['AAPL', 'TSLA', 'BAC', 'DE']
    yr = YahooReader()
    print(yr.request_stats(tickers))
    print(yr.request_financials(tickers)[0])
    print(yr.request_prices(tickers))

    tickers = ['AAPL', 'ABC.DEF&GHI']
    print(yr.request_stats(tickers))


if __name__ == "__main__":
    test()
