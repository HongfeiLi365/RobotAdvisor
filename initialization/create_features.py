import pandas as pd
import numpy as np
import pandas_ta as ta
import os

def get_stochRSI(closes, **kwargs):
    return ta.stochrsi(closes, **kwargs).iloc[:, 0]

def load_data(data_folder):
    statistics = pd.read_csv(
        os.path.join(data_folder, "all_stats_clean.csv"), index_col=[0])
    financials = pd.read_csv(os.path.join(data_folder, "all_financials_clean.csv"))
    prices = pd.read_csv(
        os.path.join(data_folder, "all_prices_clean.csv")
        ).sort_values(['symbol', 'date'])
    return statistics, financials, prices

def get_stats_features(statistics, col):
    return statistics[col].replace(-999, np.nan)

def add_gross_margin(financials, features):
    features['revenue'] = financials.groupby(
        'symbol')['total_revenue'].sum().replace(0, np.nan)
    features['gross_profit'] = financials.groupby(
        'symbol')['gross_profit'].sum().replace(0, np.nan)
    features['gross_margin'] = features['gross_profit'] / features['revenue']
    return features

def add_price_to_sales(prices, features):
    features['price'] = prices.groupby('symbol')['close'].last()
    features['price_to_sales'] = features['price'] * \
        features['shares_outstanding'] / features['revenue']
    return features

def add_volume(prices, features):
    vol = prices.pivot_table(index='date', columns='symbol', values='volume')
    features['volume'] = vol.rolling(252, min_periods=0).mean().ffill().iloc[-1]
    return features

def add_return(closes, features):
    features['return_1m'] = closes.pct_change(
        20, fill_method=None).ffill().iloc[-1]
    features['return_6m'] = closes.pct_change(
        120, fill_method=None).ffill().iloc[-1]
    return features

def add_stochrsi(closes, features):
    closes_m = closes.resample('M').last().iloc[:-1]
    stochrsi_m = closes_m.apply(get_stochRSI, length=10, rsi_length=14)
    features['stochrsi'] = stochrsi_m.iloc[-1]
    return features

def rank_features(features):
    features = features[['current_ratio', 'gross_margin', 'operating_margin',
                        'debt_to_equity', 'price_to_sales', 'volume',
                        'return_1m', 'return_6m', 'stochrsi']]

    for col in features.columns:
        features[col+'_rank'] = features[col].rank(pct=True)

    for col in ['debt_to_equity', 'price_to_sales']:
        features.loc[:,col+'_rank'] = features[col].rank(pct=True, ascending=False)

    features.iloc[:,9:] = features.iloc[:,9:].fillna(0) 
    return features


def main(data_folder='data'):
    statistics, financials, prices = load_data(data_folder)

    features = pd.DataFrame(
        index=statistics.index.intersection(financials['symbol'].unique())
        .intersection(prices['symbol'].unique()))

    features['current_ratio'] = get_stats_features(statistics, 'current_ratio')
    features['operating_margin'] = get_stats_features(statistics, 'operating_margin')
    features['debt_to_equity'] = get_stats_features(statistics,'total_debt_to_equity')
    features['shares_outstanding'] = get_stats_features(statistics,'shares_outstanding' )

    features = add_gross_margin(financials, features)
    features = add_price_to_sales(prices, features)

    closes = prices.pivot_table(index='date', columns='symbol', values='adjclose')
    closes.index = pd.DatetimeIndex(closes.index)

    features = add_volume(prices, features)
    features = add_return(closes, features)
    features = add_stochrsi(closes, features)

    features = rank_features(features)
    features = features.sort_index()

    features.to_csv(os.path.join(data_folder, "features.csv"))


if __name__ == "__main__":
    main(data_folder="data")