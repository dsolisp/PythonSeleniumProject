"""
Bing search engine page implementation using the Page Object Model pattern.
Demonstrates clean POM architecture with consolidated methods.
"""

import time
from typing import Any

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from locators.search_engine_locators import SearchEngineLocators
from pages.base_page import BasePage


class SearchEnginePage(BasePage):
    """
    Bing search engine page object demonstrating clean POM architecture.
    Consolidated from 355 lines to ~150 lines while keeping all functionality.
    """

    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout=timeout)
        self.page_url = settings.BASE_URL
        self._locators = SearchEngineLocators  # Alias for cleaner code

    # === Core Navigation & Search ===

    def open(self) -> bool:
        """Navigate to search engine and verify page loaded."""
        if not self.navigate_to(self.page_url):
            return False
        return self.wait_for_element(self._locators.SEARCH_BOX, timeout=10) is not None

    def search(
        self, search_term: str, *, navigate_first: bool = False, use_enter: bool = True
    ) -> bool:
        """
        Unified search method - consolidates search/search_for.

        Args:
            search_term: Text to search for
            navigate_first: Whether to navigate to search engine first
            use_enter: Submit with Enter key (True) or click button (False)
        """
        if navigate_first and not self.open():
            return False

        if not self.send_keys(self._locators.SEARCH_BOX, search_term):
            return False

        return self.submit_search(use_enter=use_enter)

    def submit_search(self, *, use_enter: bool = True) -> bool:
        """Submit the search form."""
        if use_enter:
            element = self.find_element(self._locators.SEARCH_BOX)
            if element:
                element.send_keys(Keys.RETURN)
                return True
            return False
        return self.click(self._locators.SEARCH_BUTTON)

    # === Search Input Operations ===

    def get_search_input(self):
        """Get the search input element."""
        return self.find_element(self._locators.SEARCH_BOX)

    def enter_search_term(self, search_term: str) -> bool:
        """Enter search term with fallback validation."""
        if self.send_keys(self._locators.SEARCH_BOX, search_term):
            return True
        # Fallback: check if text was partially entered
        value = self.get_search_input_value()
        return search_term.strip().lower() in value.lower()

    def clear_search(self) -> bool:
        """Clear the search input field using JavaScript."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if element:
            self.execute_script("arguments[0].value = '';", element)
            return True
        return False

    def get_search_input_value(self) -> str:
        """Get current value of search input."""
        element = self.find_element(self._locators.SEARCH_BOX)
        return element.get_attribute("value") or "" if element else ""

    def type_with_action_chains(self, text: str) -> bool:
        """Type text using ActionChains for more reliable input."""
        try:
            element = self.find_element(self._locators.SEARCH_BOX)
            if element:
                ActionChains(self.driver).move_to_element(element).click().send_keys(
                    text
                ).perform()
                return True
        except WebDriverException:
            pass
        return False

    def click_search_input(self) -> bool:
        """Click on search input element."""
        return self.click(self._locators.SEARCH_BOX)

    # === Results Handling ===

    def has_results(self) -> bool:
        """Check if search results are visible."""
        return self.is_element_visible(self._locators.RESULTS_CONTAINER, timeout=10)

    def get_results_stats(self) -> str:
        """Get search results statistics text."""
        return self.get_text(self._locators.RESULT_STATS)

    def get_result_titles(self, max_count: int = 5) -> list[str]:
        """Get list of search result titles."""
        try:
            elements = self.find_elements(self._locators.RESULT_TITLES)
            return [e.text.strip() for e in elements[:max_count] if e.text.strip()]
        except WebDriverException:
            return []

    # === Wait Conditions ===

    def wait_for_suggestions(self, timeout: int = 5) -> bool:
        """Wait for search suggestions to appear."""
        return (
            self.wait_for_element(self._locators.SUGGESTIONS_LISTBOX, timeout=timeout)
            is not None
        )

    def wait_for_search_input_clickable(self, timeout: int = 10) -> bool:
        """Wait until search input is clickable."""
        return (
            self.wait_for_clickable(self._locators.SEARCH_BOX, timeout=timeout)
            is not None
        )

    def wait_for_search_input_visible(self, timeout: int = 10) -> bool:
        """Wait until search input is visible."""
        return (
            self.wait_for_element(self._locators.SEARCH_BOX, timeout=timeout)
            is not None
        )

    def wait_for_search_input_focus(self, timeout: int = 5) -> bool:
        """Wait for search input to gain focus using JavaScript."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if not element:
            return False

        end_time = time.time() + timeout
        while time.time() < end_time:
            if self.execute_script(
                "return document.activeElement === arguments[0]", element
            ):
                return True
            time.sleep(0.1)
        return False

    def wait_for_text_in_search_input(self, text: str, timeout: int = 10) -> bool:
        """Wait for specific text to appear in search input."""
        expected = (text or "").strip().lower()
        end_time = time.time() + timeout

        while time.time() < end_time:
            current = self.get_search_input_value().strip().lower()
            if (not expected and not current) or (expected and expected in current):
                return True
            time.sleep(0.1)
        return False

    # === Element Health & Diagnostics ===

    def get_search_input_health(self) -> dict[str, Any]:
        """Return health status of the search input element."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if not element:
            return {
                "exists": False,
                "is_displayed": False,
                "is_enabled": False,
                "tag_name": None,
            }

        return {
            "exists": True,
            "is_displayed": element.is_displayed(),
            "is_enabled": element.is_enabled(),
            "tag_name": element.tag_name,
        }

    def get_search_input_dimensions(self) -> dict[str, int]:
        """Get dimensions and position of search input."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if not element:
            return {"width": 0, "height": 0, "x": 0, "y": 0}
        return {**element.size, **element.location}

    # === Workflow Methods ===

    def perform_search_workflow(self, search_term: str) -> dict[str, Any]:
        """Execute full search workflow and return results summary."""
        result = {
            "search_term": search_term,
            "success": False,
            "has_results": False,
            "stats": "",
            "titles": [],
        }

        try:
            if self.open() and self.search(search_term) and self.has_results():
                result.update(
                    has_results=True,
                    stats=self.get_results_stats(),
                    titles=self.get_result_titles(),
                    success=True,
                )
            self.take_screenshot(f"search_{search_term.replace(' ', '_')}")
        except RuntimeError as e:
            result["error"] = str(e)

        return result

    def capture_search_input_screenshot(self, filename: str) -> str:
        """Capture screenshot - simplified from original."""
        return self.take_screenshot(filename)
