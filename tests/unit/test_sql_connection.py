"""
Unit tests for SQL connection utility module.
Tests database operations, query execution, and data manipulation.
"""

import sqlite3
from unittest.mock import Mock, patch, MagicMock

import pytest

from utils.sql_connection import (
    get_connection,
    get_connection_context,
    execute_query,
    execute_query_safe,
    fetch_one,
    fetch_all,
    fetch_many,
    execute_and_fetch_one,
    execute_and_fetch_all,
    insert_data,
    update_data,
    delete_data,
    get_table_info,
    get_table_names,
    close_connection,
    test_connection,
    get_artists,
    get_albums_by_artist,
    get_tracks_by_album,
)


class TestConnectionFunctions:
    """Test cases for database connection functions."""

    @patch('utils.sql_connection.sqlite3.connect')
    @patch('utils.sql_connection.os.path.exists')
    def test_get_connection_success(self, mock_exists, mock_connect):
        """Test successful database connection."""
        mock_exists.return_value = True
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        db_path = "/path/to/database.db"
        
        result = get_connection(db_path)
        
        mock_exists.assert_called_once_with(db_path)
        mock_connect.assert_called_once_with(db_path)
        assert result == mock_connection
        assert mock_connection.row_factory == sqlite3.Row
        mock_connection.execute.assert_called_once_with("PRAGMA foreign_keys = ON")

    @patch('utils.sql_connection.os.path.exists')
    def test_get_connection_file_not_found(self, mock_exists):
        """Test get_connection when database file doesn't exist."""
        mock_exists.return_value = False
        db_path = "/path/to/nonexistent.db"
        
        with pytest.raises(FileNotFoundError, match="Database file not found"):
            get_connection(db_path)

    @patch('utils.sql_connection.sqlite3.connect')
    @patch('utils.sql_connection.os.path.exists')
    def test_get_connection_sqlite_error(self, mock_exists, mock_connect):
        """Test get_connection with SQLite error."""
        mock_exists.return_value = True
        mock_connect.side_effect = sqlite3.Error("Connection failed")
        
        with pytest.raises(sqlite3.Error):
            get_connection("/path/to/database.db")

    @patch('utils.sql_connection.get_connection')
    def test_get_connection_context_success(self, mock_get_connection):
        """Test successful connection context manager."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection
        
        with get_connection_context("/path/to/db.db") as conn:
            assert conn == mock_connection
        
        mock_connection.close.assert_called_once()

    @patch('utils.sql_connection.get_connection')
    def test_get_connection_context_exception(self, mock_get_connection):
        """Test connection context manager with exception."""
        mock_connection = Mock()
        mock_get_connection.return_value = mock_connection
        
        with pytest.raises(ValueError):
            with get_connection_context("/path/to/db.db") as conn:
                raise ValueError("Test error")
        
        mock_connection.rollback.assert_called_once()
        mock_connection.close.assert_called_once()

    def test_execute_query_success(self):
        """Test successful query execution."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        result = execute_query(mock_connection, "SELECT * FROM users", ("param",))
        
        mock_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users", ("param",))
        assert result == mock_cursor

    def test_execute_query_without_params(self):
        """Test query execution without parameters."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        
        result = execute_query(mock_connection, "SELECT * FROM users")
        
        mock_cursor.execute.assert_called_once_with("SELECT * FROM users")
        assert result == mock_cursor

    def test_execute_query_sqlite_error(self):
        """Test execute_query with SQLite error."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = sqlite3.Error("Query failed")
        
        with pytest.raises(sqlite3.Error):
            execute_query(mock_connection, "INVALID QUERY")

    @patch('utils.sql_connection.execute_query')
    def test_execute_query_safe_success(self, mock_execute_query):
        """Test safe query execution success."""
        mock_cursor = Mock()
        mock_execute_query.return_value = mock_cursor
        mock_connection = Mock()
        
        result = execute_query_safe(mock_connection, "SELECT * FROM users")
        
        assert result == mock_cursor

    @patch('utils.sql_connection.execute_query')
    def test_execute_query_safe_exception(self, mock_execute_query):
        """Test safe query execution with exception."""
        mock_execute_query.side_effect = Exception("Query failed")
        mock_connection = Mock()
        
        result = execute_query_safe(mock_connection, "INVALID QUERY")
        
        assert result is None

    def test_fetch_one_success(self):
        """Test successful single row fetch."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = ("row_data",)
        
        result = fetch_one(mock_cursor)
        
        mock_cursor.fetchone.assert_called_once()
        assert result == ("row_data",)

    def test_fetch_one_no_results(self):
        """Test fetch_one with no results."""
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        result = fetch_one(mock_cursor)
        
        assert result is None

    def test_fetch_one_exception(self):
        """Test fetch_one with exception."""
        mock_cursor = Mock()
        mock_cursor.fetchone.side_effect = Exception("Fetch failed")
        
        result = fetch_one(mock_cursor)
        
        assert result is None

    def test_fetch_all_success(self):
        """Test successful all rows fetch."""
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
        
        result = fetch_all(mock_cursor)
        
        mock_cursor.fetchall.assert_called_once()
        assert result == [("row1",), ("row2",)]

    def test_fetch_all_exception(self):
        """Test fetch_all with exception."""
        mock_cursor = Mock()
        mock_cursor.fetchall.side_effect = Exception("Fetch failed")
        
        result = fetch_all(mock_cursor)
        
        assert result == []

    def test_fetch_many_success(self):
        """Test successful many rows fetch."""
        mock_cursor = Mock()
        mock_cursor.fetchmany.return_value = [("row1",), ("row2",)]
        
        result = fetch_many(mock_cursor, 2)
        
        mock_cursor.fetchmany.assert_called_once_with(2)
        assert result == [("row1",), ("row2",)]

    def test_fetch_many_exception(self):
        """Test fetch_many with exception."""
        mock_cursor = Mock()
        mock_cursor.fetchmany.side_effect = Exception("Fetch failed")
        
        result = fetch_many(mock_cursor, 5)
        
        assert result == []

    @patch('utils.sql_connection.execute_query')
    @patch('utils.sql_connection.fetch_one')
    def test_execute_and_fetch_one(self, mock_fetch_one, mock_execute_query):
        """Test execute and fetch one operation."""
        mock_cursor = Mock()
        mock_execute_query.return_value = mock_cursor
        mock_fetch_one.return_value = ("result",)
        mock_connection = Mock()
        
        result = execute_and_fetch_one(mock_connection, "SELECT * FROM users", (1,))
        
        mock_execute_query.assert_called_once_with(mock_connection, "SELECT * FROM users", (1,))
        mock_fetch_one.assert_called_once_with(mock_cursor)
        assert result == ("result",)

    @patch('utils.sql_connection.execute_query')
    @patch('utils.sql_connection.fetch_all')
    def test_execute_and_fetch_all(self, mock_fetch_all, mock_execute_query):
        """Test execute and fetch all operation."""
        mock_cursor = Mock()
        mock_execute_query.return_value = mock_cursor
        mock_fetch_all.return_value = [("result1",), ("result2",)]
        mock_connection = Mock()
        
        result = execute_and_fetch_all(mock_connection, "SELECT * FROM users")
        
        mock_execute_query.assert_called_once_with(mock_connection, "SELECT * FROM users", None)
        mock_fetch_all.assert_called_once_with(mock_cursor)
        assert result == [("result1",), ("result2",)]

    @patch('utils.sql_connection.execute_query')
    def test_insert_data_success(self, mock_execute_query):
        """Test successful data insertion."""
        mock_cursor = Mock()
        mock_cursor.lastrowid = 123
        mock_execute_query.return_value = mock_cursor
        mock_connection = Mock()
        
        data = {"name": "John", "email": "john@example.com"}
        result = insert_data(mock_connection, "users", data)
        
        expected_query = "INSERT INTO users (name, email) VALUES (?, ?)"
        mock_execute_query.assert_called_once_with(mock_connection, expected_query, ("John", "john@example.com"))
        mock_connection.commit.assert_called_once()
        assert result == 123

    @patch('utils.sql_connection.execute_query')
    def test_insert_data_exception(self, mock_execute_query):
        """Test data insertion with exception."""
        mock_execute_query.side_effect = Exception("Insert failed")
        mock_connection = Mock()
        
        data = {"name": "John"}
        result = insert_data(mock_connection, "users", data)
        
        assert result is None
        mock_connection.rollback.assert_called_once()

    @patch('utils.sql_connection.execute_query')
    def test_update_data_success(self, mock_execute_query):
        """Test successful data update."""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_execute_query.return_value = mock_cursor
        mock_connection = Mock()
        
        data = {"name": "John Updated"}
        result = update_data(mock_connection, "users", data, "id = ?", (1,))
        
        expected_query = "UPDATE users SET name = ? WHERE id = ?"
        mock_execute_query.assert_called_once_with(mock_connection, expected_query, ("John Updated", 1))
        mock_connection.commit.assert_called_once()
        assert result == 1

    @patch('utils.sql_connection.execute_query')
    def test_update_data_exception(self, mock_execute_query):
        """Test data update with exception."""
        mock_execute_query.side_effect = Exception("Update failed")
        mock_connection = Mock()
        
        data = {"name": "John"}
        result = update_data(mock_connection, "users", data, "id = ?", (1,))
        
        assert result == 0
        mock_connection.rollback.assert_called_once()

    @patch('utils.sql_connection.execute_query')
    def test_delete_data_success(self, mock_execute_query):
        """Test successful data deletion."""
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_execute_query.return_value = mock_cursor
        mock_connection = Mock()
        
        result = delete_data(mock_connection, "users", "id = ?", (1,))
        
        expected_query = "DELETE FROM users WHERE id = ?"
        mock_execute_query.assert_called_once_with(mock_connection, expected_query, (1,))
        mock_connection.commit.assert_called_once()
        assert result == 1

    @patch('utils.sql_connection.execute_query')
    def test_delete_data_exception(self, mock_execute_query):
        """Test data deletion with exception."""
        mock_execute_query.side_effect = Exception("Delete failed")
        mock_connection = Mock()
        
        result = delete_data(mock_connection, "users", "id = ?", (1,))
        
        assert result == 0
        mock_connection.rollback.assert_called_once()

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_table_info(self, mock_execute_and_fetch_all):
        """Test get table info."""
        mock_execute_and_fetch_all.return_value = [("column_info",)]
        mock_connection = Mock()
        
        result = get_table_info(mock_connection, "users")
        
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, "PRAGMA table_info(users)")
        assert result == [("column_info",)]

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_table_names(self, mock_execute_and_fetch_all):
        """Test get table names."""
        mock_row1 = {"name": "users"}
        mock_row2 = {"name": "products"}
        mock_execute_and_fetch_all.return_value = [mock_row1, mock_row2]
        mock_connection = Mock()
        
        result = get_table_names(mock_connection)
        
        expected_query = "SELECT name FROM sqlite_master WHERE type='table'"
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, expected_query)
        assert result == ["users", "products"]

    def test_close_connection_success(self):
        """Test successful connection close."""
        mock_connection = Mock()
        
        close_connection(mock_connection)
        
        mock_connection.close.assert_called_once()

    def test_close_connection_exception(self):
        """Test connection close with exception."""
        mock_connection = Mock()
        mock_connection.close.side_effect = Exception("Close failed")
        
        # Should not raise exception
        close_connection(mock_connection)

    def test_close_connection_none(self):
        """Test closing None connection."""
        # Should not raise exception
        close_connection(None)

    @patch('utils.sql_connection.get_connection_context')
    @patch('utils.sql_connection.execute_query')
    @patch('utils.sql_connection.fetch_one')
    def test_test_connection_success(self, mock_fetch_one, mock_execute_query, mock_context):
        """Test successful connection test."""
        mock_connection = Mock()
        mock_context.return_value.__enter__.return_value = mock_connection
        mock_cursor = Mock()
        mock_execute_query.return_value = mock_cursor
        mock_fetch_one.return_value = ("3.39.0",)
        
        result = test_connection("/path/to/db.db")
        
        assert result is True
        mock_execute_query.assert_called_once_with(mock_connection, "SELECT sqlite_version()")
        mock_fetch_one.assert_called_once_with(mock_cursor)

    @patch('utils.sql_connection.get_connection_context')
    def test_test_connection_failure(self, mock_context):
        """Test connection test failure."""
        mock_context.side_effect = Exception("Connection failed")
        
        result = test_connection("/path/to/db.db")
        
        assert result is False


class TestChinookFunctions:
    """Test cases for Chinook database convenience functions."""

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_artists(self, mock_execute_and_fetch_all):
        """Test get_artists function."""
        mock_execute_and_fetch_all.return_value = [("1", "Artist1"), ("2", "Artist2")]
        mock_connection = Mock()
        
        result = get_artists(mock_connection, limit=5)
        
        expected_query = "SELECT ArtistId, Name FROM artists LIMIT ?"
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, expected_query, (5,))
        assert result == [("1", "Artist1"), ("2", "Artist2")]

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_artists_default_limit(self, mock_execute_and_fetch_all):
        """Test get_artists function with default limit."""
        mock_execute_and_fetch_all.return_value = []
        mock_connection = Mock()
        
        get_artists(mock_connection)
        
        expected_query = "SELECT ArtistId, Name FROM artists LIMIT ?"
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, expected_query, (10,))

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_albums_by_artist(self, mock_execute_and_fetch_all):
        """Test get_albums_by_artist function."""
        mock_execute_and_fetch_all.return_value = [("1", "Album1"), ("2", "Album2")]
        mock_connection = Mock()
        
        result = get_albums_by_artist(mock_connection, 5)
        
        expected_query = "SELECT AlbumId, Title FROM albums WHERE ArtistId = ?"
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, expected_query, (5,))
        assert result == [("1", "Album1"), ("2", "Album2")]

    @patch('utils.sql_connection.execute_and_fetch_all')
    def test_get_tracks_by_album(self, mock_execute_and_fetch_all):
        """Test get_tracks_by_album function."""
        mock_execute_and_fetch_all.return_value = [("1", "Track1", 180000), ("2", "Track2", 240000)]
        mock_connection = Mock()
        
        result = get_tracks_by_album(mock_connection, 3)
        
        expected_query = "SELECT TrackId, Name, Milliseconds FROM tracks WHERE AlbumId = ?"
        mock_execute_and_fetch_all.assert_called_once_with(mock_connection, expected_query, (3,))
        assert result == [("1", "Track1", 180000), ("2", "Track2", 240000)]