"""
Search engine results page locators - centralized locator management.
Generic locators that work with Bing search engine.
"""

from selenium.webdriver.common.by import By


class ResultPageLocators:
    """All locators for Bing search engine results page in one place."""

    # Results container and lists
    RESULTS_CONTAINER = (By.ID, "b_results")  # Bing main results container
    RESULT_ITEMS = (By.CSS_SELECTOR, "#b_results .b_algo")  # Bing result items
    RESULT_TITLES = (By.CSS_SELECTOR, "#b_results h2")  # Result titles
    RESULT_LINKS = (By.CSS_SELECTOR, "#b_results h2 a")  # Result links
    RESULT_DESCRIPTIONS = (
        By.CSS_SELECTOR,
        "#b_results .b_caption p",
    )  # Result descriptions/snippets

    # Stats and navigation
    RESULTS_STATS = (By.CSS_SELECTOR, ".sb_count")  # Bing results count
    NEXT_PAGE_BUTTON = (
        By.CSS_SELECTOR,
        "a.sb_pagN",
    )  # Bing next page button
    PREVIOUS_PAGE_BUTTON = (
        By.CSS_SELECTOR,
        "a.sb_pagP",
    )  # Bing previous page button

    # Search elements in results page
    SEARCH_BOX_IN_RESULTS = (By.NAME, "q")  # Search box on results page

    # Special result types
    # "Did you mean" suggestions
    DID_YOU_MEAN = (By.CSS_SELECTOR, ".sp_spellLink, .b_spell")
    NO_RESULTS_MESSAGE = (By.CSS_SELECTOR, ".b_no")  # No results message

    # Alternative result selectors for broader compatibility
    # SEARCH_RESULTS is an alias for RESULTS_CONTAINER for backward compatibility
    SEARCH_RESULTS = RESULTS_CONTAINER
    ALL_H3_ELEMENTS = (By.XPATH, "//h2")  # All H2 heading elements
    RESULT_ELEMENTS_DATA_VED = (
        By.CSS_SELECTOR,
        "#b_results .b_algo",
    )  # Bing result items

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
        """Get the first Bing search result element."""
        return (By.CSS_SELECTOR, "#b_results .b_algo")
