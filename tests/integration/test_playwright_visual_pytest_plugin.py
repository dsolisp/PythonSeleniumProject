"""
Playwright Visual Regression Test using pytest-playwright-visual (2025)
This is a minimal, maintainable example using the recommended plugin for Python.
"""

import pytest
import pytest_playwright_visual

@pytest.mark.visual
@pytest.mark.playwright
@pytest.mark.parametrize("search_term", ["Python", "Playwright"])
def test_search_page_visual_regression(page, assert_snapshot, search_term):
    page.goto("https://duckduckgo.com")
    assert_snapshot(page.screenshot(), name="search_homepage.png")

    page.fill("#searchbox_input", search_term)
    page.press("#searchbox_input", "Enter")
    page.wait_for_selector("#links")
    assert_snapshot(page.screenshot(), name=f"search_results_{search_term}.png")

@pytest.mark.visual
@pytest.mark.playwright
def test_search_input_visual_regression(page, assert_snapshot):
    page.goto("https://duckduckgo.com")
    input_el = page.query_selector("#searchbox_input")
    assert input_el, "Search input not found"
    assert_snapshot(input_el.screenshot(), name="search_input.png")
