"""
Bing search engine page implementation using the Page Object Model pattern.
Demonstrates clean POM architecture with consolidated methods.
"""

import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from locators.search_engine_locators import SearchEngineLocators
from pages.base_page import TIMEOUT_DEFAULT, BasePage


class SearchEnginePage(BasePage):
    """Bing search engine page object with clean POM architecture."""

    def __init__(self, driver):
        super().__init__(driver)
        self.page_url = settings.BASE_URL
        self._locators = SearchEngineLocators

    # === Core Navigation & Search ===

    def open(self):
        """Navigate to search engine. Returns True on success."""
        if not self.navigate_to(self.page_url):
            return False
        return self.wait_for_element(self._locators.SEARCH_BOX) is not None

    def search(self, search_term, *, navigate_first=False, use_enter=True):
        """
        Perform a search.

        Args:
            search_term: Text to search for
            navigate_first: Whether to navigate to search engine first
            use_enter: Submit with Enter key (True) or click button (False)

        Returns True on success.
        """
        if navigate_first and not self.open():
            return False

        if not self.send_keys(self._locators.SEARCH_BOX, search_term):
            return False

        return self.submit_search(use_enter=use_enter)

    def submit_search(self, *, use_enter=True):
        """Submit the search form. Returns True on success."""
        if use_enter:
            element = self.find_element(self._locators.SEARCH_BOX)
            if element:
                element.send_keys(Keys.RETURN)
                return True
            return False
        return self.click(self._locators.SEARCH_BUTTON)

    # === Search Input Operations ===

    def get_search_input(self):
        """Get the search input WebElement or None."""
        return self.find_element(self._locators.SEARCH_BOX)

    def enter_search_term(self, search_term):
        """Enter search term. Returns True on success."""
        if self.send_keys(self._locators.SEARCH_BOX, search_term):
            return True
        # Fallback: check if text was partially entered
        value = self.get_search_input_value()
        return search_term.strip().lower() in value.lower()

    def clear_search(self):
        """Clear the search input field. Returns True on success."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if element:
            self.execute_script("arguments[0].value = '';", element)
            return True
        return False

    def get_search_input_value(self):
        """Get current value of search input. Returns string."""
        element = self.find_element(self._locators.SEARCH_BOX)
        return element.get_attribute("value") or "" if element else ""

    def type_with_action_chains(self, text):
        """Type text using ActionChains. Returns True on success."""
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

    def click_search_input(self):
        """Click on search input. Returns True on success."""
        return self.click(self._locators.SEARCH_BOX)

    # === Results Handling ===

    def has_results(self):
        """Check if search results are visible. Returns True or False."""
        return self.is_element_visible(self._locators.RESULTS_CONTAINER)

    def get_results_stats(self):
        """Get search results statistics text. Returns string."""
        return self.get_text(self._locators.RESULT_STATS)

    def get_result_titles(self, max_count=5):
        """Get list of search result titles. Returns list of strings."""
        try:
            elements = self.find_elements(self._locators.RESULT_TITLES)
            return [e.text.strip() for e in elements[:max_count] if e.text.strip()]
        except WebDriverException:
            return []

    # === Wait Conditions ===

    def wait_for_suggestions(self):
        """Wait for search suggestions. Returns True if found."""
        return self.wait_for_element(self._locators.SUGGESTIONS_LISTBOX) is not None

    def wait_for_search_input_clickable(self):
        """Wait until search input is clickable. Returns True if clickable."""
        return self.wait_for_clickable(self._locators.SEARCH_BOX) is not None

    def wait_for_search_input_visible(self):
        """Wait until search input is visible. Returns True if visible."""
        return self.wait_for_element(self._locators.SEARCH_BOX) is not None

    def wait_for_search_input_focus(self):
        """Wait for search input to gain focus. Returns True if focused."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if not element:
            return False

        end_time = time.time() + TIMEOUT_DEFAULT
        while time.time() < end_time:
            if self.execute_script(
                "return document.activeElement === arguments[0]", element
            ):
                return True
            time.sleep(0.1)
        return False

    def wait_for_text_in_search_input(self, text):
        """Wait for text to appear in search input. Returns True if found."""
        expected = (text or "").strip().lower()
        end_time = time.time() + TIMEOUT_DEFAULT

        while time.time() < end_time:
            current = self.get_search_input_value().strip().lower()
            if (not expected and not current) or (expected and expected in current):
                return True
            time.sleep(0.1)
        return False

    # === Element Health & Diagnostics ===

    def get_search_input_health(self):
        """Return health status dict of the search input element."""
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

    def get_search_input_dimensions(self):
        """Get dimensions and position dict of search input."""
        element = self.find_element(self._locators.SEARCH_BOX)
        if not element:
            return {"width": 0, "height": 0, "x": 0, "y": 0}
        return {**element.size, **element.location}

    # === Workflow Methods ===

    def perform_search_workflow(self, search_term):
        """Execute full search workflow. Returns results dict."""
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

    def capture_search_input_screenshot(self, filename):
        """Capture screenshot. Returns filepath or empty string."""
        return self.take_screenshot(filename)
