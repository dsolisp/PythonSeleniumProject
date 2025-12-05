"""
Search engine results page locators - centralized locator management.
Generic locators that work with Bing search engine.
"""

from selenium.webdriver.common.by import By

from locators.bing_common_locators import BingCommonLocators


class ResultPageLocators(BingCommonLocators):
    """All locators for Bing search engine results page in one place."""

    # Additional result elements (RESULTS_CONTAINER, RESULT_ITEMS, RESULT_TITLES inherited)
    RESULT_LINKS = (By.CSS_SELECTOR, "#b_results h2 a")
    RESULT_DESCRIPTIONS = (By.CSS_SELECTOR, "#b_results .b_caption p")

    # Navigation
    NEXT_PAGE_BUTTON = (By.CSS_SELECTOR, "a.sb_pagN")
    PREVIOUS_PAGE_BUTTON = (By.CSS_SELECTOR, "a.sb_pagP")

    # Search elements in results page (alias for inherited SEARCH_BOX)
    SEARCH_BOX_IN_RESULTS = BingCommonLocators.SEARCH_BOX

    # Special result types
    DID_YOU_MEAN = (By.CSS_SELECTOR, ".sp_spellLink, .b_spell")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, ".b_no")

    # Backward compatibility aliases
    SEARCH_RESULTS = BingCommonLocators.RESULTS_CONTAINER
    ALL_H3_ELEMENTS = (By.XPATH, "//h2")
    RESULT_ELEMENTS_DATA_VED = BingCommonLocators.RESULT_ITEMS

    # Dynamic locators
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
        """Get the first Bing search result element."""
        return (By.CSS_SELECTOR, "#b_results .b_algo")
