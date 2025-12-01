"""
Unit tests for SQL connection utilities.
Tests core database functions with in-memory SQLite.
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from utils.sql_connection import (
    _validate_identifier,
    connection_context,
    delete,
    execute_query,
    fetch_all,
    fetch_one,
    get_connection,
    get_table_info,
    get_table_names,
    insert,
    update,
)


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
    conn.commit()
    conn.close()
    yield db_path
    Path(db_path).unlink(missing_ok=True)


class TestIdentifierValidation:
    """Test SQL identifier validation."""

    @pytest.mark.parametrize("valid", ["users", "test_data", "Table123", "_private"])
    def test_valid_identifiers(self, valid):
        assert _validate_identifier(valid) == valid

    @pytest.mark.parametrize(
        "invalid", ["users; DROP", "table-name", "user's", "", None]
    )
    def test_invalid_identifiers(self, invalid):
        with pytest.raises(ValueError):
            _validate_identifier(invalid or "")


class TestConnection:
    """Test database connection functions."""

    def test_get_connection_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            get_connection("nonexistent.db")

    def test_get_connection_success(self, temp_db):
        conn = get_connection(temp_db)
        assert conn is not None
        assert conn.row_factory == sqlite3.Row
        conn.close()

    def test_connection_context_manager(self, temp_db):
        with connection_context(temp_db) as conn:
            result = fetch_one(conn, "SELECT COUNT(*) as cnt FROM users")
            assert result["cnt"] == 2


class TestQueryExecution:
    """Test query execution functions."""

    def test_execute_query(self, temp_db):
        with connection_context(temp_db) as conn:
            cursor = execute_query(conn, "SELECT * FROM users WHERE age > ?", (20,))
            assert cursor.fetchall() is not None

    def test_fetch_one(self, temp_db):
        with connection_context(temp_db) as conn:
            row = fetch_one(conn, "SELECT name FROM users WHERE age = ?", (30,))
            assert row["name"] == "Alice"

    def test_fetch_all(self, temp_db):
        with connection_context(temp_db) as conn:
            rows = fetch_all(conn, "SELECT * FROM users ORDER BY name")
            assert len(rows) == 2
            assert rows[0]["name"] == "Alice"


class TestCRUDOperations:
    """Test insert, update, delete operations."""

    def test_insert(self, temp_db):
        with connection_context(temp_db) as conn:
            row_id = insert(conn, "users", {"name": "Charlie", "age": 35})
            assert row_id is not None
            row = fetch_one(conn, "SELECT * FROM users WHERE id = ?", (row_id,))
            assert row["name"] == "Charlie"

    def test_insert_invalid_table(self, temp_db):
        with connection_context(temp_db) as conn:
            result = insert(conn, "users; DROP", {"name": "Evil"})
            assert result is None

    def test_update(self, temp_db):
        with connection_context(temp_db) as conn:
            affected = update(conn, "users", {"age": 31}, "name = ?", ("Alice",))
            assert affected == 1
            row = fetch_one(conn, "SELECT age FROM users WHERE name = ?", ("Alice",))
            assert row["age"] == 31

    def test_delete(self, temp_db):
        with connection_context(temp_db) as conn:
            deleted = delete(conn, "users", "name = ?", ("Bob",))
            assert deleted == 1
            row = fetch_one(conn, "SELECT * FROM users WHERE name = ?", ("Bob",))
            assert row is None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_table_names(self, temp_db):
        with connection_context(temp_db) as conn:
            tables = get_table_names(conn)
            assert "users" in tables

    def test_get_table_info(self, temp_db):
        with connection_context(temp_db) as conn:
            info = get_table_info(conn, "users")
            column_names = [row["name"] for row in info]
            assert "id" in column_names
            assert "name" in column_names
            assert "age" in column_names
