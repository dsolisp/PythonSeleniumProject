"""
Comprehensive tests for SQL validation functions to prevent injection attacks.
Tests ensure _validate_table_name and _validate_column_name cannot be bypassed.
"""

from unittest.mock import MagicMock, patch

import pytest

from utils.sql_connection import (
    _validate_column_name,
    _validate_table_name,
    delete_data,
    update_data,
)


class TestTableNameValidation:
    """Test _validate_table_name against SQL injection attempts."""

    @pytest.mark.parametrize(
        "valid_name",
        [
            "users",
            "test_data",
            "table_123",
            "_private",
            "TABLE2024",
            "a1b2c3",
            "user_profile_data",
        ],
    )
    def test_valid_table_names(self, valid_name):
        """Valid table names should pass validation."""
        assert _validate_table_name(valid_name) == valid_name

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "users; DROP TABLE users--",
            "users' OR '1'='1",
            "users/*comment*/",
            "users--",
            "users#",
            "users/**/OR/**/1=1",
            "users UNION SELECT",
            "users WHERE 1=1",
            "table name",
            "table-name",
            "table.name",
            "table`name",
            "table'name",
            'table"name',
            "table;name",
            "table(name)",
            "table[name]",
            "table{name}",
            "table@name",
            "table$name",
            "table%name",
            "table&name",
            "table*name",
            "table+name",
            "table=name",
            "table/name",
            "table\\name",
            "table|name",
            "table<name>",
            "",
            " ",
            "\t",
            "\n",
            "table\x00name",
        ],
    )
    def test_invalid_table_names(self, invalid_name):
        """Invalid table names should raise ValueError."""
        with pytest.raises(ValueError, match=r"Invalid table name|cannot be empty"):
            _validate_table_name(invalid_name)

    def test_empty_string_explicit_message(self):
        """Empty string should raise specific error."""
        with pytest.raises(ValueError, match="Table name cannot be empty"):
            _validate_table_name("")


class TestColumnNameValidation:
    """Test _validate_column_name against SQL injection attempts."""

    @pytest.mark.parametrize(
        "valid_name",
        [
            "id",
            "user_name",
            "email_address",
            "_private_field",
            "column123",
            "COL_UPPER",
            "a1b2c3",
            "data_2024_01",
        ],
    )
    def test_valid_column_names(self, valid_name):
        """Valid column names should pass validation."""
        assert _validate_column_name(valid_name) == valid_name

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "col; DROP TABLE users--",
            "col' OR '1'='1",
            "col/*comment*/",
            "col--",
            "col#",
            "col/**/OR/**/1=1",
            "col UNION SELECT",
            "col WHERE 1=1",
            "col name",
            "col-name",
            "col.name",
            "col`name",
            "col'name",
            'col"name',
            "col;name",
            "col(name)",
            "col[name]",
            "col{name}",
            "col@name",
            "col$name",
            "col%name",
            "col&name",
            "col*name",
            "col+name",
            "col=name",
            "col/name",
            "col\\name",
            "col|name",
            "col<name>",
            "",
            " ",
            "\t",
            "\n",
            "col\x00name",
        ],
    )
    def test_invalid_column_names(self, invalid_name):
        """Invalid column names should raise ValueError."""
        with pytest.raises(ValueError, match=r"Invalid column name|cannot be empty"):
            _validate_column_name(invalid_name)

    def test_empty_string_explicit_message(self):
        """Empty string should raise specific error."""
        with pytest.raises(ValueError, match="Column name cannot be empty"):
            _validate_column_name("")


class TestValidationIntegration:
    """Test validation functions work together correctly."""

    def test_both_validations_in_sequence(self):
        """Both validations should work when called in sequence."""
        table = _validate_table_name("users")
        column = _validate_column_name("email")
        assert table == "users"
        assert column == "email"

    def test_multiple_columns_validation(self):
        """Multiple column names should all validate correctly."""
        columns = ["id", "name", "email", "created_at"]
        validated = [_validate_column_name(col) for col in columns]
        assert validated == columns

    def test_validation_prevents_query_construction_bypass(self):
        """Validation should prevent bypassing query construction."""
        # This simulates how INSERT uses the validation
        malicious_data = {"col' OR '1'='1": "value"}

        with pytest.raises(ValueError, match="Invalid column name"):
            [_validate_column_name(col) for col in malicious_data]


class TestWhereClauseValidation:
    """Test WHERE clause parameter validation in update_data and delete_data."""

    def test_update_data_requires_params_for_placeholders(self):
        """update_data should return 0 if WHERE clause has ? but no params."""
        mock_conn = MagicMock()
        data = {"name": "Jane"}

        # Should return 0 if WHERE clause has ? but no params
        # (caught by ValueError handler)
        with patch("utils.sql_connection.logger"):
            result = update_data(mock_conn, "users", data, "id = ?", None)
        assert result == 0

    def test_update_data_accepts_params_with_placeholders(self):
        """update_data should accept properly parameterized WHERE clauses."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor

        data = {"name": "Jane"}

        # Should succeed with proper parameterization
        with patch("utils.sql_connection.logger"):
            result = update_data(mock_conn, "users", data, "id = ?", (1,))
        assert result == 1

    def test_delete_data_requires_params_for_placeholders(self):
        """delete_data should return 0 if WHERE clause has ? but no params."""
        mock_conn = MagicMock()

        # Should return 0 if WHERE clause has ? but no params
        # (caught by ValueError handler)
        with patch("utils.sql_connection.logger"):
            result = delete_data(mock_conn, "users", "id = ?", None)
        assert result == 0

    def test_delete_data_accepts_params_with_placeholders(self):
        """delete_data should accept properly parameterized WHERE clauses."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor

        # Should succeed with proper parameterization
        with patch("utils.sql_connection.logger"):
            result = delete_data(mock_conn, "users", "id = ?", (1,))
        assert result == 1
