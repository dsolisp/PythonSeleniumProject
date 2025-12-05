from selenium.common.exceptions import NoSuchElementException, WebDriverException

from locators.result_page_locators import ResultPageLocators
from pages.base_page import BasePage


class ResultPage(BasePage):
    """Search result page using BasePage methods exclusively."""

    def __init__(self, driver):
        """Initialize search engine result page."""
        super().__init__(driver)
        self.result_locators = ResultPageLocators()

    def get_result_by_name(self, name):
        """Get result element by name."""
        return self.find_element(self.result_locators.get_result_by_name(name))

    def get_result_by_index(self, index):
        """Get result element by index."""
        return self.find_element(self.result_locators.get_result_by_index(index))

    def get_search_results(self):
        """Get all search result elements."""
        return self.find_elements(self.result_locators.RESULT_ITEMS)

    def get_first_result(self):
        """Get the first search result article element."""
        return self.find_element(self.result_locators.get_first_result_article())

    def is_results_displayed(self):
        """Check if search results are displayed. Returns True or False."""
        try:
            return (
                self.is_element_visible(self.result_locators.SEARCH_RESULTS)
                or len(self.find_elements(self.result_locators.ALL_H3_ELEMENTS)) > 0
                or len(
                    self.find_elements(self.result_locators.RESULT_ELEMENTS_DATA_VED)
                )
                > 0
            )
        except (NoSuchElementException, WebDriverException):
            return False

    def get_results_count(self):
        """Get the number of search results. Returns int."""
        try:
            h3_elements = self.find_elements(self.result_locators.ALL_H3_ELEMENTS)
            if h3_elements:
                return len(h3_elements)

            result_elements = self.find_elements(
                self.result_locators.RESULT_ELEMENTS_DATA_VED
            )
            return len(result_elements)
        except (NoSuchElementException, WebDriverException):
            return 0

    def wait_for_results_page(self):
        """Wait for results page to load. Returns True on success."""
        return self.wait_for_element(self.result_locators.SEARCH_RESULTS) is not None
