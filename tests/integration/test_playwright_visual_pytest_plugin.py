"""
Playwright Visual Regression Test using pytest-playwright-visual (2025)
This is a minimal, maintainable example using the recommended plugin for Python.
"""

import time

import pytest
from hamcrest import assert_that, is_, not_none

from pages.playwright_search_engine_page import PlaywrightSearchEnginePage


@pytest.mark.visual
@pytest.mark.playwright
@pytest.mark.parametrize("search_term", ["Python"])
def test_search_page_visual_regression(assert_snapshot, page, search_term):
    """
    Visual regression test using the project's PlaywrightSearchEnginePage (sync API),
    matching project conventions. Focus on search results rather than dynamic homepage.
    """
    search_page = PlaywrightSearchEnginePage(page)
    assert_that(search_page.open_search_engine(), is_(True))

    # Test search functionality
    search_result = search_page.search_for(search_term)
    assert_that(search_result, is_(True))

    # Check if we're on a results page
    current_url = search_page.get_url()
    assert_that(
        any(indicator in current_url.lower() for indicator in ["q=", "search"]),
        is_(True),
    )

    # Ensure search results page is fully loaded before taking screenshot
    search_page.wait_for_search_completion()
    time.sleep(2)  # Increased wait for dynamic content to settle

    # Take screenshot of the search input element using page object method
    input_screenshot = search_page.take_element_screenshot(
        search_page.locators.SEARCH_INPUT,
    )
    assert_that(input_screenshot, is_(not_none))
    assert_snapshot(
        input_screenshot,
        name=f"search_input_after_{search_term}.png",
        threshold=0.2,
    )



@pytest.mark.visual
@pytest.mark.playwright
def test_search_input_visual_regression(assert_snapshot, page):
    """
    Visual regression for the search input element using the page object,
    matching project conventions.
    """
    search_page = PlaywrightSearchEnginePage(page)
    assert_that(search_page.open_search_engine(), is_(True))

    # Ensure page is fully loaded before taking element screenshot
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(1)  # Increased wait for dynamic content to settle

    # Take screenshot of the search input element using page object method
    input_screenshot = search_page.take_element_screenshot(
        search_page.locators.SEARCH_INPUT,
    )
    assert_that(input_screenshot, is_(not_none))
    assert_snapshot(
        input_screenshot,
        name="search_input.png",
        threshold=0.2,
    )
