import pandas as pd

def insert_dataframe(conn, df, table, batch_size=10000):
    for i in range(0, len(df), batch_size):
        df.iloc[i: i+batch_size]
        insert_many(conn, df.iloc[i: i+batch_size], table)


def insert_many(conn, df, table):
    # Creating a list of tupples from the dataframe values
    tpls = [tuple(x) for x in df.to_numpy()]
    
    # dataframe columns with Comma-separated
    cols = ','.join(list(df.columns))
    
    # SQL query to execute
    sql = "INSERT INTO %s(%s)"  % (table, cols)
    sql = sql + " VALUES(" + "%s, "* (len(df.columns)-1) + "%s)"

    cursor = conn.cursor()
    try:
        cursor.executemany(sql, tpls)
        conn.commit()
        print("Successfully inserted {} tuples into {}.".format(len(tpls), table))
    except Exception as e:
        print("Error while inserting to MySQL", e)
        cursor.close()
        raise Exception("break")