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
            cast(profit AS FLOAT) / revenue AS gross_margin,
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
        SELECT symbol, close
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
                (close - sma200) / sma200 AS sma200,
                market_cap,
                (market_cap / revenue) AS price_to_sales,
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

    mycursor.execute(
        """
        CREATE INDEX idx_sma200 ON screening (sma200);
        CREATE INDEX idx_market_cap ON screening (market_cap);
        CREATE INDEX idx_ps ON screening (price_to_sales);
        CREATE INDEX idx_gross_margin ON screening (gross_margin);
        CREATE INDEX idx_profit_margin ON statistics (profit_margin);
        CREATE INDEX idx_operating_margin ON statistics (operating_margin);
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_cap_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_cap_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'Micro(<$300mln)' THEN
                    SELECT min(market_cap) 
                    INTO lower_bound
                    FROM screening;
                    SET upper_bound = 3e8;
                WHEN 'Small($300mln~$2bln)' THEN
                    SET lower_bound = 3e8;
                    SET upper_bound = 2e9;
                WHEN 'Mid($2bln~$10bln)' THEN
                    SET lower_bound = 2e9;
                    SET upper_bound = 1e10;
                WHEN 'Large(>$10bln)' THEN
                    SET lower_bound =1e10;
                    SELECT MAX(market_cap)
                    INTO upper_bound
                    FROM screening;
                ELSE
                    SELECT MIN(market_cap), max(market_cap) 
                    INTO lower_bound, upper_bound
                    FROM screening;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_sma_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_sma_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'Price above SMA200' THEN
                    SELECT max(sma200)
                    INTO upper_bound
                    FROM screening;
                    SET lower_bound = 0;
                WHEN 'Price below SMA200' THEN
                    SELECT min(sma200)
                    INTO lower_bound
                    FROM screening;
                    SET upper_bound = 0;
                ELSE
                    SELECT MIN(sma200), max(sma200) 
                    INTO lower_bound, upper_bound
                    FROM screening;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_ps_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_ps_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'High(>10)' THEN
                    SELECT max(price_to_sales)
                    INTO upper_bound
                    FROM screening;
                    SET lower_bound = 10;
                WHEN 'Low(<1)' THEN
                    SELECT min(price_to_sales)
                    INTO lower_bound
                    FROM screening;
                    SET upper_bound = 1;
                WHEN 'Under 10' THEN
                    SELECT min(price_to_sales)
                    INTO lower_bound
                    FROM screening;
                    SET upper_bound = 10;
                ELSE
                    SELECT MIN(price_to_sales), max(price_to_sales) 
                    INTO lower_bound, upper_bound
                    FROM screening;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_gm_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_gm_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'Positive(>0%)' THEN
                    SELECT max(gross_margin)
                    INTO upper_bound
                    FROM screening;
                    SET lower_bound = 0;
                WHEN 'Negative(<0%)' THEN
                    SELECT min(gross_margin)
                    INTO lower_bound
                    FROM screening;
                    SET upper_bound = 0;
                WHEN 'High(>50%)' THEN
                    SELECT max(gross_margin)
                    INTO upper_bound
                    FROM screening;
                    SET lower_bound = 0.5;
                ELSE
                    SELECT MIN(gross_margin), max(gross_margin) 
                    INTO lower_bound, upper_bound
                    FROM screening;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_pm_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_pm_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'Positive(>0%)' THEN
                    SELECT max(profit_margin)
                    INTO upper_bound
                    FROM statistics;
                    SET lower_bound = 0;
                WHEN 'Negative(<0%)' THEN
                    SELECT min(profit_margin)
                    INTO lower_bound
                    FROM statistics;
                    SET upper_bound = 0;
                WHEN 'High(>20%)' THEN
                    SELECT max(profit_margin)
                    INTO upper_bound
                    FROM statistics;
                    SET lower_bound = 0.2;
                ELSE
                    SELECT MIN(profit_margin), max(profit_margin) 
                    INTO lower_bound, upper_bound
                    FROM statistics;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS get_om_range;

        DELIMITER $$ 

        CREATE PROCEDURE get_om_range(
            IN  option_str  VARCHAR(255),
            out lower_bound FLOAT,
            out upper_bound FLOAT
        ) 
        BEGIN
            CASE option_str
                WHEN 'Positive(>0%)' THEN
                    SELECT max(operating_margin)
                    INTO upper_bound
                    FROM statistics;
                    SET lower_bound = 0;
                WHEN 'Negative(<0%)' THEN
                    SELECT min(operating_margin)
                    INTO lower_bound
                    FROM statistics;
                    SET upper_bound = 0;
                WHEN 'High(>25%)' THEN
                    SELECT max(operating_margin)
                    INTO upper_bound
                    FROM statistics;
                    SET lower_bound = 0.25;
                WHEN 'Very Negative(<-20%)' THEN
                    SELECT min(operating_margin)
                    INTO lower_bound
                    FROM statistics;
                    SET upper_bound = -0.2;
                ELSE
                    SELECT MIN(operating_margin), max(operating_margin) 
                    INTO lower_bound, upper_bound
                    FROM statistics;
            END CASE;

        END $$ 

        DELIMITER ;
        """
    )

    mycursor.execute(
        """
        DROP PROCEDURE IF EXISTS filter_stocks;

        DELIMITER $$

        CREATE PROCEDURE filter_stocks(
            IN str_cap VARCHAR(255),
            IN str_sma VARCHAR(255),
            IN str_ps VARCHAR(255),
            IN str_gm VARCHAR(255),
            IN str_pm VARCHAR(255),
            IN str_om VARCHAR(255)
        ) 
        BEGIN
            DECLARE
                min_cap, max_cap,
                min_sma, max_sma,
                min_ps, max_ps,
                min_gm, max_gm,
                min_pm, max_pm,
                min_om, max_om FLOAT DEFAULT 0.0;

            CALL get_cap_range(str_cap, @min_cap, @max_cap);
            CALL get_sma_range(str_sma, @min_sma, @max_sma);
            CALL get_ps_range(str_ps, @min_ps, @max_ps);
            CALL get_gm_range(str_gm, @min_gm, @max_gm);
            CALL get_pm_range(str_pm, @min_pm, @max_pm);
            CALL get_om_range(str_om, @min_om, @max_om);

            SELECT t1.symbol, market_cap, sma200, price_to_sales, 
                gross_margin, t2.profit_margin, t2.operating_margin
            FROM
            (SELECT * 
            FROM screening
            WHERE market_cap BETWEEN @min_cap AND @max_cap
            AND sma200 BETWEEN @min_sma AND @max_sma
            AND price_to_sales BETWEEN @min_ps AND @max_ps
            AND gross_margin BETWEEN @min_gm AND @max_gm) AS t1
            INNER JOIN
            (SELECT symbol, profit_margin, operating_margin 
            FROM statistics
            WHERE profit_margin BETWEEN @min_pm AND @max_pm
            AND operating_margin BETWEEN @min_om AND @max_om) AS t2
            ON t1.symbol = t2.symbol;

        END $$ 

        DELIMITER ;
        """
    )

    mydb.close()


if __name__ == "__main__":
    main()
