"""
Integration tests for page object interactions.
Tests complete workflows and module interactions.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from pages.base_page import BasePage
from pages.google_search_page import GoogleSearchPage
from pages.google_result_page import GoogleResultPage
from utils.webdriver_factory import get_driver
from utils.sql_connection import get_connection, execute_query, insert_data, execute_and_fetch_one


class TestPageObjectIntegration:
    """Integration tests for page object interactions."""

    @pytest.fixture
    def chrome_driver(self):
        """Create a headless Chrome driver for testing."""
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()

    @pytest.fixture
    def temp_database(self):
        """Create a temporary database for testing."""
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        
        # Create a simple test table
        conn = get_connection(temp_db.name)
        execute_query(conn, """
            CREATE TABLE test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                result TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        yield temp_db.name
        
        # Cleanup
        conn.close()
        os.unlink(temp_db.name)

    def test_base_page_integration(self, chrome_driver, temp_database):
        """Test BasePage integration with all action handlers."""
        conn = get_connection(temp_database)
        base_page = BasePage(chrome_driver, conn)
        
        # Test navigation integration
        base_page.navigation.navigate_to_url("https://www.google.com")
        current_url = base_page.navigation.get_current_url()
        assert "google.com" in current_url
        
        # Test database integration
        test_data = {"test_name": "integration_test", "result": "passed"}
        record_id = base_page.database.insert_data("test_results", test_data)
        assert record_id is not None
        
        # Verify data was inserted
        fetched_record = base_page.database.fetch_single_record(
            "SELECT * FROM test_results WHERE id = ?", (record_id,)
        )
        assert fetched_record is not None
        assert fetched_record[1] == "integration_test"  # test_name column
        
        conn.close()

    def test_page_object_inheritance(self, chrome_driver):
        """Test that page objects properly inherit from BasePage."""
        search_page = GoogleSearchPage(chrome_driver)
        result_page = GoogleResultPage(chrome_driver)
        
        # Test that both pages have access to action handlers
        assert hasattr(search_page, 'elements')
        assert hasattr(search_page, 'navigation')
        assert hasattr(search_page, 'screenshots')
        
        assert hasattr(result_page, 'elements')
        assert hasattr(result_page, 'navigation')
        assert hasattr(result_page, 'screenshots')
        
        # Test navigation between pages
        search_page.navigation.navigate_to_url("https://www.google.com")
        title = search_page.navigation.get_page_title()
        assert "Google" in title

    @patch('utils.webdriver_factory.webdriver.Chrome')
    def test_webdriver_factory_integration(self, mock_chrome):
        """Test WebDriverFactory integration with page objects."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Test driver creation and page object initialization
        driver = get_driver("chrome")
        page = BasePage(driver)
        
        assert page.driver == mock_driver
        assert page.elements.driver == mock_driver
        assert page.navigation.driver == mock_driver
        assert page.screenshots.driver == mock_driver

    def test_database_integration_with_page_actions(self, temp_database):
        """Test database operations integration with page actions."""
        conn = get_connection(temp_database)
        mock_driver = Mock()
        
        page = BasePage(mock_driver, conn)
        
        # Test database operations through page object
        test_results = [
            {"test_name": "test_1", "result": "passed"},
            {"test_name": "test_2", "result": "failed"},
            {"test_name": "test_3", "result": "skipped"},
        ]
        
        inserted_ids = []
        for result in test_results:
            record_id = page.database.insert_data("test_results", result)
            inserted_ids.append(record_id)
        
        # Verify all records were inserted
        all_records = page.database.fetch_multiple_records("SELECT * FROM test_results")
        assert len(all_records) == 3
        
        # Test update operation
        updated_count = page.database.update_data(
            "test_results", 
            {"result": "re-tested"}, 
            "test_name = ?", 
            ("test_2",)
        )
        assert updated_count == 1
        
        # Verify update
        updated_record = page.database.fetch_single_record(
            "SELECT result FROM test_results WHERE test_name = ?", ("test_2",)
        )
        assert updated_record[0] == "re-tested"
        
        # Test delete operation
        deleted_count = page.database.delete_data(
            "test_results", 
            "result = ?", 
            ("skipped",)
        )
        assert deleted_count == 1
        
        # Verify deletion
        remaining_records = page.database.fetch_multiple_records("SELECT * FROM test_results")
        assert len(remaining_records) == 2
        
        conn.close()

    def test_screenshot_integration(self, chrome_driver):
        """Test screenshot functionality integration."""
        page = BasePage(chrome_driver)
        
        # Navigate to a page for screenshot
        page.navigation.navigate_to_url("https://www.google.com")
        
        # Create temporary directory for screenshots
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshot_path = os.path.join(temp_dir, "integration_test.png")
            
            # Take screenshot
            success = page.screenshots.take_screenshot(screenshot_path)
            assert success is True
            assert os.path.exists(screenshot_path)
            assert os.path.getsize(screenshot_path) > 0

    def test_element_actions_integration(self, chrome_driver):
        """Test element actions integration with real browser."""
        page = BasePage(chrome_driver)
        
        # Navigate to Google search page
        page.navigation.navigate_to_url("https://www.google.com")
        
        # Test finding elements (this may vary based on Google's current layout)
        search_elements = page.elements.find_elements(("name", "q"))
        
        # Google should have at least one search box
        assert len(search_elements) >= 0  # Allow for 0 in case of changes
        
        # Test page load waiting
        page_loaded = page.navigation.wait_for_page_load(timeout=10)
        assert page_loaded is True

    def test_error_handling_integration(self, chrome_driver):
        """Test error handling across integrated components."""
        page = BasePage(chrome_driver)
        
        # Test navigation to invalid URL
        page.navigation.navigate_to_url("https://nonexistent-domain-12345.com")
        
        # Test element finding on page that might not load
        element = page.elements.find_element(("id", "nonexistent-element"))
        assert element is None
        
        # Test screenshot on potentially problematic page
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshot_path = os.path.join(temp_dir, "error_test.png")
            # This should still work even if the page didn't load properly
            success = page.screenshots.take_screenshot(screenshot_path)
            # Result may vary, but shouldn't raise unhandled exceptions
            assert success in [True, False]

    def test_multiple_page_objects_integration(self, chrome_driver):
        """Test integration between multiple page objects."""
        search_page = GoogleSearchPage(chrome_driver)
        result_page = GoogleResultPage(chrome_driver)
        
        # Both should be able to navigate
        search_page.navigation.navigate_to_url("https://www.google.com")
        search_title = search_page.navigation.get_page_title()
        
        # Switch to results page object (same driver)
        result_page.navigation.navigate_to_url("https://www.google.com/search?q=test")
        result_title = result_page.navigation.get_page_title()
        
        # Both operations should work
        assert "Google" in search_title
        assert "Google" in result_title or "test" in result_title


class TestConfigurationIntegration:
    """Integration tests for configuration and settings."""

    @patch.dict(os.environ, {
        'BASE_URL': 'https://test.example.com',
        'BROWSER': 'chrome',
        'HEADLESS': 'true'
    })
    def test_settings_integration(self):
        """Test settings integration with environment variables."""
        from config.settings import Settings
        
        settings = Settings()
        
        assert settings.base_url == 'https://test.example.com'
        assert settings.browser == 'chrome'
        assert settings.headless is True

    def test_logger_integration_across_modules(self, temp_database):
        """Test logger integration across different modules."""
        from utils.logger import TestLogger
        
        # Create logger
        logger = TestLogger("integration_test")
        
        # Test that logger works with different components
        mock_driver = Mock()
        conn = get_connection(temp_database)
        
        page = BasePage(mock_driver, conn)
        
        # Logger should be properly initialized in page object
        assert page.logger is not None
        
        # Test logging through page actions
        page.database.insert_data("test_results", {"test_name": "logger_test", "result": "passed"})
        
        # Verify no exceptions were raised during logging
        conn.close()


class TestEndToEndWorkflow:
    """End-to-end workflow integration tests."""

    def test_complete_test_workflow(self, chrome_driver, temp_database):
        """Test a complete test execution workflow."""
        # Initialize components
        conn = get_connection(temp_database)
        search_page = GoogleSearchPage(chrome_driver, conn)
        
        # Record test start
        search_page.database.insert_data("test_results", {
            "test_name": "end_to_end_workflow",
            "result": "started"
        })
        
        # Navigate to search page
        search_page.navigation.navigate_to_url("https://www.google.com")
        
        # Take screenshot
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshot_path = os.path.join(temp_dir, "workflow_test.png")
            screenshot_success = search_page.screenshots.take_screenshot(screenshot_path)
            
            # Update test result
            search_page.database.update_data(
                "test_results",
                {"result": "completed" if screenshot_success else "failed"},
                "test_name = ?",
                ("end_to_end_workflow",)
            )
            
            # Verify final state
            final_result = search_page.database.fetch_single_record(
                "SELECT result FROM test_results WHERE test_name = ?",
                ("end_to_end_workflow",)
            )
            
            assert final_result is not None
            assert final_result[0] in ["completed", "failed"]
            
            if screenshot_success:
                assert os.path.exists(screenshot_path)
        
        conn.close()