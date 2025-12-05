"""
Common Bing locators shared between search and results pages.
Eliminates duplication between search_engine_locators.py and result_page_locators.py.
"""

from selenium.webdriver.common.by import By


class BingCommonLocators:
    """Shared locators for Bing search engine - used by both search and results pages."""

    # Results container and items
    RESULTS_CONTAINER = (By.ID, "b_results")
    RESULT_ITEMS = (By.CSS_SELECTOR, "#b_results .b_algo")
    RESULT_TITLES = (By.CSS_SELECTOR, "#b_results h2")

    # Search elements
    SEARCH_BOX = (By.NAME, "q")

    # Results stats
    RESULTS_STATS = (By.CSS_SELECTOR, ".sb_count")
