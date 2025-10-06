"""
Search engine page locators - centralized locator management.
Generic locators that work with DuckDuckGo and other search engines.
"""

from selenium.webdriver.common.by import By


class SearchEngineLocators:
    """All locators for search engine page in one place."""

    # Search elements
    SEARCH_BOX = (By.NAME, "q")  # Main search input box
    SEARCH_BUTTON = (By.XPATH, "//button[@type='submit']")  # Search button
    LUCKY_BUTTON = (
        By.XPATH,
        "//button[@type='submit']",
    )  # I'm Feeling Lucky button

    # Search suggestions
    SUGGESTIONS_CONTAINER = (
        By.CSS_SELECTOR,
        ".search__autocomplete",
    )  # Suggestions container
    SUGGESTION_ITEMS = (
        By.CSS_SELECTOR,
        ".search__autocomplete .acp",
    )  # Individual suggestions
    SUGGESTIONS_LISTBOX = (
        By.CSS_SELECTOR,
        "ul[role='listbox']",
    )  # Suggestions listbox (for waiting)

    # Page elements
    SITE_LOGO = (By.CSS_SELECTOR, ".header__logo-wrap")  # Site logo
    LANGUAGE_SETTINGS = (By.CSS_SELECTOR, ".header__button")  # Settings button

    # Results elements
    RESULTS_CONTAINER = (By.ID, "links")  # Results container
    RESULT_STATS = (By.CSS_SELECTOR, ".js-results-wrapper")  # Results wrapper
    RESULT_TITLES = (By.CSS_SELECTOR, "article h2")  # Result titles

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.CSS_SELECTOR, ".search-wrap")
