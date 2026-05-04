"""UserBuilder — fluent builder for SauceDemo credentials."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserCredentials:
    """Value object representing a set of login credentials."""

    username: str
    password: str


class UserBuilder:
    """Builds UserCredentials via a fluent API.

    Usage::

        creds = UserBuilder().standard().build()
        creds = UserBuilder().with_username("locked_out_user").build()
    """

    _DEFAULT_PASSWORD = "secret_sauce"

    def __init__(self) -> None:
        self._username = "standard_user"
        self._password = self._DEFAULT_PASSWORD

    # ── Preset methods ────────────────────────────────────────────────────────

    def standard(self) -> UserBuilder:
        self._username = "standard_user"
        return self

    def locked_out(self) -> UserBuilder:
        self._username = "locked_out_user"
        return self

    def problem(self) -> UserBuilder:
        self._username = "problem_user"
        return self

    def performance_glitch(self) -> UserBuilder:
        self._username = "performance_glitch_user"
        return self

    # ── Custom overrides ──────────────────────────────────────────────────────

    def with_username(self, username: str) -> UserBuilder:
        self._username = username
        return self

    def with_password(self, password: str) -> UserBuilder:
        self._password = password
        return self

    # ── Terminal method ───────────────────────────────────────────────────────

    def build(self) -> UserCredentials:
        return UserCredentials(username=self._username, password=self._password)
