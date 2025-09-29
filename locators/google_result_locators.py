"""
Google search results page locators - centralized locator management.
"""

from selenium.webdriver.common.by import By


class GoogleResultLocators:
    """All locators for Google search results page in one place."""

    # Results container and lists
    RESULTS_CONTAINER = (By.ID, "search")
    RESULT_ITEMS = (By.CSS_SELECTOR, ".g .yuRUbf")  # Individual result items
    RESULT_TITLES = (By.CSS_SELECTOR, ".g .yuRUbf h3")  # Result titles
    RESULT_LINKS = (By.CSS_SELECTOR, ".g .yuRUbf a")  # Result links
    RESULT_DESCRIPTIONS = (By.CSS_SELECTOR, ".g .VwiC3b")  # Result descriptions

    # Stats and navigation
    RESULTS_STATS = (By.ID, "result-stats")  # Results statistics
    NEXT_PAGE_BUTTON = (By.ID, "pnnext")  # Next page button
    PREVIOUS_PAGE_BUTTON = (By.ID, "pnprev")  # Previous page button
    
    # Search elements in results page
    SEARCH_BOX_IN_RESULTS = (By.NAME, "q")  # Search box on results page
    
    # Special result types
    DID_YOU_MEAN = (By.CSS_SELECTOR, ".gqLQtd a")  # "Did you mean" suggestions
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, "#topstuff .med")  # No results message
    
    # Alternative result selectors for broader compatibility
    SEARCH_RESULTS = (By.ID, "search")  # Main results container
    ALL_H3_ELEMENTS = (By.XPATH, "//h3")  # All H3 elements (common result titles)
    RESULT_ELEMENTS_DATA_VED = (By.CSS_SELECTOR, "[data-ved]")  # Elements with data-ved attribute

    # Dynamic locators with formatting - these need to be tuples for tests to pass
    RESULT_BY_NAME_XPATH = (By.XPATH, "//h3[.='{}']")
    RESULT_BY_INDEX_XPATH = (By.XPATH, "(//h3)[{}]")

    @staticmethod
    def get_result_by_index(index: int):
        """Get result by index position."""
        return (By.XPATH, f"(//h3)[{index}]")

    @staticmethod
    def get_result_by_name(name: str):
        """Get result by exact title match."""
        return (By.XPATH, f"//h3[.='{name}']")
