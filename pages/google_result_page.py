from locators.google_result_locators import GoogleResultLocators
from pages.base_page import BasePage


class GoogleResultPage(BasePage):
    def __init__(self, driver_and_db, test_name: str = None, environment: str = "test"):
        """Initialize Google result page with enhanced features."""
        super().__init__(driver_and_db, test_name=test_name, environment=environment)
        self.google_result_locators = GoogleResultLocators()

    # Locators

    def get_result_by_name(self, name):
        return self.driver.find_element(
            *self.google_result_locators.get_result_by_name(name)
        )

    def get_result_by_index(self, index):
        return self.driver.find_element(
            *self.google_result_locators.get_result_by_index(index)
        )

    def is_results_displayed(self) -> bool:
        """Check if search results are displayed."""
        try:
            # Look for common result indicators using locators
            results_found = (
                self.is_element_visible(self.google_result_locators.SEARCH_RESULTS) or
                len(self.driver.find_elements(*self.google_result_locators.ALL_H3_ELEMENTS)) > 0 or
                len(self.driver.find_elements(*self.google_result_locators.RESULT_ELEMENTS_DATA_VED)) > 0
            )
            return results_found
        except:
            return False

    def get_results_count(self) -> int:
        """Get the number of search results found."""
        try:
            # Try multiple strategies to count results using locators
            h3_elements = self.driver.find_elements(*self.google_result_locators.ALL_H3_ELEMENTS)
            if h3_elements:
                return len(h3_elements)
            
            # Fallback to other result indicators
            result_elements = self.driver.find_elements(*self.google_result_locators.RESULT_ELEMENTS_DATA_VED)
            return len(result_elements)
        except:
            return 0
