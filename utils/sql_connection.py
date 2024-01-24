import sqlite3


def get_connection(db_file):
    """
    Establish a connection to the .db file
    """
    conn = sqlite3.connect(db_file)
    return conn


def execute_query(conn, query):
    """
    Execute a query on the given connection
    """
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor


def fetch_one(cursor):
    """
    Fetch a single result from the cursor
    """
    return cursor.fetchone()


def close_connection(conn):
    """
    Close the connection to the database
    """
    conn.close()
