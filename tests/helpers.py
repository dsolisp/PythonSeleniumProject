"""
Shared test helper functions and utilities.

This module contains reusable helper functions used across multiple test files.
Functions here should be generic test utilities, not specific to particular
frameworks or factories (those belong in their respective factory classes).
"""

import contextlib
from collections.abc import Iterator
from typing import Optional

import pytest


class SoftAssert:
    """Collects assertion failures and reports them together on context exit.

    Mirrors the C# FluentAssertions ``AssertionScope`` and Java soft-assert
    pattern: every check runs even if an earlier one failed, and all failures
    are reported at once instead of stopping at the first.
    """

    def __init__(self) -> None:
        self._failures: list[str] = []

    def check(self, condition: object, message: str = "assertion failed") -> None:
        """Record a failure when ``condition`` is falsy."""
        if not condition:
            self._failures.append(message)

    def equal(
        self,
        actual: object,
        expected: object,
        message: Optional[str] = None,
    ) -> None:
        """Record a failure when ``actual`` does not equal ``expected``."""
        if actual != expected:
            self._failures.append(
                message or f"expected {expected!r} but was {actual!r}",
            )

    def contains(
        self,
        container: object,
        member: object,
        message: Optional[str] = None,
    ) -> None:
        """Record a failure when ``member`` is not in ``container``."""
        if member not in container:  # type: ignore[operator]
            self._failures.append(
                message or f"expected {container!r} to contain {member!r}",
            )

    def not_contains(
        self,
        container: object,
        member: object,
        message: Optional[str] = None,
    ) -> None:
        """Record a failure when ``member`` is in ``container``."""
        if member in container:  # type: ignore[operator]
            self._failures.append(
                message or f"expected {container!r} not to contain {member!r}",
            )

    def assert_all(self) -> None:
        """Raise an aggregated ``AssertionError`` if any check failed."""
        if self._failures:
            joined = "\n".join(f"  - {failure}" for failure in self._failures)
            count = len(self._failures)
            raise AssertionError(f"{count} soft assertion(s) failed:\n{joined}")


@contextlib.contextmanager
def soft_assert() -> Iterator[SoftAssert]:
    """Yield a :class:`SoftAssert`; raise aggregated failures on block exit.

    Example::

        with soft_assert() as check:
            check.check(page.is_visible(), "widget should be visible")
            check.contains("Loaded", page.status())
    """
    checker = SoftAssert()
    yield checker
    checker.assert_all()


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
            "Database connection not available - driver fixture must return "
            "(driver, db)",
        )
