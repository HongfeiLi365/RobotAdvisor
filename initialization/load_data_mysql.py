import mysql.connector
import pandas as pd
import os

from utils import insert_dataframe


def main():
    mydb = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS")
    )

    mycursor = mydb.cursor()

    mycursor.execute("CREATE DATABASE IF NOT EXISTS robotadvisor")

    mydb = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database="robotadvisor"
    )

    mycursor = mydb.cursor()

    mycursor.execute("DROP TABLE IF EXISTS prices, statistics, financials")

    mycursor.execute(
        "CREATE TABLE statistics ("
        "symbol VARCHAR(10), "
        "most_recent_quarter DATE, "
        "shares_outstanding BIGINT, "
        "payout_ratio FLOAT, profit_margin FLOAT, "
        "operating_margin FLOAT, return_on_assets FLOAT, "
        "return_on_equity FLOAT, revenue_per_share FLOAT, "
        "quarterly_revenue_growth FLOAT, ebitda BIGINT, diluted_eps FLOAT, "
        "quarterly_earnings_growth FLOAT, total_cash_per_share FLOAT, "
        "total_debt_to_equity FLOAT, current_ratio FLOAT, "
        "operating_cash_flow BIGINT, "
        "PRIMARY KEY(symbol)"
        ")"
    )

    mycursor.execute(
        "CREATE TABLE prices ("
        "symbol VARCHAR(10), "
        "date DATE, "
        "open FLOAT, high FLOAT, low FLOAT, "
        "close FLOAT, adjclose FLOAT, volume BIGINT, "
        "PRIMARY KEY(symbol, date), "
        "FOREIGN KEY (symbol) REFERENCES statistics(symbol)"
        ")"
    )

    mycursor.execute(
        "CREATE TABLE financials ("
        "symbol VARCHAR(10), "
        "date DATE, "
        "income_before_tax BIGINT, "
        "net_income BIGINT, "
        "gross_profit BIGINT, "
        "ebit BIGINT, "
        "operating_income BIGINT, "
        "total_revenue BIGINT, "
        "total_operating_expenses BIGINT, "
        "cost_of_revenue BIGINT, "
        "total_assets BIGINT, "
        "cash BIGINT, "
        "total_current_liabilities BIGINT, "
        "total_current_assets BIGINT, "
        "PRIMARY KEY(symbol, date), "
        "FOREIGN KEY (symbol) REFERENCES statistics(symbol)"
        ")"
    )

    statistics = pd.read_csv("data/all_stats_clean_small.zip")
    financials = pd.read_csv("data/all_financials_clean_small.zip")
    prices = pd.read_csv("data/all_prices_clean_small.zip")

    insert_dataframe(mydb, statistics, 'statistics')
    insert_dataframe(mydb, financials, 'financials')
    insert_dataframe(mydb, prices, 'prices', batch_size=10000)


if __name__ == "__main__":
    main()
