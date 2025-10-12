"""
Search engine page implementation using the page object pattern.
"""

import contextlib
import time
from typing import Optional

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from locators.search_engine_locators import SearchEngineLocators
from pages.base_page import BasePage


class SearchEnginePage(BasePage):
    """
    Search engine page implementation.
    Provides methods for search operations and result handling.
    """

    def __init__(
        self,
        driver_and_db,
        test_name: Optional[str] = None,
        environment: str = "test",
    ):
        """Initialize Search engine page with enhanced features."""
        super().__init__(driver_and_db, test_name=test_name, environment=environment)

        self.page_url = settings.BASE_URL

    def open(self) -> bool:
        """Open Search engine homepage (alias for open_search_engine)."""
        return self.open_search_engine()

    def search(self, search_term: str) -> bool:
        """Perform search without navigating (assumes already on search engine page)."""
        # Just search, don't navigate
        if not self.send_keys(SearchEngineLocators.SEARCH_BOX, search_term):
            return False

        # Submit search using ENTER key
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            element.send_keys(Keys.RETURN)
            return True
        return False

    def open_search_engine(self) -> bool:
        """Navigate to search engine and verify page loaded."""
        if self.navigate_to(self.page_url):
            try:
                return self.wait_for_element(
                    SearchEngineLocators.SEARCH_BOX,
                    timeout=10,
                )
            except TimeoutException:
                return False
        return False

    def navigate_to_search_engine(self) -> bool:
        """Navigate to search engine homepage."""
        return self.navigate_to(settings.BASE_URL)

    def search_for(*, self, search_term: str, use_enter: bool = True) -> bool:
        """Perform search with given term."""
        # Navigate to search engine first
        if not self.navigate_to_search_engine():
            return False

        # Clear and type search term
        if not self.send_keys(SearchEngineLocators.SEARCH_BOX, search_term):
            return False

        # Submit search
        if use_enter:
            element = self.find_element(SearchEngineLocators.SEARCH_BOX)
            if element:
                element.send_keys(Keys.RETURN)
                return True
            return False
        return self.click(SearchEngineLocators.SEARCH_BUTTON)

    def has_results(self) -> bool:
        """Check if search results are visible."""
        return self.is_element_visible(
            SearchEngineLocators.RESULTS_CONTAINER,
            timeout=10,
        )

    def get_results_stats(self) -> str:
        """Get search results statistics text."""
        return self.get_text(SearchEngineLocators.RESULT_STATS)

    def get_result_titles(self, max_count: int = 5) -> list[str]:
        """Get list of search result titles."""
        elements = self.driver.find_elements(*SearchEngineLocators.RESULT_TITLES)
        titles = []
        try:
            for element in elements[:max_count]:
                title = element.text.strip()
                if title:
                    titles.append(title)
        except WebDriverException:
            pass
        return titles

    def perform_search_workflow(self, search_term: str) -> dict[str, any]:
        """
        Complete search workflow that orchestrates the search process.
        """
        result = {
            "search_term": search_term,
            "success": False,
            "has_results": False,
            "stats": "",
            "titles": [],
        }

        try:
            # Open search engine
            if not self.open_search_engine():
                return result

            # Perform search
            if not self.search_for(search_term):
                return result

            # Wait and collect results
            if self.has_results():
                result["has_results"] = True
                result["stats"] = self.get_results_stats()
                result["titles"] = self.get_result_titles()
                result["success"] = True

            # Take screenshot for verification
            self.take_screenshot(f"search_{search_term.replace(' ', '_')}")

        except RuntimeError as e:
            result["error"] = str(e)

        return result

    def get_search_input(self):
        """Get the search input element."""
        return self.find_element(SearchEngineLocators.SEARCH_BOX)

    def enter_search_term(self, search_term: str) -> bool:
        """Enter search term with enhanced error handling."""
        if self.send_keys(SearchEngineLocators.SEARCH_BOX, search_term):
            return True

        # Fallback for headless runs where the native send_keys verification fails
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if not element:
            return False

        with contextlib.suppress(WebDriverException):
            self.driver.execute_script(
                "arguments[0].focus();",
                element,
            )

        try:
            self.driver.execute_script(
                """
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """,
                element,
                search_term,
            )
        except WebDriverException:
            return False

        current_value = (element.get_attribute("value") or "").strip()
        return search_term.strip().lower() in current_value.lower()

    def clear_search(self) -> bool:
        """Clear the search input field."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            self.driver.execute_script("arguments[0].value = '';", element)
            return True
        return False

    def click_search_button(self) -> bool:
        """Click search button with enhanced features."""
        return self.click(SearchEngineLocators.SEARCH_BUTTON)

    def submit_search_with_enter(self) -> bool:
        """Submit search using Enter key (more reliable in headless mode)."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            element.send_keys(Keys.RETURN)
            return True
        return False

    def capture_search_input_screenshot(self, filename: str) -> str:
        """Capture screenshot of search input area."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            return self.take_screenshot(filename)
        return ""

    def click_search_input_advanced(self) -> bool:
        """Click on search input using advanced method."""
        return self.click(SearchEngineLocators.SEARCH_BOX)

    def type_with_action_chains(self, text: str) -> bool:
        """Type text using ActionChains."""
        try:
            element = self.find_element(SearchEngineLocators.SEARCH_BOX)
            if element:
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().send_keys(text).perform()
                return True
        except WebDriverException:
            return False
        else:
            return False

    def wait_for_suggestions(self, timeout: int = 5) -> bool:
        """Wait for search suggestions to appear."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    SearchEngineLocators.SUGGESTIONS_LISTBOX,
                ),
            )
        except TimeoutException:
            return False
        else:
            return True

    def get_search_input_health(self) -> dict:
        """Get health information about the search input element."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
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

    def get_search_input_value(self) -> str:
        """Get the current value of the search input."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            return element.get_attribute("value") or ""
        return ""

    def get_search_input_dimensions(self) -> dict:
        """Get dimensions and position of search input."""
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if not element:
            return {"width": 0, "height": 0, "x": 0, "y": 0}

        size = element.size
        location = element.location
        return {
            "width": size.get("width", 0),
            "height": size.get("height", 0),
            "x": location.get("x", 0),
            "y": location.get("y", 0),
        }

    def wait_for_search_input_clickable(self, timeout: int = 10) -> bool:
        """Wait until search input is clickable."""
        try:
            element = self.wait_for_clickable(
                SearchEngineLocators.SEARCH_BOX,
                timeout=timeout,
            )
        except TimeoutException:
            return False
        else:
            return element is not None

    def wait_for_search_input_visible(self, timeout: int = 10) -> bool:
        """Wait until search input is visible."""
        try:
            return (
                self.wait_for_element(SearchEngineLocators.SEARCH_BOX, timeout=timeout)
                is not None
            )
        except TimeoutException:
            return False

    def click_search_input(self) -> bool:
        """Click on the search input element."""
        return self.click(SearchEngineLocators.SEARCH_BOX)

    def wait_for_search_input_focus(self, timeout: int = 5) -> bool:
        """Wait for search input to gain focus."""
        try:
            element = self.find_element(SearchEngineLocators.SEARCH_BOX)
            if element:
                # Check if element has focus using JavaScript
                start_time = time.time()
                while time.time() - start_time < timeout:
                    has_focus = self.driver.execute_script(
                        "return document.activeElement === arguments[0]",
                        element,
                    )
                    if has_focus:
                        return True
                    time.sleep(0.1)
        except WebDriverException:
            return False
        else:
            return False

    def wait_for_text_in_search_input(self, text: str, timeout: int = 10) -> bool:
        """Wait for specific text (or containing text) to appear in search input."""
        try:
            normalized_expected = (text or "").strip().lower()
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_value = (self.get_search_input_value() or "").strip()
                if not normalized_expected:
                    return current_value == ""

                if normalized_expected in current_value.lower():
                    return True
                time.sleep(0.1)
        except RuntimeError:
            return False
        else:
            return False

    def open_search_engine_with_timing(self) -> float:
        """Open search engine and return time taken."""
        start_time = time.time()
        self.open_search_engine()
        return time.time() - start_time

    def get_search_input_timing(self) -> float:
        """Find search input and return time taken."""
        start_time = time.time()
        self.find_element(SearchEngineLocators.SEARCH_BOX)
        return time.time() - start_time

    def enter_search_term_with_timing(self, search_term: str) -> float:
        """Enter search term and return time taken."""
        start_time = time.time()
        self.enter_search_term(search_term)
        return time.time() - start_time

    def clear_and_retype_with_timing(self, search_term: str) -> float:
        """Clear input, retype text, and return time taken."""
        start_time = time.time()
        element = self.find_element(SearchEngineLocators.SEARCH_BOX)
        if element:
            # Use JavaScript to clear the value for DuckDuckGo compatibility
            self.driver.execute_script("arguments[0].value = '';", element)
            element.send_keys(search_term)
        return time.time() - start_time
