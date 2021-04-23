import mysql.connector
import pandas as pd
import os
import time

from utils import insert_dataframe


def create_tables():
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

    mycursor.execute(
        """
        CREATE OR REPLACE VIEW view_sma200 AS
        SELECT symbol, AVG(close) AS sma200
        FROM (
            SELECT 
                symbol, date, close, 
                NTH_VALUE(date, 200) OVER (
                        PARTITION BY symbol
                        ORDER BY date DESC 
                        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                    ) AS date200
            FROM prices
        ) AS p
        WHERE date >= date200
        GROUP BY symbol;
        """
    )

    mycursor.execute(
        """
        CREATE OR REPLACE VIEW view_gross_margin AS
        SELECT 
            symbol,
            cast(profit AS FLOAT) / nullif(revenue, 0) AS gross_margin,
            revenue
        FROM (
            SELECT
                symbol,
                SUM(gross_profit) AS profit,
                SUM(total_revenue) AS revenue
            FROM  financials
            GROUP BY symbol
        ) AS f;
        """
    )

    mycursor.execute(
        """
        CREATE OR REPLACE VIEW view_latest_price AS
        SELECT symbol,  max(close) as close
        FROM (
            SELECT 
                symbol, date, close, 
                MAX(date) OVER (
                        PARTITION BY symbol
                        ORDER BY date DESC 
                        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                    ) AS max_date
            FROM prices
        ) AS p
        WHERE date = max_date
        GROUP BY symbol;
        """
    )

    mycursor.execute(
        """
        DROP TABLE IF EXISTS screening;
        CREATE TABLE screening AS (
            SELECT
                symbol,
                (close / nullif(sma200,0)) AS sma200,
                market_cap,
                (market_cap / nullif(revenue, 0)) AS price_to_sales,
                gross_margin
            FROM (
                SELECT
                    s.symbol,
                    s.shares_outstanding,
                    vp.close,
                    s.shares_outstanding * vp.close AS market_cap,
                    vg.revenue,
                    vg.gross_margin,
                    vs.sma200
                FROM statistics AS s
                INNER JOIN view_latest_price AS vp ON s.symbol = vp.symbol
                INNER JOIN view_gross_margin AS vg ON s.symbol = vg.symbol
                INNER JOIN view_sma200 AS vs ON s.symbol = vs.symbol
            ) AS t
        );
        """
    )

    mycursor.close()
    mydb.close()


def create_indexes():
    mydb = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database="robotadvisor"
    )

    mycursor = mydb.cursor()

    mycursor.execute("CREATE INDEX idx_sma200 ON screening (sma200)")
    mycursor.execute("CREATE INDEX idx_market_cap ON screening (market_cap)")
    mycursor.execute("CREATE INDEX idx_ps ON screening (price_to_sales)")
    mycursor.execute(
        "CREATE INDEX idx_gross_margin ON screening (gross_margin)")
    mycursor.execute(
        "CREATE INDEX idx_profit_margin ON statistics (profit_margin)")
    mycursor.execute(
        "CREATE INDEX idx_operating_margin ON statistics (operating_margin)")

    mycursor.close()
    mydb.close()


if __name__ == "__main__":
    create_tables()
    time.sleep(20)
    create_indexes()
