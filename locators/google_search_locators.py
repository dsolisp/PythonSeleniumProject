"""
Google search page locators - centralized locator management.
"""

from selenium.webdriver.common.by import By


class GoogleSearchLocators:
    """All locators for Google search page in one place."""

    # Search elements
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.NAME, "btnK")

    # Results elements
    RESULTS_CONTAINER = (By.ID, "search")
    RESULT_STATS = (By.ID, "result-stats")
    RESULT_TITLES = (By.CSS_SELECTOR, "div.g h3")

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.XPATH, "//textarea[@name='q']/../../../../..")
