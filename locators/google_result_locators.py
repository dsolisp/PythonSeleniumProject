"""
DuckDuckGo search results page locators - centralized locator management.
(Keeping class name GoogleResultLocators for backward compatibility)
"""

from selenium.webdriver.common.by import By


class GoogleResultLocators:
    """All locators for DuckDuckGo search results page in one place."""

    # Results container and lists
    # DuckDuckGo main results container
    RESULTS_CONTAINER = (By.ID, "react-layout")
    # Individual result items
    RESULT_ITEMS = (By.CSS_SELECTOR, "article[data-testid='result']")
    # Result titles (h2 in DuckDuckGo)
    RESULT_TITLES = (By.CSS_SELECTOR, "article h2")
    RESULT_LINKS = (By.CSS_SELECTOR, "article h2 a")  # Result links
    RESULT_DESCRIPTIONS = (
        By.CSS_SELECTOR,
        "article [data-result='snippet']",
    )  # Result descriptions

    # Stats and navigation
    RESULTS_STATS = (By.CSS_SELECTOR, ".js-results-wrapper")  # Results wrapper
    NEXT_PAGE_BUTTON = (
        By.CSS_SELECTOR,
        ".nav-link[aria-label='Next']",
    )  # Next page button
    PREVIOUS_PAGE_BUTTON = (
        By.CSS_SELECTOR,
        ".nav-link[aria-label='Previous']",
    )  # Previous page button

    # Search elements in results page
    SEARCH_BOX_IN_RESULTS = (By.NAME, "q")  # Search box on results page (same)

    # Special result types
    # "Did you mean" suggestions
    DID_YOU_MEAN = (By.CSS_SELECTOR, ".spelling__suggestion")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, ".no-results")  # No results message

    # Alternative result selectors for broader compatibility
    SEARCH_RESULTS = (By.ID, "react-layout")  # Main results container
    # All H2 elements (DuckDuckGo uses h2)
    ALL_H3_ELEMENTS = (By.XPATH, "//h2")
    RESULT_ELEMENTS_DATA_VED = (
        By.CSS_SELECTOR,
        "[data-testid='result']",
    )  # Result articles

    # Dynamic locators with formatting - these need to be tuples for tests to
    # pass
    RESULT_BY_NAME_XPATH = (By.XPATH, "//h2[.='{}']")
    RESULT_BY_INDEX_XPATH = (By.XPATH, "(//h2)[{}]")

    @staticmethod
    def get_result_by_index(index: int):
        """Get result by index position."""
        return (By.XPATH, f"(//h2)[{index}]")

    @staticmethod
    def get_result_by_name(name: str):
        """Get result by exact title match."""
        return (By.XPATH, f"//h2[.='{name}']")

    @staticmethod
    def get_first_result_article():
        """Get the first search result article element."""
        return (By.XPATH, "//article[@data-testid='result']")
