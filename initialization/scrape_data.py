import yahoo_fin.stock_info as si
import pandas as pd
import time


class YahooReader():
    """
    Collect and format data from Yahoo finance using yahoo_fin.
    https://github.com/atreadw1492/yahoo_fin
    """

    def __init__(self, tickers, key_stats=True, stmts=False, prices=False):
        """Initialize reader and collect data.

        Parameters
        ----------
        tickers: str | [str]
            Tickers of stocks to include.
        key_stats: bool; def. True
            Pull key statistics.
        stmts: bool; def. False
            Pull financial statements.
        """
        self.tickers = [tickers] if type(tickers) is str else tickers

        self.key_stats = self._req_stats()

        if stmts:
            self._req_financials()

        if prices:
            self.prices = self._req_prices()

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
                      ' Retry for the {} time.'.format(n))
                time.sleep(3)
                n += 1
                if n == max_tries:
                    raise Exception('Could not connect to Yahoo.')
        return df

    def _req_stats(self):
        """
        Requests and reformats key statistics. 
        """
        all_stats = []
        for ticker in self.tickers:
            stats = self._try_request(si.get_stats, ticker=ticker)
            if stats is None:
                continue
            stats.index = stats['Attribute']
            all_stats.append(stats.drop(['Attribute'], axis=1).rename(
                columns={'Value': ticker}))
        all_stats = pd.concat(all_stats, axis=1)
        return all_stats

    def _req_financials(self):
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
        for ticker in self.tickers:
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

        self.income_stmt_qtr = _concat_and_fmt('quarterly_income_statement')
        self.income_stmt_annual = _concat_and_fmt('yearly_income_statement')
        self.balance_sheet_qtr = _concat_and_fmt('quarterly_balance_sheet')
        self.balance_sheet_annual = _concat_and_fmt('yearly_balance_sheet')
        self.cash_flow_qtr = _concat_and_fmt('quarterly_cash_flow')
        self.cash_flow_annual = _concat_and_fmt('yearly_cash_flow')

    def _req_prices(self):
        all_prices = []
        for ticker in self.tickers:
            prices = self._try_request(si.get_data, ticker=ticker)
            if prices is None:
                continue
            prices = prices.reset_index().rename({'index':'date', 'ticker':'symbol'},axis=1)
            all_prices.append(prices)
        all_prices = pd.concat(all_prices)
        return all_prices


def test():
    # Test cases
    pd.set_option('display.max_rows', 5)
    yr = YahooReader(['AAPL', 'TSLA', 'BAC', 'DE'], stmts=True, prices=True)
    print(yr.balance_sheet_qtr)
    print(yr.key_stats.loc['Current Ratio (mrq)'])
    print(yr.prices)
    yr2 = YahooReader(['QCOM'], key_stats=False, stmts=True)
    print(yr2.income_stmt_annual)
    yr3 = YahooReader(['ACN', 'ZM', 'BA'])
    print(yr3.key_stats)
    yr4 = YahooReader('FB')
    print(yr4.key_stats)
    yr5 = YahooReader(['AAPL', 'ABC.DEF&GHI'])
    print(yr5.key_stats)


if __name__ == "__main__":
    test()
