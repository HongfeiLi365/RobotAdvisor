import pandas as pd
import re


def parse_pct(series):
    return series.str.replace("%", "").str.replace(",", "").astype('float').divide(100)


def parse_big_num(series):
    multiplier = pd.Series(index=series.index, dtype='float')
    multiplier.loc[series.str.contains('B') & ~series.isna()] = 1e9
    multiplier.loc[series.str.contains('M') & ~series.isna()] = 1e6
    num = series.str.extract(r'(\-*\d+\.*\d*)').astype('float')[0]
    series = num*multiplier
    return series


def split_camel(col_name):
    find_camel = re.compile(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')
    col_name = re.findall(find_camel, col_name)
    col_name = [s.lower() for s in col_name]
    col_name = "_".join(col_name)
    return col_name


def trim_tail(col_name):
    trim_pat = re.compile("\d*|(\(\w+\))")
    col_name = trim_pat.sub('', col_name).lower().strip()
    col_name = col_name.replace(' ', '_').replace('/', '_to_')
    return col_name


def clean_prices(file_path):
    prices = pd.read_csv(file_path)
    use_cols = ['symbol', 'date', 'open', 'high',
                'low', 'close', 'adjclose', 'volume']
    prices = prices.loc[:, use_cols]
    prices[['close', 'adjclose']] = prices.sort_values(["symbol", "date"]).groupby(
        "symbol")[['close', 'adjclose']].ffill().bfill()
    prices['volume'] = prices['volume'].fillna(0)
    prices.loc[prices.isna()['open']] = prices.loc[prices.isna()[
        'open']].fillna(method='bfill', axis=1)
    return prices


def clean_statistics(file_path):
    stats = pd.read_csv(file_path)
    use_cols = ['symbol', 'Most Recent Quarter (mrq)',
                'Payout Ratio 4', 'Profit Margin',
                'Operating Margin (ttm)', 'Return on Assets (ttm)',
                'Return on Equity (ttm)', 'Revenue Per Share (ttm)',
                'Quarterly Revenue Growth (yoy)', 'EBITDA',
                'Diluted EPS (ttm)',
                'Quarterly Earnings Growth (yoy)',
                'Total Cash Per Share (mrq)',
                'Total Debt/Equity (mrq)', 'Current Ratio (mrq)',
                'Operating Cash Flow (ttm)',
                ]
    stats = stats.loc[:, use_cols]
    stats.columns = [trim_tail(s) for s in use_cols]

    pct_col = ['payout_ratio', 'profit_margin',
               'operating_margin', 'return_on_assets', 'return_on_equity',
               'quarterly_revenue_growth', 'quarterly_earnings_growth']
    for col in pct_col:
        stats[col] = parse_pct(stats[col])

    num_col = ['ebitda', 'operating_cash_flow']
    for col in num_col:
        stats[col] = parse_big_num(stats[col])

    stats['most_recent_quarter'] = pd.to_datetime(
        stats['most_recent_quarter']).dt.strftime("%Y-%m-%d").fillna('2099-12-31')

    stats = stats.dropna(subset=['symbol'], how='any')
    stats = stats.fillna(-999)
    return stats


def clean_financials(file_path):
    financials = pd.read_csv(file_path)
    new_cols = [split_camel(s) for s in financials.columns]
    financials.columns = new_cols
    financials = financials.dropna(how='all', axis=1)
    financials = financials.drop(
        ['net_income.1', 'minority_interest.1'], axis=1)
    financials = financials.dropna(subset=['symbol', 'date'], how='any')
    financials = financials.fillna(0)
    return financials


if __name__ == "__main__":

    statistics = clean_statistics("data_sp500/all_stats.csv")
    financials = clean_financials("data_sp500/all_financials_q.csv")
    prices = clean_prices("data_sp500/all_prices.csv")

    statistics.to_csv("data_sp500/all_stats_clean.csv", index=False)
    financials.to_csv("data_sp500/all_financials_clean.csv", index=False)
    prices.to_csv("data_sp500/all_prices_clean.csv", index=False)

