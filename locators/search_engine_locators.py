"""
Search engine page locators - centralized locator management.
Generic locators that work with Bing and other search engines.
"""

from selenium.webdriver.common.by import By


class SearchEngineLocators:
    """All locators for Bing search engine page in one place."""

    # Search elements
    SEARCH_BOX = (By.NAME, "q")  # Main search input box (Bing uses 'q')
    SEARCH_BUTTON = (By.ID, "search_icon")  # Bing search button
    SEARCH_BUTTON_ALT = (
        By.CSS_SELECTOR,
        "label[for='sb_form_go']",
    )  # Alt search button

    # Search suggestions
    SUGGESTIONS_CONTAINER = (
        By.CSS_SELECTOR,
        "#sa_ul, .sa_sg",
    )  # Bing suggestions container
    SUGGESTION_ITEMS = (
        By.CSS_SELECTOR,
        "#sa_ul li, .sa_sg li",
    )  # Individual suggestions
    SUGGESTIONS_LISTBOX = (
        By.CSS_SELECTOR,
        "#sa_ul",
    )  # Suggestions listbox (for waiting)

    # Page elements
    SITE_LOGO = (By.ID, "bLogo")  # Bing logo
    LANGUAGE_SETTINGS = (By.CSS_SELECTOR, "#id_sc")  # Settings button

    # Results elements
    RESULTS_CONTAINER = (By.ID, "b_results")  # Bing results container
    RESULT_STATS = (By.CSS_SELECTOR, ".sb_count")  # Results count text
    RESULT_TITLES = (By.CSS_SELECTOR, "#b_results h2")  # Result titles
    RESULT_ITEMS = (By.CSS_SELECTOR, "#b_results .b_algo")  # Individual result items

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.CSS_SELECTOR, "#sb_form")
