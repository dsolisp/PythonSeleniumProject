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
