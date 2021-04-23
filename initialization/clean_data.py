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
                'Shares Outstanding 5',
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

    num_col = ['ebitda', 'operating_cash_flow', 'shares_outstanding']
    for col in num_col:
        stats[col] = parse_big_num(stats[col])

    stats['most_recent_quarter'] = pd.to_datetime(
        stats['most_recent_quarter']).dt.strftime("%Y-%m-%d")

    stats = stats.dropna(subset=['symbol', 'most_recent_quarter'], how='any')
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


def concat_univ(data='stats', output_dir='.'):
    file_name = 'all_{}_clean.csv'.format(data)
    df_list = []
    for folder in ['data_sp500', 'data_nasdaq', 'data_other']:
        df_list.append(pd.read_csv(os.path.join(folder, file_name)))
    df = pd.concat(df_list)
    if data == 'stats':
        df = df.sort_values('most_recent_quarter').drop_duplicates(
            subset=['symbol'], keep='last')
    else:
        df = df.sort_values(['symbol', 'date']).drop_duplicates(
            subset=['symbol', 'date'], keep='last')
    df.to_csv(os.path.join(output_dir, file_name), index=False)


def keep_newest(prices, n=300):
    return prices.sort_values(['symbol', 'date'], ascending=False).groupby('symbol').head(n)


def financials_subset(financials):
    financials = financials[[
        'symbol', 'date',
        'income_before_tax',
        'net_income',
        'gross_profit',
        'ebit',
        'operating_income',
        'total_revenue',
        'total_operating_expenses',
        'cost_of_revenue',
        'total_assets',
        'cash',
        'total_current_liabilities',
        'total_current_assets']]
    return financials


if __name__ == "__main__":

    for folder in ['data_sp500', 'data_nasdaq', 'data_other']:
        statistics = clean_statistics(os.path.join(folder, "all_stats.csv"))
        financials = clean_financials(
            os.path.join(folder, "all_financials_q.csv"))
        prices = clean_prices(os.path.join(folder, "all_prices.csv"))

        statistics.to_csv(os.path.join(
            folder, "all_stats_clean.csv"), index=False)
        financials.to_csv(os.path.join(
            folder, "all_financials_clean.csv"), index=False)
        prices.to_csv(os.path.join(
            folder, "all_prices_clean.csv"), index=False)

    os.makedirs('data', exist_ok=True)
    for data in ['stats', 'financials', 'prices']:
        concat_univ(data, 'data')

    statistics = pd.read_csv("data/all_stats_clean.csv", index_col=[0])
    financials = pd.read_csv("data/all_financials_clean.csv")
    prices = pd.read_csv("data/all_prices_clean.csv")

    inds = statistics.index.intersection(
        prices['symbol'].unique()).intersection(financials['symbol'])

    statistics = statistics.loc[inds]
    financials = financials[financials['symbol'].isin(inds)]
    financials = financials_subset(financials)

    prices = prices[prices['symbol'].isin(inds)]
    prices = keep_newest(prices, 300).sort_values(['symbol', 'date'])

    statistics.to_csv("data/all_stats_clean_small.zip")
    financials.to_csv("data/all_financials_clean_small.zip", index=False)
    prices.to_csv("data/all_prices_clean_small.zip", index=False)
