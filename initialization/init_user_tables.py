import mysql.connector
import pandas as pd
import os


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

    mycursor.execute("DROP TABLE IF EXISTS post, user")


    mycursor.execute(
        "CREATE TABLE user ("
        "id INTEGER NOT NULL, "
        "username VARCHAR(20) NOT NULL, "
        "email VARCHAR(120) NOT NULL, "
        "image_file VARCHAR(20) NOT NULL, "
        "password VARCHAR(60) NOT NULL, "
        "PRIMARY KEY (id), "
        "UNIQUE (username), "
        "UNIQUE (email))")

    mycursor.execute(
        "CREATE TABLE post ("
        "id INTEGER NOT NULL, "
        "title VARCHAR(100) NOT NULL, "
        "date_posted DATETIME NOT NULL, "
        "content TEXT NOT NULL, "
        "user_id INTEGER NOT NULL, "
        "PRIMARY KEY (id), "
        "FOREIGN KEY(user_id) REFERENCES user (id))"
    )
    
    mydb.commit()
    mycursor.close()
    mydb.close()

if __name__ == "__main__":
    main()