"""
Google search page implementation using the page object pattern.
"""

from typing import Dict, List

from selenium.webdriver.common.keys import Keys

from locators.google_search_locators import GoogleSearchLocators
from pages.base_page import BasePage


class GoogleSearchPage(BasePage):
    """
    Google search page implementation.
    Provides methods for search operations and result handling.
    """

    def __init__(self, driver_and_db, test_name: str = None, environment: str = "test"):
        """Initialize Google search page with enhanced features."""
        super().__init__(driver_and_db, test_name=test_name, environment=environment)
        from config.settings import settings

        self.page_url = settings.BASE_URL

    def open(self) -> bool:
        """Open Google homepage (alias for open_google)."""
        return self.open_google()

    def search(self, search_term: str) -> bool:
        """Perform search without navigating (assumes already on Google)."""
        # Just search, don't navigate
        if not self.send_keys(GoogleSearchLocators.SEARCH_BOX, search_term):
            return False

        # Submit search using ENTER key
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if element:
            element.send_keys(Keys.RETURN)
            return True
        return False

    def open_google(self) -> bool:
        """Navigate to Google and verify page loaded."""
        if self.navigate_to(self.page_url):
            try:
                return self.wait_for_element(
                    GoogleSearchLocators.SEARCH_BOX, timeout=10
                )
            except Exception:
                return False
        return False

    def navigate_to_google(self) -> bool:
        """Navigate to Google homepage."""
        from config.settings import settings

        return self.navigate_to(settings.BASE_URL)

    def search_for(self, search_term: str, use_enter: bool = True) -> bool:
        """Perform search with given term."""
        # Navigate to Google first
        if not self.navigate_to_google():
            return False

        # Clear and type search term
        if not self.send_keys(GoogleSearchLocators.SEARCH_BOX, search_term):
            return False

        # Submit search
        if use_enter:
            element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
            if element:
                element.send_keys(Keys.RETURN)
                return True
            return False
        else:
            return self.click(GoogleSearchLocators.SEARCH_BUTTON)

    def has_results(self) -> bool:
        """Check if search results are visible."""
        return self.is_element_visible(
            GoogleSearchLocators.RESULTS_CONTAINER, timeout=10
        )

    def get_results_stats(self) -> str:
        """Get search results statistics text."""
        return self.get_text(GoogleSearchLocators.RESULT_STATS)

    def get_result_titles(self, max_count: int = 5) -> List[str]:
        """Get list of search result titles."""
        elements = self.driver.find_elements(*GoogleSearchLocators.RESULT_TITLES)
        titles = []

        for element in elements[:max_count]:
            try:
                title = element.text.strip()
                if title:
                    titles.append(title)
            except Exception:
                continue

        return titles

    def perform_search_workflow(self, search_term: str) -> Dict[str, any]:
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
            # Open Google
            if not self.open_google():
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

        except Exception as e:
            result["error"] = str(e)

        return result

    def get_search_input(self):
        """Get the search input element."""
        return self.find_element(GoogleSearchLocators.SEARCH_BOX)

    def enter_search_term(self, search_term: str) -> bool:
        """Enter search term with enhanced error handling."""
        return self.send_keys(GoogleSearchLocators.SEARCH_BOX, search_term)

    def click_search_button(self) -> bool:
        """Click search button with enhanced features."""
        return self.click(GoogleSearchLocators.SEARCH_BUTTON)

    def capture_search_input_screenshot(self, filename: str) -> str:
        """Capture screenshot of search input area."""
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if element:
            return self.take_screenshot(filename)
        return ""

    def click_search_input_advanced(self) -> bool:
        """Click on search input using advanced method."""
        return self.click(GoogleSearchLocators.SEARCH_BOX)

    def type_with_action_chains(self, text: str) -> bool:
        """Type text using ActionChains."""
        try:
            element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
            if element:
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.driver)
                actions.move_to_element(element).click().send_keys(text).perform()
                return True
            return False
        except Exception:
            return False

    def wait_for_suggestions(self, timeout: int = 5) -> bool:
        """Wait for search suggestions to appear."""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            suggestions_locator = (By.CSS_SELECTOR, "ul[role='listbox']")
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(suggestions_locator)
            )
            return True
        except Exception:
            return False

    def get_search_input_health(self) -> dict:
        """Get health information about the search input element."""
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if not element:
            return {
                "exists": False,
                "is_displayed": False,
                "is_enabled": False,
                "tag_name": None
            }
        
        return {
            "exists": True,
            "is_displayed": element.is_displayed(),
            "is_enabled": element.is_enabled(),
            "tag_name": element.tag_name
        }

    def get_search_input_value(self) -> str:
        """Get the current value of the search input."""
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if element:
            return element.get_attribute("value") or ""
        return ""

    def get_search_input_dimensions(self) -> dict:
        """Get dimensions and position of search input."""
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if not element:
            return {"width": 0, "height": 0, "x": 0, "y": 0}
        
        size = element.size
        location = element.location
        return {
            "width": size.get("width", 0),
            "height": size.get("height", 0),
            "x": location.get("x", 0),
            "y": location.get("y", 0)
        }

    def wait_for_search_input_clickable(self, timeout: int = 10) -> bool:
        """Wait until search input is clickable."""
        try:
            element = self.wait_for_clickable(
                GoogleSearchLocators.SEARCH_BOX,
                timeout=timeout
            )
            return element is not None
        except Exception:
            return False

    def wait_for_search_input_visible(self, timeout: int = 10) -> bool:
        """Wait until search input is visible."""
        try:
            return self.wait_for_element(
                GoogleSearchLocators.SEARCH_BOX,
                timeout=timeout
            ) is not None
        except Exception:
            return False

    def click_search_input(self) -> bool:
        """Click on the search input element."""
        return self.click(GoogleSearchLocators.SEARCH_BOX)

    def wait_for_search_input_focus(self, timeout: int = 5) -> bool:
        """Wait for search input to gain focus."""
        try:
            element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
            if element:
                # Check if element has focus using JavaScript
                import time
                start_time = time.time()
                while time.time() - start_time < timeout:
                    has_focus = self.driver.execute_script(
                        "return document.activeElement === arguments[0]",
                        element
                    )
                    if has_focus:
                        return True
                    time.sleep(0.1)
            return False
        except Exception:
            return False

    def wait_for_text_in_search_input(self, text: str, timeout: int = 10) -> bool:
        """Wait for specific text to appear in search input."""
        try:
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_value = self.get_search_input_value()
                if current_value == text:
                    return True
                time.sleep(0.1)
            return False
        except Exception:
            return False

    def open_google_with_timing(self) -> float:
        """Open Google and return time taken."""
        import time
        start_time = time.time()
        self.open_google()
        return time.time() - start_time

    def get_search_input_timing(self) -> float:
        """Find search input and return time taken."""
        import time
        start_time = time.time()
        self.find_element(GoogleSearchLocators.SEARCH_BOX)
        return time.time() - start_time

    def enter_search_term_with_timing(self, search_term: str) -> float:
        """Enter search term and return time taken."""
        import time
        start_time = time.time()
        self.enter_search_term(search_term)
        return time.time() - start_time

    def clear_and_retype_with_timing(self, search_term: str) -> float:
        """Clear input, retype text, and return time taken."""
        import time
        start_time = time.time()
        element = self.find_element(GoogleSearchLocators.SEARCH_BOX)
        if element:
            element.clear()
            element.send_keys(search_term)
        return time.time() - start_time
