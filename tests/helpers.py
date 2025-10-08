"""
Shared test helper functions and utilities.

This module contains reusable helper functions used across multiple test files.
Functions here should be generic test utilities, not specific to particular
frameworks or factories (those belong in their respective factory classes).
"""

import pytest


def require_database_connection(driver):
    """
    Helper function to ensure driver fixture provides database connection.

    This function is used in tests that require database connectivity.
    It validates that the driver fixture returns a tuple containing both
    the WebDriver instance and a database connection.

    Args:
        driver: Driver fixture that should be a tuple (driver, db_connection)

    Raises:
        pytest.skip: If driver is not a tuple with database connection

    Example:
        >>> def test_with_db(driver):
        ...     require_database_connection(driver)
        ...     web_driver, db_conn = driver
        ...     # Test code that uses both driver and database
    """
    if not (isinstance(driver, (tuple, list)) and len(driver) > 1):
        pytest.skip(
            "Database connection not available - driver fixture must return (driver, db)"
        )
