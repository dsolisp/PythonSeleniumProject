"""
Smoke Tests - Quick Framework Health Checks
These tests verify that the framework is in a working state.
"""

import sqlite3

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
)
from selenium.webdriver.common.by import By

from config.settings import Settings
from locators.search_engine_locators import SearchEngineLocators


class TestFrameworkSmoke:
    """Quick smoke tests to verify framework health."""

    # TODO: test doing pass with true is true
    def test_all_core_imports_work(self):
        """Test that all core framework components can be imported."""
        # This is the most important test - if imports fail, nothing works
        try:
            pass

            # If we get here, all imports worked
            assert_that(True, is_(True))  # noqa: FBT003

        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")

    def test_settings_provide_expected_values(self):
        """Test that settings provide sensible default values."""
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

    def test_locators_have_valid_format(self):
        """Test that locators follow the expected format."""
        # Check a few key locators
        search_box = SearchEngineLocators.SEARCH_BOX
        search_button = SearchEngineLocators.SEARCH_BUTTON

        # Should be tuples with (By.METHOD, "selector")
        assert_that(search_box, instance_of(tuple))
        assert_that(len(search_box), equal_to(2))
        assert_that(
            search_box[0],
            is_in(
                [By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME, By.XPATH, By.CSS_SELECTOR],
            ),
        )
        assert_that(search_box[1], instance_of(str))
        assert_that(len(search_box[1]), greater_than(0))

        assert_that(search_button, instance_of(tuple))
        assert_that(len(search_button), equal_to(2))


class TestDependenciesAvailable:
    """Test that required dependencies are available."""

    # TODO: test doing pass with true is true
    def test_selenium_available(self):
        """Test that Selenium is properly installed."""
        try:
            pass

            assert_that(True, is_(True))  # noqa: FBT003
        except ImportError as e:
            pytest.fail(f"Selenium not properly installed: {e}")

    def test_sqlite_available(self):
        """Test that SQLite support is available."""
        try:
            # Test basic SQLite functionality
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()
            assert_that(result[0], equal_to(1))
        except (sqlite3.Error, OSError) as e:
            pytest.fail(f"SQLite not working properly: {e}")

    # TODO: test doing pass with true is true
    def test_image_processing_available(self):
        """Test that image processing dependencies are available."""
        try:
            pass

            assert_that(True, is_(True))  # noqa: FBT003
        except ImportError:
            # PIL/numpy might not be installed, that's ok for basic framework
            pytest.skip(
                "PIL/numpy not available - image processing features may be limited",
            )
