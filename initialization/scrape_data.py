import yahoo_fin.stock_info as si
import pandas as pd
import time
import os
import random
from urllib.error import HTTPError

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
        if len(ticker) > 0:
            while n < max_tries:
                try:
                    df = func(ticker)
                    break
                except (ValueError, AssertionError):
                    # Likely invalid symbol so skip ahead
                    print('Yahoo Reader failed to read: ' + ticker)
                    break
                except KeyError:
                    print("Yahoo Reader failed to read: {} because of Key Error".format(ticker))
                    break
                except IndexError:
                    print("Yahoo Reader failed to read: {} because of IndexError".format(ticker))
                    break
                except HTTPError as err:
                    if err.code == 404:
                        print("Yahoo Reader failed to read: {} because of HTTPError 404".format(ticker))
                        break
                    else:
                        pass
                except:
                    # Likely failed to connect to Yahoo
                    # print('Failed to connect to Yahoo.' +
                    #     ' Retry for the {} time.'.format(n+1))
                    # time.sleep(3)
                    # n += 1
                    # if n == max_tries:
                    #     raise Exception(
                    #         'Could not connect to Yahoo. Please try later.')
                    print("Skip: {}".format(ticker))
                    break
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
            key_stats = self.request_stats(tickers)
            key_stats = key_stats.transpose()
            key_stats.index = key_stats.index.rename("symbol")
            key_stats.to_csv(file_name)

    def save_prices_if_not_exist(self, tickers,
                                 folder_path='.',
                                 force_refresh=False):

        file_name = os.path.join(folder_path, "prices.csv")
        if force_refresh or not os.path.isfile(file_name):
            prices = self.request_prices(tickers)
            prices.to_csv(file_name, index=False)

    def save_financials_if_not_exist(self, tickers,
                                     folder_path='.',
                                     force_refresh=False):
        qtr_file_name = os.path.join(folder_path, "financials_qtr.csv")
        yr_file_name = os.path.join(folder_path, "financials_annual.csv")
        if force_refresh or not os.path.isfile(qtr_file_name):
            financials_qtr, financials_annual = self.request_financials(
                tickers)
            financials_qtr.to_csv(qtr_file_name)
            financials_annual.to_csv(yr_file_name)

    def save_data(self, tickers, key_stats=True, financials=True, prices=True,
                  folder_path='.', batch_size=20, force_refresh=False):
        tickers = sorted(tickers)
        for i in range(0, len(tickers), batch_size):
            batch_i = i // batch_size
            print("Collecting batch #{}".format(batch_i))
            batch_folder = os.path.join(folder_path, "batch_"+str(batch_i))
            os.makedirs(batch_folder, exist_ok=True)
            batch_tickers = tickers[i:i+batch_size]
            if key_stats:
                self.save_stats_if_not_exist(
                    batch_tickers, batch_folder, force_refresh)
            if financials:
                self.save_financials_if_not_exist(
                    batch_tickers, batch_folder, force_refresh)
            if prices:
                self.save_prices_if_not_exist(
                    batch_tickers, batch_folder, force_refresh)
            #time.sleep(random.random()*5+3)
            # if batch_i > 0 and batch_i % 10 == 0:
            #     print("Pause for 120 seconds...")
            #     time.sleep(120)

        self.combine_batches(folder_path)

    def combine_batches(self, folder_path):
        all_stats = []
        all_prices = []
        all_financials_q = []
        all_financials_y = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('stats.csv'):
                    all_stats.append(pd.read_csv(file_path, index_col=[0]))
                elif file.endswith('prices.csv'):
                    all_prices.append(pd.read_csv(
                        file_path, index_col=[0], parse_dates=True))
                elif file.endswith('_qtr.csv'):
                    all_financials_q.append(pd.read_csv(
                        file_path,   parse_dates=['date']))
                elif file.endswith('_annual.csv'):
                    all_financials_y.append(pd.read_csv(
                        file_path,  parse_dates=['date']))

        all_stats = pd.concat(all_stats)
        all_prices = pd.concat(all_prices)
        all_financials_q = pd.concat(all_financials_q)
        all_financials_y = pd.concat(all_financials_y)

        all_stats.to_csv(os.path.join(folder_path, "all_stats.csv"))
        all_prices.to_csv(os.path.join(folder_path, "all_prices.csv"))
        all_financials_q.to_csv(os.path.join(
            folder_path, "all_financials_q.csv"), index=False)
        all_financials_y.to_csv(os.path.join(
            folder_path, "all_financials_y.csv"), index=False)


def main():
    # get key stats, financial statements, and prices data of SP500 stocks
    tickers_nasdaq = set(si.tickers_nasdaq())
    tickers_other = set(si.tickers_other())
    tickers_sp500 = set(si.tickers_sp500())
    
    tickers_nasdaq_ = list(tickers_nasdaq - tickers_sp500)
    tickers_other_ = list(tickers_other - tickers_sp500)
    tickers_sp500 = list(tickers_sp500)

    yr = YahooReader()
    yr.save_data(tickers_nasdaq_, folder_path='data_nasdaq')
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

    yr.save_data(tickers, folder_path="data_test", force_refresh=False)


if __name__ == "__main__":
    main()
