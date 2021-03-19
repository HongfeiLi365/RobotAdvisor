import mysql.connector
import os

def request_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database="robotadvisor"
    )
    return conn

def request_cursor(conn):
    return conn.cursor(buffered=True, dictionary=True)

def execute_query(query, fetch=True, commit=True):
    r = []
    conn = request_connection()
    cur = request_cursor(conn)

    cur.execute(query)

    if fetch:
        r = cur.fetchall()

    if commit:
        conn.commit()

    cur.close()
    conn.close()
    return r
