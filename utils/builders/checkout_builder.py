"""CheckoutBuilder — fluent builder for checkout form data."""

from __future__ import annotations

from pages.sauce.checkout_page import CheckoutInfo

try:
    from faker import Faker as _Faker

    _faker = _Faker()
except ImportError:  # faker not yet installed; fallback for CI bootstrap
    _faker = None  # type: ignore[assignment]


class CheckoutBuilder:
    """Builds CheckoutInfo via a fluent API.

    Usage::

        info = CheckoutBuilder().with_random_data().build()
        info = CheckoutBuilder().with_first_name("Jane").build()
    """

    def __init__(self) -> None:
        self._first_name = "Test"
        self._last_name = "User"
        self._postal_code = "12345"

    # ── Preset methods ────────────────────────────────────────────────────────

    def with_random_data(self) -> CheckoutBuilder:
        """Populate all fields with Faker-generated realistic data."""
        if _faker is not None:
            self._first_name = _faker.first_name()
            self._last_name = _faker.last_name()
            self._postal_code = _faker.postcode()
        return self

    # ── Custom overrides ──────────────────────────────────────────────────────

    def with_first_name(self, first_name: str) -> CheckoutBuilder:
        self._first_name = first_name
        return self

    def with_last_name(self, last_name: str) -> CheckoutBuilder:
        self._last_name = last_name
        return self

    def with_postal_code(self, postal_code: str) -> CheckoutBuilder:
        self._postal_code = postal_code
        return self

    # ── Terminal method ───────────────────────────────────────────────────────

    def build(self) -> CheckoutInfo:
        return CheckoutInfo(
            first_name=self._first_name,
            last_name=self._last_name,
            postal_code=self._postal_code,
        )
