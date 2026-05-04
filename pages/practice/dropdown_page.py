"""Dropdown page object for the Practice App (/dropdown.html)."""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.settings import settings
from locators.practice.dropdown_locators import DropdownLocators
from pages.base_page import BasePage


class DropdownPage(BasePage):
    """Practice App Dropdown page (ADV-E1, ADV-E2).

    Responsibilities: navigate, select dropdown options, surface status text.
    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).
    """

    def open(self) -> "DropdownPage":
        """Navigate to the dropdown page and return self for chaining."""
        self.navigate_to(f"{settings.PRACTICE_BASE_URL}/dropdown.html")
        return self

    # ── ADV-E1: Static dropdown ───────────────────────────────────────────

    def select_static(self, value: str) -> "DropdownPage":
        """Select an option from the static dropdown by value."""
        element = self.wait_for_element(DropdownLocators.STATIC_DROPDOWN)
        if element:
            Select(element).select_by_value(value)
        return self

    def get_static_status(self) -> str:
        """Return the static dropdown status text."""
        return self.get_text(DropdownLocators.STATIC_STATUS)

    def is_static_dropdown_visible(self) -> bool:
        """Return True when the static dropdown is visible."""
        return self.is_element_visible(DropdownLocators.STATIC_DROPDOWN)

    # ── ADV-E2: Dynamic dropdown ──────────────────────────────────────────

    def is_dynamic_dropdown_disabled(self) -> bool:
        """Return True when the dynamic dropdown is still loading (disabled)."""
        element = self.wait_for_element(DropdownLocators.DYNAMIC_DROPDOWN)
        if element:
            return not element.is_enabled()
        return True

    def is_dynamic_dropdown_enabled(self) -> bool:
        """Return True once the dynamic dropdown has finished loading."""
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(DropdownLocators.DYNAMIC_DROPDOWN)
            )
            return element is not None
        except Exception:  # noqa: BLE001
            return False

    def select_dynamic(self, value: str) -> "DropdownPage":
        """Select an option from the dynamic dropdown by value (after it has loaded)."""
        element = self.wait_for_element(DropdownLocators.DYNAMIC_DROPDOWN)
        if element:
            Select(element).select_by_value(value)
        return self

    def get_dynamic_status(self) -> str:
        """Return the dynamic dropdown status text."""
        return self.get_text(DropdownLocators.DYNAMIC_STATUS)
