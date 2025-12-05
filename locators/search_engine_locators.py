"""
Search engine page locators - centralized locator management.
Generic locators that work with Bing and other search engines.
"""

from selenium.webdriver.common.by import By

from locators.bing_common_locators import BingCommonLocators


class SearchEngineLocators(BingCommonLocators):
    """All locators for Bing search engine page in one place."""

    # Search elements (SEARCH_BOX inherited from BingCommonLocators)
    SEARCH_BUTTON = (By.ID, "search_icon")
    SEARCH_BUTTON_ALT = (By.CSS_SELECTOR, "label[for='sb_form_go']")

    # Search suggestions
    SUGGESTIONS_CONTAINER = (By.CSS_SELECTOR, "#sa_ul, .sa_sg")
    SUGGESTION_ITEMS = (By.CSS_SELECTOR, "#sa_ul li, .sa_sg li")
    SUGGESTIONS_LISTBOX = (By.CSS_SELECTOR, "#sa_ul")

    # Page elements
    SITE_LOGO = (By.ID, "bLogo")
    LANGUAGE_SETTINGS = (By.CSS_SELECTOR, "#id_sc")

    # Aliases for compatibility (inherited: RESULTS_CONTAINER, RESULT_ITEMS, RESULT_TITLES)
    RESULT_STATS = BingCommonLocators.RESULTS_STATS

    # Screenshot locator for full search area
    MAIN_SEARCH_INPUT_SCREENSHOT = (By.CSS_SELECTOR, "#sb_form")
