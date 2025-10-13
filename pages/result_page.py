from typing import Optional

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from locators.result_page_locators import ResultPageLocators
from pages.base_page import BasePage


class ResultPage(BasePage):
    def __init__(
        self,
        driver_and_db,
        test_name: Optional[str] = None,
        environment: str = "test",
    ):
        """Initialize search engine result page with enhanced features."""
        super().__init__(driver_and_db, test_name=test_name, environment=environment)
        self.result_locators = ResultPageLocators()

    # Locators

    def get_result_by_name(self, name):
        return self.driver.find_element(*self.result_locators.get_result_by_name(name))

    def get_result_by_index(self, index):
        return self.driver.find_element(
            *self.result_locators.get_result_by_index(index),
        )

    def get_search_results(self):
        """Get all search result elements."""
        return self.driver.find_elements(*self.result_locators.RESULT_ITEMS)

    def get_first_result(self):
        """Get the first search result article element."""
        return self.driver.find_element(
            *self.result_locators.get_first_result_article(),
        )

    def is_results_displayed(self) -> bool:
        """Check if search results are displayed."""
        try:
            # Look for common result indicators using locators
            return (
                self.is_element_visible(self.result_locators.SEARCH_RESULTS)
                or len(self.driver.find_elements(*self.result_locators.ALL_H3_ELEMENTS))
                > 0
                or len(
                    self.driver.find_elements(
                        *self.result_locators.RESULT_ELEMENTS_DATA_VED,
                    ),
                )
                > 0
            )
        except (NoSuchElementException, WebDriverException):
            return False

    def get_results_count(self) -> int:
        """Get the number of search results found."""
        try:
            # Try multiple strategies to count results using locators
            h3_elements = self.driver.find_elements(
                *self.result_locators.ALL_H3_ELEMENTS,
            )
            if h3_elements:
                return len(h3_elements)

            # Fallback to other result indicators
            result_elements = self.driver.find_elements(
                *self.result_locators.RESULT_ELEMENTS_DATA_VED,
            )
            return len(result_elements)
        except (NoSuchElementException, WebDriverException):
            return 0

    def wait_for_results_page(self, timeout: int = 10) -> bool:
        """Wait for results page to load."""
        try:
            return (
                self.wait_for_element(
                    self.result_locators.SEARCH_RESULTS,
                    timeout=timeout,
                )
                is not None
            )
        except TimeoutException:
            return False

    def wait_for_results_page_complete(self, timeout: int = 15) -> bool:
        """Wait for results page to fully load with extended timeout."""
        try:
            return (
                self.wait_for_element(
                    self.result_locators.SEARCH_RESULTS,
                    timeout=timeout,
                )
                is not None
            )
        except TimeoutException:
            return False
