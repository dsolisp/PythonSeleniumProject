"""
Tests for SQL identifier validation to prevent injection attacks.
"""

import pytest

from utils.sql_connection import _validate_identifier


class TestIdentifierValidation:
    """Test _validate_identifier against SQL injection attempts."""

    @pytest.mark.parametrize("valid", [
        "users", "test_data", "table_123", "_private", "TABLE2024",
    ])
    def test_valid_identifiers(self, valid):
        """Valid identifiers should pass validation."""
        assert _validate_identifier(valid) == valid

    @pytest.mark.parametrize("invalid", [
        "users; DROP TABLE users--",
        "users' OR '1'='1",
        "table name",  # space
        "table-name",  # dash
        "table.name",  # dot
        "table;name",  # semicolon
        "",  # empty
    ])
    def test_invalid_identifiers_rejected(self, invalid):
        """SQL injection attempts should raise ValueError."""
        with pytest.raises(ValueError):
            _validate_identifier(invalid)

    def test_multiple_identifiers(self):
        """Multiple identifiers should all validate correctly."""
        columns = ["id", "name", "email", "created_at"]
        validated = [_validate_identifier(col) for col in columns]
        assert validated == columns

    def test_malicious_column_in_dict(self):
        """Malicious column names in dict keys should be caught."""
        malicious_data = {"col' OR '1'='1": "value"}
        with pytest.raises(ValueError):
            [_validate_identifier(col) for col in malicious_data]
