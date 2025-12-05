"""
Framework Core Tests - Essential health checks and structure validation.

This file consolidates test_smoke.py and test_core_functionality.py into a single
file that tests framework health, dependencies, locators, and page object structure.
Duplicate tests have been eliminated - each concept is tested once.
"""

import sqlite3
from unittest.mock import Mock

import pytest
from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    has_property,
    instance_of,
    is_,
    is_in,
    not_none,
)
from selenium.webdriver.common.by import By

from config.settings import Settings
from locators.result_page_locators import ResultPageLocators
from locators.search_engine_locators import SearchEngineLocators
from pages.base_page import BasePage
from pages.result_page import ResultPage
from pages.search_engine_page import SearchEnginePage


class TestFrameworkHealth:
    """Quick health checks to verify framework is operational."""

    def test_core_imports_work(self):
        """Verify all core framework components can be imported."""
        # If we reach this point, all imports at module level worked
        assert_that(True, is_(True))  # noqa: FBT003

    def test_settings_provide_expected_values(self):
        """Verify settings provide sensible default values."""
        settings = Settings()

        # Should have basic required settings
        assert_that(settings, has_property("BROWSER"))
        assert_that(settings, has_property("BASE_URL"))
        assert_that(settings, has_property("TIMEOUT"))

        # Values should be reasonable
        assert_that(settings.BROWSER, is_in(["chrome", "firefox", "edge", "safari"]))
        assert_that(settings.BASE_URL.lower(), contains_string("http"))
        assert_that(settings.TIMEOUT, instance_of(int))
        assert_that(settings.TIMEOUT, greater_than(0))


class TestDependencies:
    """Verify required dependencies are available and functional."""

    def test_selenium_available(self):
        """Verify Selenium WebDriver is properly installed."""
        # Import succeeded at module level - just confirm By is usable
        assert_that(By.ID, equal_to("id"))
        assert_that(By.CSS_SELECTOR, equal_to("css selector"))

    def test_sqlite_available(self):
        """Verify SQLite support is available and functional."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        assert_that(result[0], equal_to(1))

    def test_image_processing_available(self):
        """Verify image processing dependencies (numpy) are available."""
        try:
            import numpy as np  # noqa: PLC0415

            assert_that(np.array([1, 2, 3]).sum(), equal_to(6))
        except ImportError:
            pytest.skip("numpy not available - image processing features limited")


class TestLocatorsStructure:
    """Verify locators are properly defined with correct structure."""

    def test_search_engine_locators(self):
        """Verify search engine locators have correct tuple structure."""
        # Test key locators exist
        assert_that(SearchEngineLocators, has_property("SEARCH_BOX"))
        assert_that(SearchEngineLocators, has_property("SEARCH_BUTTON"))

        # Verify tuple structure: (By.METHOD, "selector")
        search_box = SearchEngineLocators.SEARCH_BOX
        assert_that(search_box, instance_of(tuple))
        assert_that(len(search_box), equal_to(2))
        assert_that(
            search_box[0],
            is_in(
                [By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME, By.XPATH, By.CSS_SELECTOR]
            ),
        )
        assert_that(search_box[1], instance_of(str))
        assert_that(len(search_box[1]), greater_than(0))

    def test_result_page_locators(self):
        """Verify result page locators have correct structure."""
        assert_that(ResultPageLocators, has_property("RESULTS_CONTAINER"))
        assert_that(ResultPageLocators.RESULTS_CONTAINER, instance_of(tuple))
        assert_that(len(ResultPageLocators.RESULTS_CONTAINER), equal_to(2))


class TestPageObjectStructure:
    """Verify page objects follow correct patterns and inheritance."""

    def test_base_page_initialization(self):
        """Verify BasePage can be initialized with driver."""
        mock_driver = Mock()
        mock_driver.get = Mock()

        page = BasePage(mock_driver)
        assert_that(page.driver, equal_to(mock_driver))

    def test_page_object_inheritance(self):
        """Verify page objects inherit from BasePage correctly."""
        assert_that(issubclass(SearchEnginePage, BasePage), is_(True))
        assert_that(issubclass(ResultPage, BasePage), is_(True))

    def test_page_object_initialization(self):
        """Verify page objects can be initialized with mock driver."""
        mock_driver = Mock()
        mock_driver.get = Mock()

        search_page = SearchEnginePage(mock_driver)
        result_page = ResultPage(mock_driver)

        assert_that(search_page, is_(not_none()))
        assert_that(result_page, is_(not_none()))
        assert_that(search_page, has_property("driver"))
        assert_that(result_page, has_property("driver"))
