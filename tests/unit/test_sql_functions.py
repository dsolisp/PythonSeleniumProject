from hamcrest import (
    assert_that,
    equal_to,
    is_,
    none,
)

"""
Real Unit Tests for SQL Connection Functions
Testing actual function logic with proper mocks and edge cases.
"""

import sqlite3
from unittest.mock import Mock, patch

import pytest

from utils.sql_connection import (
    close_connection,
    delete_data,
    execute_query,
    execute_query_safe,
    fetch_all,
    fetch_many,
    fetch_one,
    get_connection,
    get_table_info,
    get_table_names,
    insert_data,
    update_data,
    validate_connection,
)


class TestDatabaseConnectionFunctions:
    """Test core database connection functions."""

    def test_get_connection_file_not_found(self):
        """Test get_connection raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError, match="Database file not found"):
            get_connection("nonexistent_file.db")

    @patch("utils.sql_connection.os.path.exists")
    @patch("utils.sql_connection.sqlite3.connect")
    def test_get_connection_sqlite_error(self, mock_connect, mock_exists):
        """Test get_connection handles sqlite3.Error properly."""
        mock_exists.return_value = True
        mock_connect.side_effect = sqlite3.Error("Connection failed")

        with pytest.raises(sqlite3.Error, match="Connection failed"):
            get_connection("test.db")

    @patch("utils.sql_connection.os.path.exists")
    @patch("utils.sql_connection.sqlite3.connect")
    def test_get_connection_success(self, mock_connect, mock_exists):
        """Test successful connection setup."""
        mock_exists.return_value = True
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        result = get_connection("test.db")

        assert_that(result, equal_to(mock_conn))
        mock_connect.assert_called_once_with("test.db")
        mock_conn.execute.assert_called_with("PRAGMA foreign_keys = ON")
        assert_that(mock_conn.row_factory, equal_to(sqlite3.Row))


class TestQueryExecutionFunctions:
    """Test query execution functions."""

    def test_execute_query_without_params(self):
        """Test execute_query with no parameters."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        result = execute_query(mock_conn, "SELECT 1")

        assert_that(result, equal_to(mock_cursor))
        mock_cursor.execute.assert_called_once_with("SELECT 1")

    def test_execute_query_with_params(self):
        """Test execute_query with parameters."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        result = execute_query(mock_conn, "SELECT * FROM users WHERE id = ?", (1,))

        assert_that(result, equal_to(mock_cursor))
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM users WHERE id = ?", (1,)
        )

    def test_execute_query_sqlite_error(self):
        """Test execute_query handles sqlite3.Error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Query failed")

        with pytest.raises(sqlite3.Error, match="Query failed"):
            execute_query(mock_conn, "INVALID SQL")

    def test_execute_query_safe_success(self):
        """Test execute_query_safe returns cursor on success."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        result = execute_query_safe(mock_conn, "SELECT 1")

        assert_that(result, equal_to(mock_cursor))

    def test_execute_query_safe_failure(self):
        """Test execute_query_safe returns None on failure."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Query failed")

        result = execute_query_safe(mock_conn, "INVALID SQL")

        assert_that(result, is_(none()))


class TestDataFetchingFunctions:
    """Test data fetching functions."""

    def test_fetch_one_success(self):
        """Test fetch_one returns single row."""
        mock_cursor = Mock()
        mock_row = Mock()
        mock_cursor.fetchone.return_value = mock_row

        result = fetch_one(mock_cursor)

        assert_that(result, equal_to(mock_row))
        mock_cursor.fetchone.assert_called_once()

    def test_fetch_one_no_results(self):
        """Test fetch_one handles no results."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None

        result = fetch_one(mock_cursor)

        assert_that(result, is_(none()))

    def test_fetch_one_exception(self):
        """Test fetch_one handles exceptions."""
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = Exception("Fetch failed")

        result = fetch_one(mock_cursor)

        assert_that(result, is_(none()))

    def test_fetch_all_success(self):
        """Test fetch_all returns all rows."""
        mock_cursor = Mock()
        mock_rows = [Mock(), Mock(), Mock()]
        mock_cursor.fetchall.return_value = mock_rows

        result = fetch_all(mock_cursor)

        assert_that(result, equal_to(mock_rows))
        assert_that(len(result), equal_to(3))

    def test_fetch_all_exception(self):
        """Test fetch_all handles exceptions."""
        mock_cursor = Mock()
        mock_cursor.fetchall.side_effect = Exception("Fetch failed")

        result = fetch_all(mock_cursor)

        assert_that(result, equal_to([]))

    def test_fetch_many_success(self):
        """Test fetch_many returns specified number of rows."""
        mock_cursor = Mock()
        mock_rows = [Mock(), Mock()]
        mock_cursor.fetchmany.return_value = mock_rows

        result = fetch_many(mock_cursor, 2)

        assert_that(result, equal_to(mock_rows))
        mock_cursor.fetchmany.assert_called_once_with(2)

    def test_fetch_many_exception(self):
        """Test fetch_many handles exceptions."""
        mock_cursor = Mock()
        mock_cursor.fetchmany.side_effect = Exception("Fetch failed")

        result = fetch_many(mock_cursor, 5)

        assert_that(result, equal_to([]))


class TestDataModificationFunctions:
    """Test data modification functions."""

    def test_insert_data_success(self):
        """Test insert_data builds correct query and returns row ID."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 123

        with patch("utils.sql_connection.execute_query", return_value=mock_cursor):
            result = insert_data(mock_conn, "users", {"name": "John", "age": 30})

        assert_that(result, equal_to(123))
        mock_conn.commit.assert_called_once()

    def test_insert_data_exception(self):
        """Test insert_data handles exceptions and rollback."""
        mock_conn = Mock()

        with patch(
            "utils.sql_connection.execute_query", side_effect=Exception("Insert failed")
        ):
            result = insert_data(mock_conn, "users", {"name": "John"})

        assert_that(result, is_(none()))
        mock_conn.rollback.assert_called_once()

    def test_update_data_success(self):
        """Test update_data builds correct query."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 2

        with patch("utils.sql_connection.execute_query", return_value=mock_cursor):
            result = update_data(mock_conn, "users", {"name": "Jane"}, "id = ?", (1,))

        assert_that(result, equal_to(2))
        mock_conn.commit.assert_called_once()

    def test_update_data_exception(self):
        """Test update_data handles exceptions."""
        mock_conn = Mock()

        with patch(
            "utils.sql_connection.execute_query", side_effect=Exception("Update failed")
        ):
            result = update_data(mock_conn, "users", {"name": "Jane"}, "id = ?", (1,))

        assert_that(result, equal_to(0))
        mock_conn.rollback.assert_called_once()

    def test_delete_data_success(self):
        """Test delete_data returns correct count."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.rowcount = 1

        with patch("utils.sql_connection.execute_query", return_value=mock_cursor):
            result = delete_data(mock_conn, "users", "id = ?", (1,))

        assert_that(result, equal_to(1))
        mock_conn.commit.assert_called_once()

    def test_delete_data_exception(self):
        """Test delete_data handles exceptions."""
        mock_conn = Mock()

        with patch(
            "utils.sql_connection.execute_query", side_effect=Exception("Delete failed")
        ):
            result = delete_data(mock_conn, "users", "id = ?", (1,))

        assert_that(result, equal_to(0))
        mock_conn.rollback.assert_called_once()


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_table_info_success(self):
        """Test get_table_info returns table schema."""
        mock_conn = Mock()
        mock_rows = [Mock(), Mock()]

        with patch(
            "utils.sql_connection.execute_and_fetch_all", return_value=mock_rows
        ):
            result = get_table_info(mock_conn, "users")

        assert_that(result, equal_to(mock_rows))

    def test_get_table_names_success(self):
        """Test get_table_names extracts table names correctly."""
        mock_conn = Mock()
        mock_rows = [{"name": "users"}, {"name": "products"}]

        with patch(
            "utils.sql_connection.execute_and_fetch_all", return_value=mock_rows
        ):
            result = get_table_names(mock_conn)

        assert_that(result, equal_to(["users", "products"]))

    def test_get_table_names_exception(self):
        """Test get_table_names handles exceptions."""
        mock_conn = Mock()

        with patch(
            "utils.sql_connection.execute_and_fetch_all",
            side_effect=Exception("Failed"),
        ):
            result = get_table_names(mock_conn)

        assert_that(result, equal_to([]))

    def test_close_connection_success(self):
        """Test close_connection calls close method."""
        mock_conn = Mock()

        close_connection(mock_conn)

        mock_conn.close.assert_called_once()

    def test_close_connection_exception(self):
        """Test close_connection handles exceptions."""
        mock_conn = Mock()
        mock_conn.close.side_effect = Exception("Close failed")

        # Should not raise exception
        close_connection(mock_conn)

    def test_close_connection_none(self):
        """Test close_connection handles None input."""
        # Should not raise exception
        close_connection(None)


class TestValidationFunctions:
    """Test validation functions."""

    @patch("utils.sql_connection.get_connection_context")
    @patch("utils.sql_connection.execute_query")
    @patch("utils.sql_connection.fetch_one")
    def test_validate_connection_success(self, mock_fetch, mock_execute, mock_context):
        """Test validate_connection returns True on success."""
        mock_conn = Mock()
        mock_context.return_value.__enter__.return_value = mock_conn
        mock_context.return_value.__exit__.return_value = None
        mock_fetch.return_value = ["3.39.0"]  # SQLite version

        result = validate_connection("test.db")

        assert_that(result, is_(True))

    @patch("utils.sql_connection.get_connection_context")
    def test_validate_connection_failure(self, mock_context):
        """Test validate_connection returns False on failure."""
        mock_context.side_effect = Exception("Connection failed")

        result = validate_connection("test.db")

        assert_that(result, is_(False))
