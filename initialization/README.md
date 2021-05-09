# Overview

This folder contains scripts to scrape data from Yahoo Finance and set up MySQL and Neo4j for the first time. 

# Data

Run the following scripts to scrape and clean data from Yahoo Finance:

1. scrape_data.py
2. clean_data.py
3. create_features.py

# MySQL

Run the following scripts to dump data into MySQL database and create stored procedures:

1. load_data_mysql.py
2. create_procedures.sql

Optionally, run the following script to set up user and posts table if you are going to store users in MySQL instead of Neo4j:

- init_user_tables_mysql.py

# Neo4j

Run the following scripts to set up neo4j and label stocks by their clusters:

1. load_stocks_neo4j.py
2. label_stocks_neo4j.py
