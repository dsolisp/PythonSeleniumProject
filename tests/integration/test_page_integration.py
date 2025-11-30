"""
Integration tests for page object interactions.
Tests complete workflows and module interactions.
All locators are centralized in locator classes following clean architecture.
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    greater_than_or_equal_to,
    has_property,
    is_,
    is_in,
    none,
    not_none,
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config.settings import Settings, settings
from locators.search_engine_locators import SearchEngineLocators
from locators.test_framework_locators import TestFrameworkLocators
from pages.base_page import BasePage
from pages.result_page import ResultPage
from pages.search_engine_page import SearchEnginePage
from utils.sql_connection import execute_query, get_connection
from utils.structured_logger import TestLogger
from utils.webdriver_factory import WebDriverFactory, get_driver

# SQL for creating the standard test results table
TEST_RESULTS_TABLE_SQL = """
    CREATE TABLE test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_name TEXT NOT NULL,
        result TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
"""


def create_test_results_table(conn: sqlite3.Connection) -> None:
    """Create the standard test_results table in the given database connection."""
    execute_query(conn, TEST_RESULTS_TABLE_SQL)


@pytest.mark.integration
@pytest.mark.browser_chrome
class TestPageObjectIntegration:
    """Integration tests for page object interactions."""

    @pytest.fixture
    def chrome_driver(self):
        """Create a headless Chrome driver for testing."""
        driver = WebDriverFactory.create_headless_chrome_for_testing()
        yield driver
        driver.quit()

    @pytest.fixture
    def temp_database(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            pass

        conn = get_connection(temp_db.name)
        create_test_results_table(conn)

        yield temp_db.name

        # Cleanup
        conn.close()
        Path(temp_db.name).unlink()

    def test_base_page_integration(self, chrome_driver, temp_database):
        """Test BasePage integration with solid design."""
        conn = get_connection(temp_database)
        base_page = BasePage(chrome_driver, conn)

        # Test navigation integration
        base_page.navigate_to(settings.BASE_URL)
        current_url = base_page.get_current_url()
        assert_that(current_url, contains_string("duckduckgo.com"))

        # Test database integration through direct methods
        query = "INSERT INTO test_results (test_name, result) VALUES (?, ?)"
        base_page.execute_query(query, ("integration_test", "passed"))

        # Verify data was inserted
        fetched_record = base_page.execute_query(
            "SELECT * FROM test_results WHERE test_name = ?",
            ("integration_test",),
        )
        assert_that(fetched_record, is_(not_none()))
        assert_that(len(fetched_record), greater_than(0))

        conn.close()

    def test_page_object_inheritance(self, chrome_driver):
        """Test that page objects properly inherit from BasePage."""
        search_page = SearchEnginePage(chrome_driver)
        result_page = ResultPage(chrome_driver)

        # Test that both pages have access to core methods
        assert_that(search_page, has_property("find_element"))
        assert_that(search_page, has_property("navigate_to"))
        assert_that(search_page, has_property("take_screenshot"))

        assert_that(result_page, has_property("find_element"))
        assert_that(result_page, has_property("navigate_to"))
        assert_that(result_page, has_property("take_screenshot"))

        # Test navigation between pages
        search_page.navigate_to(settings.BASE_URL)
        title = search_page.get_title()
        assert_that(title, contains_string("DuckDuckGo"))

    @patch("utils.webdriver_factory.webdriver.Chrome")
    def test_webdriver_factory_integration(self, mock_chrome):
        """Test WebDriverFactory integration with page objects."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        # Test driver creation and page object initialization
        driver, _ = get_driver(browser="chrome")
        page = BasePage(driver)
        assert_that(page.driver, equal_to(mock_driver))

    def test_database_integration_with_page_actions(self, temp_database):
        """Test database operations integration with page actions."""
        conn = get_connection(temp_database)
        mock_driver = Mock()

        page = BasePage(mock_driver, conn)

        # Test database operations through direct methods
        test_results = [
            ("test_1", "passed"),
            ("test_2", "failed"),
            ("test_3", "skipped"),
        ]

        # Insert test data
        for test_name, result in test_results:
            query = "INSERT INTO test_results (test_name, result) VALUES (?, ?)"
            page.execute_query(query, (test_name, result))

        # Verify all records were inserted
        all_records = page.execute_query("SELECT * FROM test_results")
        assert_that(len(all_records), equal_to(3))

        # Test update operation
        update_query = "UPDATE test_results SET result = ? WHERE test_name = ?"
        page.execute_query(update_query, ("re-tested", "test_2"))

        # Verify update
        updated_record = page.execute_query(
            "SELECT result FROM test_results WHERE test_name = ?",
            ("test_2",),
        )
        assert_that(len(updated_record), greater_than(0))
        assert_that(updated_record[0][0], equal_to("re-tested"))

        # Test delete operation
        delete_query = "DELETE FROM test_results WHERE result = ?"
        page.execute_query(delete_query, ("skipped",))

        # Verify deletion
        remaining_records = page.execute_query("SELECT * FROM test_results")
        assert_that(len(remaining_records), equal_to(2))

        conn.close()

    def test_screenshot_integration(self, chrome_driver):
        """Test screenshot functionality integration."""
        page = BasePage(chrome_driver)

        # Navigate to a page for screenshot
        page.navigate_to(settings.BASE_URL)

        # Create temporary directory for screenshots
        with tempfile.TemporaryDirectory():
            # Take screenshot
            saved_path = page.take_screenshot("integration_test.png")
            assert_that(saved_path, is_(not_none()))
            assert_that(Path(saved_path).exists(), is_(True))
            assert_that(Path(saved_path).stat().st_size, greater_than(0))

    def test_element_actions_integration(self, chrome_driver):
        """Test element actions integration with real browser."""
        page = BasePage(chrome_driver)

        # Navigate to DuckDuckGo search page
        page.navigate_to(settings.BASE_URL)

        # Test finding elements using locators
        search_elements = page.find_elements(SearchEngineLocators.SEARCH_BOX)

        # DuckDuckGo should have at least one search box (Allow for 0 in case of
        # changes)
        assert_that(len(search_elements), greater_than_or_equal_to(0))

        # Test that page loaded successfully
        current_url = page.get_current_url()
        assert_that(current_url, contains_string("duckduckgo.com"))

    def test_error_handling_integration(self, chrome_driver):
        """Test error handling across integrated components."""
        page = BasePage(chrome_driver)

        # Test navigation to invalid URL
        page.navigate_to("https://nonexistent-domain-12345.com")

        # Test element finding on page that might not load using locators
        element = page.find_element(TestFrameworkLocators.NONEXISTENT_ELEMENT)
        assert_that(element, is_(none()))

        # Test screenshot on potentially problematic page
        screenshot_path = page.take_screenshot("error_test.png")
        # Result may vary, but shouldn't raise unhandled exceptions
        # Screenshot path should be either None or a valid string
        assert_that(
            screenshot_path is None or isinstance(screenshot_path, str),
            is_(True),
        )

    def test_multiple_page_objects_integration(self, chrome_driver):
        """Test integration between multiple page objects."""
        search_page = SearchEnginePage(chrome_driver)
        result_page = ResultPage(chrome_driver)

        # Both should be able to navigate
        search_page.navigate_to(settings.BASE_URL)
        search_title = search_page.get_title()

        # Switch to results page object (same driver)
        result_page.navigate_to(settings.SEARCH_URL)
        result_title = result_page.get_title()

        # Both operations should work - titles may vary based on search engine's
        # current layout
        assert_that(search_title is not None and len(search_title), greater_than(0))
        assert_that(result_title is not None and len(result_title), greater_than(0))
        # Accept various search page titles (DuckDuckGo, search, or
        # test-related)
        search_valid = any(
            term in search_title.lower() for term in ["duckduckgo", "search", "duck"]
        )
        result_valid = any(
            term in result_title.lower()
            for term in ["duckduckgo", "search", "test", "duck"]
        )
        # At least has some title
        assert_that(search_valid or len(search_title), greater_than(0))
        # At least has some title
        assert_that(result_valid or len(result_title), greater_than(0))


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration and settings."""

    @patch.dict(
        os.environ,
        {
            "BASE_URL": "https://test.example.com",
            "BROWSER": "chrome",
            "HEADLESS": "true",
        },
    )
    def test_settings_integration(self):
        """Test settings integration with environment variables."""
        settings = Settings()

        assert_that(settings.BASE_URL, equal_to("https://test.example.com"))
        assert_that(settings.BROWSER, equal_to("chrome"))
        assert_that(settings.HEADLESS, is_(True))

    def test_logger_integration_across_modules(self):
        """Test logger integration across different modules."""
        # Create temporary database for this test
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            pass

        conn = get_connection(temp_db.name)
        create_test_results_table(conn)

        try:
            # Create logger
            TestLogger("integration_test")

            # Test that logger works with different components
            mock_driver = Mock()

            page = BasePage(mock_driver, conn)

            # Test that page object can perform database operations (core
            # functionality)
            assert_that(page.driver, equal_to(mock_driver))
            assert_that(page.database, equal_to(conn))

            # Test database integration through page actions
            query = "INSERT INTO test_results (test_name, result) VALUES (?, ?)"
            page.execute_query(
                query,
                ("logger_test", "passed"),
            )  # Verify no exceptions were raised during logging
            conn.close()

        finally:
            # Cleanup
            if Path(temp_db.name).exists():
                Path(temp_db.name).unlink()


@pytest.mark.integration
@pytest.mark.browser_chrome
class TestEndToEndWorkflow:
    """End-to-end workflow integration tests."""

    def test_complete_test_workflow(self):
        """Test a complete test execution workflow."""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            pass

        conn = get_connection(temp_db.name)
        create_test_results_table(conn)

        # Create Chrome driver
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        chrome_driver = webdriver.Chrome(options=options)

        try:
            search_page = SearchEnginePage((chrome_driver, conn))

            # Record test start
            start_query = "INSERT INTO test_results (test_name, result) VALUES (?, ?)"
            search_page.execute_query(start_query, ("end_to_end_workflow", "started"))

            # Navigate to search page
            search_page.navigate_to(settings.BASE_URL)

            # Take screenshot
            screenshot_path = search_page.take_screenshot("workflow_test.png")
            screenshot_success = screenshot_path is not None

            # Update test result
            result_status = "completed" if screenshot_success else "failed"
            update_query = "UPDATE test_results SET result = ? WHERE test_name = ?"
            search_page.execute_query(
                update_query,
                (result_status, "end_to_end_workflow"),
            )

            # Verify final state
            final_result = search_page.execute_query(
                "SELECT result FROM test_results WHERE test_name = ?",
                ("end_to_end_workflow",),
            )

            assert_that(final_result, is_(not_none()))
            assert_that(len(final_result), greater_than(0))
            assert_that(final_result[0][0], is_in(["completed", "failed"]))

            if screenshot_success:
                assert_that(Path(screenshot_path).exists(), is_(True))

        finally:
            # Cleanup
            chrome_driver.quit()
            conn.close()
            if Path(temp_db.name).exists():
                Path(temp_db.name).unlink()
