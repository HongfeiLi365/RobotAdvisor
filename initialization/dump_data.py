import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="pyuser",
  password="fourtune1234"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS robotadvisor")


mydb = mysql.connector.connect(
  host="localhost",
  user="pyuser",
  password="fourtune1234",
  database="robotadvisor"
)

mycursor = mydb.cursor()

mycursor.execute(
    "CREATE TABLE prices (date DATE, open FLOAT, high FLOAT, low FLOAT, " +
    "close FLOAT, adjclose FLOAT, volume FLOAT, ticker VARCHAR(10), " + 
    "PRIMARY KEY(date, ticker))")

