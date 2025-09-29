"""
SQL connection utilities with comprehensive database operations and error handling.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_connection(db_file: str) -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database file with configuration.

    Args:
        db_file (str): Path to the database file

    Returns:
        sqlite3.Connection: Database connection object

    Raises:
        FileNotFoundError: If database file doesn't exist
        sqlite3.Error: If connection fails
    """
    try:
        if not os.path.exists(db_file):
            raise FileNotFoundError(f"Database file not found: {db_file}")

        # Connection with row factory for better data access
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # Enables column access by name

        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        logger.info(f"Database connection established: {db_file}")
        return conn

    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database {db_file}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {str(e)}")
        raise


@contextmanager
def get_connection_context(db_file: str):
    """
    Context manager for database connections with automatic cleanup.

    Args:
        db_file (str): Path to the database file

    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = None
    try:
        conn = get_connection(db_file)
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


def execute_query(
    conn: sqlite3.Connection, query: str, params: tuple = None
) -> sqlite3.Cursor:
    """
    Execute a query on the given connection with error handling.

    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters for prepared statements

    Returns:
        sqlite3.Cursor: Query cursor

    Raises:
        sqlite3.Error: If query execution fails
    """
    try:
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
            logger.info(
                f"Executed parameterized query: {query[:50]}... with params: {params}"
            )
        else:
            cursor.execute(query)
            logger.info(f"Executed query: {query[:50]}...")

        return cursor

    except sqlite3.Error as e:
        logger.error(f"Query execution failed: {str(e)}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Parameters: {params}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during query execution: {str(e)}")
        raise


def execute_query_safe(
    conn: sqlite3.Connection, query: str, params: tuple = None
) -> Optional[sqlite3.Cursor]:
    """
    Safely execute a query with exception handling that returns None on failure.

    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters

    Returns:
        sqlite3.Cursor or None: Query cursor or None if failed
    """
    try:
        return execute_query(conn, query, params)
    except Exception as e:
        logger.warning(f"Safe query execution failed, returning None: {str(e)}")
        return None


def fetch_one(cursor: sqlite3.Cursor) -> Optional[sqlite3.Row]:
    """
    Fetch a single result from the cursor with error handling.

    Args:
        cursor (sqlite3.Cursor): Database cursor

    Returns:
        sqlite3.Row or None: Single row result or None if no results
    """
    try:
        result = cursor.fetchone()
        if result:
            logger.info("Fetched one row successfully")
        else:
            logger.info("No rows found")
        return result
    except Exception as e:
        logger.error(f"Error fetching single row: {str(e)}")
        return None


def fetch_all(cursor: sqlite3.Cursor) -> List[sqlite3.Row]:
    """
    Fetch all results from the cursor with error handling.

    Args:
        cursor (sqlite3.Cursor): Database cursor

    Returns:
        List[sqlite3.Row]: List of all rows
    """
    try:
        results = cursor.fetchall()
        logger.info(f"Fetched {len(results)} rows successfully")
        return results
    except Exception as e:
        logger.error(f"Error fetching all rows: {str(e)}")
        return []


def fetch_many(cursor: sqlite3.Cursor, size: int) -> List[sqlite3.Row]:
    """
    Fetch a specified number of results from the cursor.

    Args:
        cursor (sqlite3.Cursor): Database cursor
        size (int): Number of rows to fetch

    Returns:
        List[sqlite3.Row]: List of rows up to specified size
    """
    try:
        results = cursor.fetchmany(size)
        logger.info(f"Fetched {len(results)} rows (requested: {size})")
        return results
    except Exception as e:
        logger.error(f"Error fetching {size} rows: {str(e)}")
        return []


def execute_and_fetch_one(
    conn: sqlite3.Connection, query: str, params: tuple = None
) -> Optional[sqlite3.Row]:
    """
    Execute query and fetch single result in one operation.

    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters

    Returns:
        sqlite3.Row or None: Single row result
    """
    try:
        cursor = execute_query(conn, query, params)
        return fetch_one(cursor)
    except Exception as e:
        logger.error(f"Execute and fetch one failed: {str(e)}")
        return None


def execute_and_fetch_all(
    conn: sqlite3.Connection, query: str, params: tuple = None
) -> List[sqlite3.Row]:
    """
    Execute query and fetch all results in one operation.

    Args:
        conn (sqlite3.Connection): Database connection
        query (str): SQL query to execute
        params (tuple, optional): Query parameters

    Returns:
        List[sqlite3.Row]: List of all rows
    """
    try:
        cursor = execute_query(conn, query, params)
        return fetch_all(cursor)
    except Exception as e:
        logger.error(f"Execute and fetch all failed: {str(e)}")
        return []


def insert_data(
    conn: sqlite3.Connection, table: str, data: Dict[str, Any]
) -> Optional[int]:
    """
    Insert data into a table with dynamic column mapping.

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name
        data (Dict[str, Any]): Column-value pairs to insert

    Returns:
        int or None: Row ID of inserted record
    """
    try:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        cursor = execute_query(conn, query, tuple(data.values()))
        conn.commit()

        row_id = cursor.lastrowid
        logger.info(f"Inserted data into {table}, row ID: {row_id}")
        return row_id

    except Exception as e:
        logger.error(f"Failed to insert data into {table}: {str(e)}")
        conn.rollback()
        return None


def update_data(
    conn: sqlite3.Connection,
    table: str,
    data: Dict[str, Any],
    where_clause: str,
    where_params: tuple = None,
) -> int:
    """
    Update data in a table with dynamic column mapping.

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name
        data (Dict[str, Any]): Column-value pairs to update
        where_clause (str): WHERE clause condition
        where_params (tuple, optional): Parameters for WHERE clause

    Returns:
        int: Number of affected rows
    """
    try:
        set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        params = list(data.values())
        if where_params:
            params.extend(where_params)

        cursor = execute_query(conn, query, tuple(params))
        conn.commit()

        affected_rows = cursor.rowcount
        logger.info(f"Updated {affected_rows} rows in {table}")
        return affected_rows

    except Exception as e:
        logger.error(f"Failed to update data in {table}: {str(e)}")
        conn.rollback()
        return 0


def delete_data(
    conn: sqlite3.Connection, table: str, where_clause: str, where_params: tuple = None
) -> int:
    """
    Delete data from a table.

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name
        where_clause (str): WHERE clause condition
        where_params (tuple, optional): Parameters for WHERE clause

    Returns:
        int: Number of deleted rows
    """
    try:
        query = f"DELETE FROM {table} WHERE {where_clause}"
        cursor = execute_query(conn, query, where_params)
        conn.commit()

        deleted_rows = cursor.rowcount
        logger.info(f"Deleted {deleted_rows} rows from {table}")
        return deleted_rows

    except Exception as e:
        logger.error(f"Failed to delete data from {table}: {str(e)}")
        conn.rollback()
        return 0


def get_table_info(conn: sqlite3.Connection, table: str) -> List[sqlite3.Row]:
    """
    Get table schema information.

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name

    Returns:
        List[sqlite3.Row]: Table schema information
    """
    try:
        query = f"PRAGMA table_info({table})"
        return execute_and_fetch_all(conn, query)
    except Exception as e:
        logger.error(f"Failed to get table info for {table}: {str(e)}")
        return []


def get_table_names(conn: sqlite3.Connection) -> List[str]:
    """
    Get all table names in the database.

    Args:
        conn (sqlite3.Connection): Database connection

    Returns:
        List[str]: List of table names
    """
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        rows = execute_and_fetch_all(conn, query)
        return [row["name"] for row in rows]
    except Exception as e:
        logger.error(f"Failed to get table names: {str(e)}")
        return []


def close_connection(conn: sqlite3.Connection) -> None:
    """
    Close the connection to the database with error handling.

    Args:
        conn (sqlite3.Connection): Database connection to close
    """
    try:
        if conn:
            conn.close()
            logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")


def validate_connection(db_file: str) -> bool:
    """
    Test database connection and basic functionality.

    Args:
        db_file (str): Path to the database file

    Returns:
        bool: True if connection test passes
    """
    try:
        with get_connection_context(db_file) as conn:
            # Test basic query
            cursor = execute_query(conn, "SELECT sqlite_version()")
            version = fetch_one(cursor)

            if version:
                logger.info(
                    f"Database connection test passed. SQLite version: {version[0]}"
                )
                return True
            else:
                logger.error("Database connection test failed - no version returned")
                return False

    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False


# Convenience functions for common Chinook database operations
def get_artists(conn: sqlite3.Connection, limit: int = 10) -> List[sqlite3.Row]:
    """Get artists from Chinook database."""
    query = "SELECT ArtistId, Name FROM artists LIMIT ?"
    return execute_and_fetch_all(conn, query, (limit,))


def get_albums_by_artist(conn: sqlite3.Connection, artist_id: int) -> List[sqlite3.Row]:
    """Get albums by specific artist from Chinook database."""
    query = "SELECT AlbumId, Title FROM albums WHERE ArtistId = ?"
    return execute_and_fetch_all(conn, query, (artist_id,))


def get_tracks_by_album(conn: sqlite3.Connection, album_id: int) -> List[sqlite3.Row]:
    """Get tracks by specific album from Chinook database."""
    query = "SELECT TrackId, Name, Milliseconds FROM tracks WHERE AlbumId = ?"
    return execute_and_fetch_all(conn, query, (album_id,))
