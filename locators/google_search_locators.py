"""
DuckDuckGo search page locators - centralized locator management.
(Keeping class name GoogleSearchLocators for backward compatibility)
"""

from selenium.webdriver.common.by import By


class GoogleSearchLocators:
    """All locators for DuckDuckGo search page in one place."""

    # Search elements
    SEARCH_BOX = (By.NAME, "q")  # Main search input box (same as Google)
    # DuckDuckGo search button
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")
    # Same as search button
    LUCKY_BUTTON = (By.XPATH, "//button[@type='submit']")

    # Search suggestions
    SUGGESTIONS_CONTAINER = (
        By.CSS_SELECTOR,
        ".search__autocomplete",
    )  # DuckDuckGo suggestions
    SUGGESTION_ITEMS = (
        By.CSS_SELECTOR,
        ".search__autocomplete .acp",
    )  # Individual suggestions

    # Page elements
    GOOGLE_LOGO = (By.CSS_SELECTOR, ".header__logo-wrap")  # DuckDuckGo logo
    LANGUAGE_SETTINGS = (By.CSS_SELECTOR, ".header__button")  # Settings button

    # Results elements
    RESULTS_CONTAINER = (By.ID, "links")  # DuckDuckGo results container
    RESULT_STATS = (By.CSS_SELECTOR, ".js-results-wrapper")  # Results wrapper
    RESULT_TITLES = (By.CSS_SELECTOR, "article h2")  # DuckDuckGo result titles

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.CSS_SELECTOR, ".search-wrap")
