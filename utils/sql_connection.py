"""
SQLite connection utilities with parameterized queries and SQL injection prevention.

Usage Examples:
    # Basic query
    from utils.sql_connection import connection_context, fetch_all

    with connection_context("resources/chinook.db") as conn:
        users = fetch_all(conn, "SELECT * FROM users WHERE active = ?", (1,))

    # Transaction with multiple operations
    with connection_context("resources/chinook.db") as conn:
        try:
            insert(conn, "orders", {"user_id": 1, "total": 99.99})
            update(conn, "inventory", {"quantity": 5}, "product_id = ?", (123,))
            conn.commit()  # Commit transaction
        except Exception:
            conn.rollback()  # Rollback on any error
            raise

    # Safe table introspection
    with connection_context("resources/chinook.db") as conn:
        tables = get_table_names(conn)
        schema = get_table_info(conn, "users")
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


def _validate_identifier(name, identifier_type="identifier"):
    """Validate table/column names (alphanumeric + underscore only)."""
    if not name or not name.replace("_", "").isalnum():
        raise ValueError(f"Invalid {identifier_type}: '{name}'")
    return name


def get_connection(db_file):
    """Connect to SQLite database with row factory enabled."""
    if not Path(db_file).exists():
        raise FileNotFoundError(f"Database not found: {db_file}")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection_context(db_file):
    """
    Context manager for database connections with auto-cleanup.

    Automatically rolls back on exceptions and closes the connection.

    Example:
        with connection_context("mydb.db") as conn:
            result = fetch_all(conn, "SELECT * FROM users")
            insert(conn, "logs", {"action": "query", "count": len(result)})
            # Connection auto-closes when exiting the block
    """
    conn = get_connection(db_file)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(conn, query, params=None):
    """Execute a parameterized query."""
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    return cursor


def fetch_one(conn, query, params=None):
    """Execute query and fetch single result. Returns Row or None."""
    return execute_query(conn, query, params).fetchone()


def fetch_all(conn, query, params=None):
    """Execute query and fetch all results."""
    return execute_query(conn, query, params).fetchall()


def insert(conn, table, data):
    """Insert data into table. Returns row ID or None on failure."""
    try:
        table = _validate_identifier(table, "table")
        cols = [_validate_identifier(c, "column") for c in data]
        query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"  # nosec B608
        cursor = execute_query(conn, query, tuple(data.values()))
        conn.commit()
        return cursor.lastrowid
    except (ValueError, sqlite3.Error) as e:
        logger.warning(f"Insert failed: {e}")
        conn.rollback()
        return None


def update(conn, table, data, where, where_params=None):
    """Update rows matching WHERE clause. Returns affected row count."""
    try:
        table = _validate_identifier(table, "table")
        cols = [_validate_identifier(c, "column") for c in data]
        set_clause = ", ".join(f"{c} = ?" for c in cols)
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"  # nosec B608
        params = tuple(data.values()) + (where_params or ())
        cursor = execute_query(conn, query, params)
        conn.commit()
        return cursor.rowcount
    except (ValueError, sqlite3.Error) as e:
        logger.warning(f"Update failed: {e}")
        conn.rollback()
        return 0


def delete(conn, table, where, where_params=None):
    """Delete rows matching WHERE clause. Returns deleted row count."""
    try:
        table = _validate_identifier(table, "table")
        query = f"DELETE FROM {table} WHERE {where}"  # nosec B608
        cursor = execute_query(conn, query, where_params)
        conn.commit()
        return cursor.rowcount
    except (ValueError, sqlite3.Error) as e:
        logger.warning(f"Delete failed: {e}")
        conn.rollback()
        return 0


def get_table_names(conn):
    """Get all table names in database."""
    rows = fetch_all(conn, "SELECT name FROM sqlite_master WHERE type='table'")
    return [r["name"] for r in rows]


def get_table_info(conn, table):
    """Get table schema (columns, types, etc.)."""
    table = _validate_identifier(table, "table")
    return fetch_all(conn, f"PRAGMA table_info({table})")  # noqa: S608
