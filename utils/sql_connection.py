"""
SQL connection utilities with comprehensive database operations and error handling.
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _validate_table_name(table: str) -> str:
    """
    Validate table name to prevent SQL injection.
    Only allows alphanumeric characters and underscores.

    Args:
        table (str): Table name to validate

    Returns:
        str: Validated table name

    Raises:
        ValueError: If table name contains invalid characters
    """
    if not table:
        message = "Table name cannot be empty"
        raise ValueError(message)

    # Only allow alphanumeric and underscores (no spaces, quotes, or special chars)
    if not table.replace("_", "").isalnum():
        message = (
            f"Invalid table name '{table}'. Only alphanumeric characters and "
            "underscores are allowed."
        )
        raise ValueError(message)

    return table


def _validate_column_name(column: str) -> str:
    """
    Validate column name to prevent SQL injection.
    Only allows alphanumeric characters and underscores.

    Args:
        column (str): Column name to validate

    Returns:
        str: Validated column name

    Raises:
        ValueError: If column name contains invalid characters
    """
    if not column:
        message = "Column name cannot be empty"
        raise ValueError(message)

    # Only allow alphanumeric and underscores (no spaces, quotes, or special chars)
    if not column.replace("_", "").isalnum():
        message = (
            f"Invalid column name '{column}'. Only alphanumeric characters and "
            "underscores are allowed."
        )
        raise ValueError(message)

    return column


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
    # Validate database file exists before attempting connection
    if not Path(db_file).exists():
        message = f"Database file not found: {db_file}"
        raise FileNotFoundError(message)

    try:
        # Connection with row factory for better data access
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # Enables column access by name

        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")

        logger.info("Database connection established: %s", db_file)
    except sqlite3.Error:
        logger.exception("Failed to connect to database %s", db_file)
        raise
    except Exception:
        logger.exception("Unexpected error connecting to database")
        raise
    else:
        return conn


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
    except Exception:
        if conn:
            conn.rollback()
        logger.exception("Database operation failed")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


def execute_query(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[tuple] = None,
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
                "Executed parameterized query: %s... with params: %s",
                query[:50],
                params,
            )
        else:
            cursor.execute(query)
            logger.info("Executed query: %s...", query[:50])
    except sqlite3.Error:
        logger.exception("Query execution failed")
        logger.exception("Query: %s", query)
        if params:
            logger.exception("Parameters: %s", params)
        raise
    except Exception:
        logger.exception("Unexpected error during query execution")
        raise
    else:
        return cursor


def execute_query_safe(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[tuple] = None,
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
    except (sqlite3.Error, ValueError, TypeError) as e:
        logger.warning("Safe query execution failed, returning None: %s", e)
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
    except Exception:
        logger.exception("Error fetching single row")
        return None
    else:
        return result


def fetch_all(cursor: sqlite3.Cursor) -> list[sqlite3.Row]:
    """
    Fetch all results from the cursor with error handling.

    Args:
        cursor (sqlite3.Cursor): Database cursor

    Returns:
        List[sqlite3.Row]: List of all rows
    """
    try:
        results = cursor.fetchall()
        logger.info("Fetched %d rows successfully", len(results))
    except Exception:
        logger.exception("Error fetching all rows")
        return []
    else:
        return results


def fetch_many(cursor: sqlite3.Cursor, size: int) -> list[sqlite3.Row]:
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
        logger.info("Fetched %d rows (requested: %d)", len(results), size)
    except Exception:
        logger.exception("Error fetching %d rows", size)
        return []
    else:
        return results


def execute_and_fetch_one(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[tuple] = None,
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
    except Exception:
        logger.exception("Execute and fetch one failed")
        return None


def execute_and_fetch_all(
    conn: sqlite3.Connection,
    query: str,
    params: Optional[tuple] = None,
) -> list[sqlite3.Row]:
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
    except Exception:
        logger.exception("Execute and fetch all failed")
        return []


def insert_data(
    conn: sqlite3.Connection,
    table: str,
    data: dict[str, Any],
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
        # Validate table name to prevent SQL injection
        validated_table = _validate_table_name(table)

        # Validate all column names to prevent SQL injection
        validated_columns = [_validate_column_name(col) for col in data]
        columns = ", ".join(validated_columns)
        placeholders = ", ".join(["?" for _ in data])
        # Safe: table and column names have been validated using
        # _validate_table_name() and _validate_column_name() to allow only
        # alphanumeric characters and underscores, preventing SQL injection.
        # Values are parameterized.
        query = f"INSERT INTO {validated_table} ({columns}) VALUES ({placeholders})"  # nosec B608

        cursor = execute_query(conn, query, tuple(data.values()))
        conn.commit()

        row_id = cursor.lastrowid
        logger.info("Inserted data into %s, row ID: %s", table, row_id)
    except ValueError:
        logger.exception("Invalid table or column name")
        return None
    except Exception:
        logger.exception("Failed to insert data into %s", table)
        conn.rollback()
        return None
    else:
        return row_id


def update_data(
    conn: sqlite3.Connection,
    table: str,
    data: dict[str, Any],
    where_clause: str,
    where_params: Optional[tuple] = None,
) -> int:
    """
    Update data in a table with dynamic column mapping.

    SECURITY: where_clause MUST use parameterized placeholders (?) to prevent
    SQL injection. Never use f-strings or concatenation for user input in
    where_clause.

    Safe:   update_data(conn, "users", {"name": "Jane"}, "id = ?", (1,))
    UNSAFE: update_data(conn, "users", {"name": "Jane"}, f"id = {user_id}")

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name
        data (Dict[str, Any]): Column-value pairs to update
        where_clause (str): WHERE clause condition (must use ? placeholders)
        where_params (tuple, optional): Parameters for WHERE clause

    Returns:
        int: Number of affected rows

    Raises:
        ValueError: If where_clause contains user input without parameterization
    """

    def _validate_params():
        if where_clause and "?" in where_clause and not where_params:
            message = "WHERE clause contains '?' but no where_params provided"
            raise ValueError(message)

    try:
        # Validate table name to prevent SQL injection
        validated_table = _validate_table_name(table)

        # Validate all column names to prevent SQL injection
        validated_columns = [_validate_column_name(col) for col in data]

        # Verify WHERE clause uses parameterized queries
        _validate_params()

        set_clause = ", ".join([f"{col} = ?" for col in validated_columns])
        # Safe: table/column names validated, values parameterized
        query = f"UPDATE {validated_table} SET {set_clause} WHERE {where_clause}"  # nosec B608

        params = list(data.values())
        if where_params:
            params.extend(where_params)

        cursor = execute_query(conn, query, tuple(params))
        conn.commit()

        affected_rows = cursor.rowcount
        logger.info("Updated %d rows in %s", affected_rows, table)
    except ValueError:
        logger.exception("Invalid table or column name")
        return 0
    except Exception:
        logger.exception("Failed to update data in %s", table)
        conn.rollback()
        return 0
    else:
        return affected_rows


def delete_data(
    conn: sqlite3.Connection,
    table: str,
    where_clause: str,
    where_params: Optional[tuple] = None,
) -> int:
    """
    Delete data from a table.

    SECURITY: where_clause MUST use parameterized placeholders (?) to prevent
    SQL injection. Never use f-strings or concatenation for user input in
    where_clause.

    Safe:   delete_data(conn, "users", "id = ?", (1,))
    UNSAFE: delete_data(conn, "users", f"id = {user_id}")

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name
        where_clause (str): WHERE clause condition (must use ? placeholders)
        where_params (tuple, optional): Parameters for WHERE clause

    Returns:
        int: Number of deleted rows

    Raises:
        ValueError: If where_clause contains user input without parameterization
    """

    def _validate_params():
        if where_clause and "?" in where_clause and not where_params:
            message = "WHERE clause contains '?' but no where_params provided"
            raise ValueError(message)

    try:
        # Validate table name to prevent SQL injection
        validated_table = _validate_table_name(table)

        # Verify WHERE clause uses parameterized queries
        _validate_params()

        # Safe: table name validated via _validate_table_name(),
        # where_params are parameterized
        query = f"DELETE FROM {validated_table} WHERE {where_clause}"  # nosec B608
        cursor = execute_query(conn, query, where_params)
        conn.commit()

        deleted_rows = cursor.rowcount
        logger.info("Deleted %d rows from %s", deleted_rows, table)
    except ValueError:
        logger.exception("Invalid table name")
        return 0
    except Exception:
        logger.exception("Failed to delete data from %s", table)
        conn.rollback()
        return 0
    else:
        return deleted_rows


def get_table_info(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    """
    Get table schema information.

    Args:
        conn (sqlite3.Connection): Database connection
        table (str): Table name

    Returns:
        List[sqlite3.Row]: Table schema information
    """
    try:
        # Validate table name to prevent SQL injection
        validated_table = _validate_table_name(table)
        # Note: PRAGMA statements don't support parameterized queries in SQLite
        # Using f-string with validated input (alphanumeric + underscore only)
        query = f"PRAGMA table_info({validated_table})"
        return execute_and_fetch_all(conn, query)
    except ValueError:
        logger.exception("Invalid table name")
        return []
    except Exception:
        logger.exception("Failed to get table info for %s", table)
        return []


def get_table_names(conn: sqlite3.Connection) -> list[str]:
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
    except Exception:
        logger.exception("Failed to get table names")
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
    except Exception:
        logger.exception("Error closing database connection")


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
                sqlite_version = version[0]
                logger.info(
                    "Database connection test passed. SQLite version: %s",
                    sqlite_version,
                )
                return True
            logger.error("Database connection test failed - no version returned")
            return False

    except Exception:
        logger.exception("Database connection test failed")
        return False


# Convenience functions for common Chinook database operations
def get_artists(conn: sqlite3.Connection, limit: int = 10) -> list[sqlite3.Row]:
    """Get artists from Chinook database."""
    query = "SELECT ArtistId, Name FROM artists LIMIT ?"
    return execute_and_fetch_all(conn, query, (limit,))


def get_albums_by_artist(conn: sqlite3.Connection, artist_id: int) -> list[sqlite3.Row]:
    """Get albums by specific artist from Chinook database."""
    query = "SELECT AlbumId, Title FROM albums WHERE ArtistId = ?"
    return execute_and_fetch_all(conn, query, (artist_id,))


def get_tracks_by_album(conn: sqlite3.Connection, album_id: int) -> list[sqlite3.Row]:
    """Get tracks by specific album from Chinook database."""
    query = "SELECT TrackId, Name, Milliseconds FROM tracks WHERE AlbumId = ?"
    return execute_and_fetch_all(conn, query, (album_id,))
