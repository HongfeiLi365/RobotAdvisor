import mysql.connector
import pandas as pd
import os

from utils import insert_dataframe
from clean_data import clean_statistics, clean_financials, clean_prices

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
        "CREATE TABLE prices (symbol VARCHAR(10), date DATE, open FLOAT, " +
        " high FLOAT, low FLOAT, " +
        "close FLOAT, adjclose FLOAT, volume BIGINT, " +
        "PRIMARY KEY(symbol, date))")

    mycursor.execute(
        "CREATE TABLE statistics (symbol VARCHAR(10), most_recent_quarter DATE, "
        "payout_ratio FLOAT, profit_margin FLOAT, "
        "operating_margin FLOAT, return_on_assets FLOAT, "
        "return_on_equity FLOAT, revenue_per_share FLOAT, "
        "quarterly_revenue_growth FLOAT, ebitda BIGINT, diluted_eps FLOAT, "
        "quarterly_earnings_growth FLOAT, total_cash_per_share FLOAT, "
        "total_debt_to_equity FLOAT, current_ratio FLOAT, "
        "operating_cash_flow BIGINT, PRIMARY KEY(symbol))")

    mycursor.execute(
        "CREATE TABLE financials (symbol VARCHAR(10), date DATE, "
        "research_development BIGINT, income_before_tax BIGINT, "
        "minority_interest BIGINT, net_income BIGINT, "
        "selling_general_administrative BIGINT, gross_profit BIGINT, "
        "ebit BIGINT, operating_income BIGINT, "
        "other_operating_expenses BIGINT, interest_expense BIGINT, "
        "income_tax_expense BIGINT, total_revenue BIGINT, "
        "total_operating_expenses BIGINT, cost_of_revenue BIGINT, "
        "total_other_income_expense_net BIGINT, "
        "discontinued_operations BIGINT, "
        "net_income_from_continuing_ops BIGINT, "
        "net_income_applicable_to_common_shares BIGINT, "
        "intangible_assets BIGINT, capital_surplus BIGINT, "
        "total_liab BIGINT, total_stockholder_equity BIGINT, "
        "other_current_liab BIGINT, total_assets BIGINT, "
        "common_stock BIGINT, other_current_assets BIGINT, "
        "retained_earnings BIGINT, other_liab BIGINT, "
        "treasury_stock BIGINT, other_assets BIGINT, "
        "cash BIGINT, total_current_liabilities BIGINT, "
        "other_stockholder_equity BIGINT, "
        "property_plant_equipment BIGINT, "
        "total_current_assets BIGINT, long_term_investments BIGINT, "
        "net_tangible_assets BIGINT, net_receivables BIGINT, "
        "long_term_debt BIGINT, inventory BIGINT, "
        "accounts_payable BIGINT, good_will BIGINT, "
        "deferred_long_term_asset_charges BIGINT, "
        "short_long_term_debt BIGINT, "
        "short_term_investments BIGINT, "
        "deferred_long_term_liab BIGINT, investments BIGINT, "
        "change_to_liabilities BIGINT, "
        "total_cashflows_from_investing_activities BIGINT, "
        "net_borrowings BIGINT, "
        "total_cash_from_financing_activities BIGINT, "
        "change_to_operating_activities BIGINT, "
        "issuance_of_stock BIGINT, "
        "change_in_cash BIGINT, repurchase_of_stock BIGINT, "
        "effect_of_exchange_rate BIGINT, "
        "total_cash_from_operating_activities BIGINT, "
        "depreciation BIGINT, dividends_paid BIGINT, "
        "change_to_inventory BIGINT, "
        "change_to_account_receivables BIGINT, "
        "change_to_netincome BIGINT, "
        "capital_expenditures BIGINT, "
        "other_cashflows_from_investing_activities BIGINT, "
        "other_cashflows_from_financing_activities BIGINT, "
        "PRIMARY KEY(symbol, date))")


    statistics = pd.read_csv("data/all_stats_clean.csv")
    financials =  pd.read_csv("data/all_financials_clean.csv")
    prices = pd.read_csv("data/all_prices_clean.csv")

    insert_dataframe(mydb, statistics, 'statistics')
    insert_dataframe(mydb, financials, 'financials')
    insert_dataframe(mydb, prices, 'prices', batch_size=10000)


if __name__ == "__main__":
    main()