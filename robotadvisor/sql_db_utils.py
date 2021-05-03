import mysql.connector
import os


def request_connection():
    """
    connect to MySQL database

    Returns
    -------
    MySQLConnection
        a connection.MySQLConnection object
    """
    conn = mysql.connector.connect(
        host="localhost",
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database="robotadvisor"
    )
    return conn


def request_cursor(conn, prepared=False):
    """
    return a MySQLCursorDict object. This type of cursor return a list of
    dictionary, where each row is a dictionary, key of this dictionary
    is field name and value is field value.
    When query result contains 0 row, this type of cursor returns an empty list.
    When query result contains 1 row, this type of cursor returns a list with a
    single element.
    """
    if prepared:
        return conn.cursor(prepared=True)
    else:
        return conn.cursor(buffered=True, dictionary=True)


def execute_query(query, fetch=True, commit=True):
    """excute sql query

    Parameters
    ----------
    query : str
        sql query to excute
    fetch : bool
        Set it to True if you expect your query to return anything, such as
        "SELECT" queries.
        Set it to False if your query makes changes to the database, such as
        "INSERT", "DELETE", "UPDATE" queires.
    commit : bool
        Set it to True if your query makes changes to the database

    Returns
    -------
    list of dictionary
        result of query
    """
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


def execute_prepared_stmt(stmt, data):
    """Execute prepared statement

    Parameters
    ----------
    stmt : str
        statement to execute
    data : tuple
        data to pass to prepared statement

    Returns
    -------
    list of tuples
        list of rows
    """
    conn = request_connection()
    cur = request_cursor(conn, prepared=True)

    cur.execute(stmt, data)
    r = cur.fetchall()

    conn.close()
    return r
