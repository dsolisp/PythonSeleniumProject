"""
Comprehensive tests for SQL validation functions to prevent injection attacks.
Tests ensure _validate_table_name and _validate_column_name cannot be bypassed.
"""

import pytest

from utils.sql_connection import _validate_column_name, _validate_table_name


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
        "invalid_name,description",
        [
            ("users; DROP TABLE users--", "SQL injection with semicolon"),
            ("users' OR '1'='1", "SQL injection with quotes"),
            ("users/*comment*/", "SQL comment injection"),
            ("users--", "SQL comment dashes"),
            ("users#", "MySQL comment"),
            ("users/**/OR/**/1=1", "Obfuscated SQL injection"),
            ("users UNION SELECT", "UNION injection"),
            ("users WHERE 1=1", "WHERE clause injection"),
            ("table name", "Space in name"),
            ("table-name", "Hyphen in name"),
            ("table.name", "Dot in name"),
            ("table`name", "Backtick in name"),
            ("table'name", "Single quote in name"),
            ('table"name', "Double quote in name"),
            ("table;name", "Semicolon in name"),
            ("table(name)", "Parentheses in name"),
            ("table[name]", "Brackets in name"),
            ("table{name}", "Braces in name"),
            ("table@name", "At symbol in name"),
            ("table$name", "Dollar sign in name"),
            ("table%name", "Percent in name"),
            ("table&name", "Ampersand in name"),
            ("table*name", "Asterisk in name"),
            ("table+name", "Plus in name"),
            ("table=name", "Equals in name"),
            ("table/name", "Slash in name"),
            ("table\\name", "Backslash in name"),
            ("table|name", "Pipe in name"),
            ("table<name>", "Angle brackets in name"),
            ("", "Empty string"),
            (" ", "Whitespace only"),
            ("\t", "Tab character"),
            ("\n", "Newline character"),
            ("table\x00name", "Null byte injection"),
        ],
    )
    def test_invalid_table_names(self, invalid_name, description):
        """Invalid table names should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid table name|cannot be empty"):
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
        "invalid_name,description",
        [
            ("col; DROP TABLE users--", "SQL injection with semicolon"),
            ("col' OR '1'='1", "SQL injection with quotes"),
            ("col/*comment*/", "SQL comment injection"),
            ("col--", "SQL comment dashes"),
            ("col#", "MySQL comment"),
            ("col/**/OR/**/1=1", "Obfuscated SQL injection"),
            ("col UNION SELECT", "UNION injection"),
            ("col WHERE 1=1", "WHERE clause injection"),
            ("col name", "Space in name"),
            ("col-name", "Hyphen in name"),
            ("col.name", "Dot in name"),
            ("col`name", "Backtick in name"),
            ("col'name", "Single quote in name"),
            ('col"name', "Double quote in name"),
            ("col;name", "Semicolon in name"),
            ("col(name)", "Parentheses in name"),
            ("col[name]", "Brackets in name"),
            ("col{name}", "Braces in name"),
            ("col@name", "At symbol in name"),
            ("col$name", "Dollar sign in name"),
            ("col%name", "Percent in name"),
            ("col&name", "Ampersand in name"),
            ("col*name", "Asterisk in name"),
            ("col+name", "Plus in name"),
            ("col=name", "Equals in name"),
            ("col/name", "Slash in name"),
            ("col\\name", "Backslash in name"),
            ("col|name", "Pipe in name"),
            ("col<name>", "Angle brackets in name"),
            ("", "Empty string"),
            (" ", "Whitespace only"),
            ("\t", "Tab character"),
            ("\n", "Newline character"),
            ("col\x00name", "Null byte injection"),
        ],
    )
    def test_invalid_column_names(self, invalid_name, description):
        """Invalid column names should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid column name|cannot be empty"):
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

        with pytest.raises(ValueError):
            validated_cols = [
                _validate_column_name(col) for col in malicious_data.keys()
            ]


class TestWhereClauseValidation:
    """Test WHERE clause parameter validation in update_data and delete_data."""

    def test_update_data_requires_params_for_placeholders(self):
        """update_data should return 0 if WHERE clause has ? but no params."""
        from unittest.mock import MagicMock, patch

        from utils.sql_connection import update_data

        mock_conn = MagicMock()
        data = {"name": "Jane"}

        # Should return 0 if WHERE clause has ? but no params
        # (caught by ValueError handler)
        with patch("utils.sql_connection.logger"):
            result = update_data(mock_conn, "users", data, "id = ?", None)
        assert result == 0

    def test_update_data_accepts_params_with_placeholders(self):
        """update_data should accept properly parameterized WHERE clauses."""
        from unittest.mock import MagicMock, patch

        from utils.sql_connection import update_data

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
        from unittest.mock import MagicMock, patch

        from utils.sql_connection import delete_data

        mock_conn = MagicMock()

        # Should return 0 if WHERE clause has ? but no params
        # (caught by ValueError handler)
        with patch("utils.sql_connection.logger"):
            result = delete_data(mock_conn, "users", "id = ?", None)
        assert result == 0

    def test_delete_data_accepts_params_with_placeholders(self):
        """delete_data should accept properly parameterized WHERE clauses."""
        from unittest.mock import MagicMock, patch

        from utils.sql_connection import delete_data

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.cursor.return_value = mock_cursor

        # Should succeed with proper parameterization
        with patch("utils.sql_connection.logger"):
            result = delete_data(mock_conn, "users", "id = ?", (1,))
        assert result == 1
