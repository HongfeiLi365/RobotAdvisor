from neo4j import GraphDatabase
import os

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
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "fourtune1234"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    print(query)
    result = []
    with driver.session() as session:
        if fetch:
            try:
                neo4jOutput = session.run(query) #session.write_transaction(cypher_command_fetch)
                result = [record for record in neo4jOutput]
                #print(result)
            except:
                pass
        else:
            try:
                session.run(query)#write_transaction(cypher_command)
            except:
                pass
    driver.close()
    if result == []:
        return None
    else:
        return result

def cypher_command_fetch(tx, command = "MATCH (n) RETURN n limit 10"):
    '''
    define the query command
    '''
    #print(command)
    result = tx.run(command)
    try: # in case of empty query result
        if result == []:
            return None
        else:
            return result
    except:
        return None

def cypher_command(tx, command = "MATCH (n) RETURN n limit 10"):
    '''
    define the query command
    '''
    print(command)
    tx.run(command)
