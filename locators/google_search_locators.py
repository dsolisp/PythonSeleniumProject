"""
Google search page locators - centralized locator management.
"""

from selenium.webdriver.common.by import By


class GoogleSearchLocators:
    """All locators for Google search page in one place."""

    # Search elements
    SEARCH_BOX = (By.NAME, "q")  # Main search input box
    SEARCH_BUTTON = (By.NAME, "btnK")
    LUCKY_BUTTON = (By.NAME, "btnI")  # I'm Feeling Lucky button
    
    # Search suggestions
    SUGGESTIONS_CONTAINER = (By.CSS_SELECTOR, ".aajZCb")  # Suggestions dropdown container
    SUGGESTION_ITEMS = (By.CSS_SELECTOR, ".aajZCb li")  # Individual suggestion items
    
    # Page elements
    GOOGLE_LOGO = (By.CSS_SELECTOR, "#hplogo")  # Google logo
    LANGUAGE_SETTINGS = (By.ID, "SIvCob")  # Language settings link

    # Results elements (for compatibility)
    RESULTS_CONTAINER = (By.ID, "search")
    RESULT_STATS = (By.ID, "result-stats")
    RESULT_TITLES = (By.CSS_SELECTOR, "div.g h3")

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.XPATH, "//textarea[@name='q']/../../../../..")
