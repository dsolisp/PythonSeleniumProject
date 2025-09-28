"""
Google search results page locators - centralized locator management.
"""

from selenium.webdriver.common.by import By


class GoogleResultLocators:
    """All locators for Google search results page in one place."""

    # Results container and lists
    RESULTS_CONTAINER = (By.ID, "search")
    RESULT_TITLES = (By.CSS_SELECTOR, "div.g h3")
    RESULT_LINKS = (By.CSS_SELECTOR, "div.g a")
    RESULT_DESCRIPTIONS = (By.CSS_SELECTOR, "div.g .VwiC3b")

    # Stats and navigation
    RESULT_STATS = (By.ID, "result-stats")
    NEXT_PAGE = (By.ID, "pnnext")
    PREVIOUS_PAGE = (By.ID, "pnprev")

    # Dynamic locators with formatting
    RESULT_BY_NAME_XPATH = "//h3[.='{}']"
    RESULT_BY_INDEX_XPATH = "(//h3)[{}]"

    @staticmethod
    def get_result_by_index(index: int):
        """Get result by index position."""
        return (By.XPATH, GoogleResultLocators.RESULT_BY_INDEX_XPATH.format(index))

    @staticmethod
    def get_result_by_name(name: str):
        """Get result by exact title match."""
        return (By.XPATH, GoogleResultLocators.RESULT_BY_NAME_XPATH.format(name))
