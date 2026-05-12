"""Login page object for SauceDemo."""

from __future__ import annotations

from config.constants import URLS
from locators.sauce.inventory_locators import InventoryLocators
from locators.sauce.login_locators import LoginLocators
from pages.base_page import BasePage


class LoginPage(BasePage):
    """SauceDemo Login page.

    Responsibilities: navigate, enter credentials, surface errors.
    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).
    """

    def open(self) -> LoginPage:
        """Navigate to the login page and return self for chaining."""
        self.navigate_to(f"{URLS.SAUCE_DEMO}/")
        return self

    def is_loaded(self) -> bool:
        """Return True when the login form is visible."""
        return self.wait_for_element(LoginLocators.USERNAME_INPUT) is not None

    def login(self, username: str, password: str) -> None:
        """Enter credentials and submit the login form."""
        self.send_keys(LoginLocators.USERNAME_INPUT, username)
        self.send_keys(LoginLocators.PASSWORD_INPUT, password)
        self.click(LoginLocators.LOGIN_BUTTON)

    def is_logged_in(self) -> bool:
        """Return True when the inventory list is visible after login."""
        return self.wait_for_element(InventoryLocators.INVENTORY_LIST) is not None

    def get_error_message(self) -> str | None:
        """Return error banner text, or None if no error is shown."""
        error = self.wait_for_element(LoginLocators.ERROR_MESSAGE)
        return error.text if error else None
