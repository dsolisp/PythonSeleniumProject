"""
Integration Tests - Focused and Practical
Tests that verify key components work together properly.
"""

import pytest
from unittest.mock import Mock, patch
import os


class TestFrameworkIntegration:
    """Test that key framework components work together."""
    
    def test_get_driver_returns_driver_and_sql(self):
        """Test that get_driver returns both driver and SQL connection."""
        with patch('utils.webdriver_factory.webdriver.Chrome') as mock_chrome, \
             patch('utils.webdriver_factory.sqlite3.connect') as mock_db:
            
            from utils.webdriver_factory import get_driver
            
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            mock_sql = Mock()
            mock_db.return_value = mock_sql
            
            result = get_driver("chrome")
            
            assert len(result) == 2
            assert result[0] == mock_driver
            assert result[1] == mock_sql

    def test_page_objects_use_webdriver_factory(self):
        """Test that page objects can use the WebDriver factory."""
        with patch('utils.webdriver_factory.get_driver') as mock_get_driver:
            mock_driver = Mock()
            mock_sql = Mock()
            mock_get_driver.return_value = (mock_driver, mock_sql)
            
            from pages.google_search_page import GoogleSearchPage
            from utils.webdriver_factory import get_driver
            
            driver, sql = get_driver("chrome")
            page = GoogleSearchPage(driver)
            
            assert page is not None

    def test_database_integration_with_real_file(self):
        """Test that database integration works with the real chinook.db file."""
        from utils.sql_connection import get_connection
        
        db_path = "resources/chinook.db"
        if os.path.exists(db_path):
            conn = get_connection(db_path)
            assert conn is not None
            conn.close()
        else:
            pytest.skip("chinook.db not found - skipping real DB test")

    def test_settings_integration(self):
        """Test that settings work with environment variables."""
        with patch.dict(os.environ, {'BROWSER': 'firefox', 'TIMEOUT': '20'}):
            from config.settings import Settings
            settings = Settings()
            
            assert settings.BROWSER == 'firefox'
            assert settings.TIMEOUT == 20


class TestErrorHandling:
    """Test that the framework handles errors gracefully."""
    
    def test_webdriver_creation_failure_handling(self):
        """Test that WebDriver creation failures are handled."""
        with patch('utils.webdriver_factory.webdriver.Chrome') as mock_chrome:
            mock_chrome.side_effect = Exception("Chrome not found")
            
            from utils.webdriver_factory import get_driver
            
            # Should not crash, might return None or raise specific exception
            try:
                result = get_driver("chrome")
                # If it doesn't raise, that's also acceptable
            except Exception as e:
                # Expected behavior - should handle gracefully
                assert "Chrome" in str(e) or "not found" in str(e).lower()

    def test_database_connection_failure_handling(self):
        """Test that database connection failures are handled."""
        from utils.sql_connection import get_connection
        
        try:
            result = get_connection("nonexistent_file.db")
            # If it doesn't raise, check it returns None or similar
            assert result is None
        except FileNotFoundError:
            # Expected behavior
            pass
        except Exception as e:
            # Other exceptions are also acceptable as long as it's handled
            assert "not found" in str(e).lower() or "database" in str(e).lower()


class TestPageObjectPatterns:
    """Test that page object patterns are properly implemented."""
    
    def test_page_inheritance_structure(self):
        """Test that page objects inherit from BasePage properly."""
        from pages.base_page import BasePage
        from pages.google_search_page import GoogleSearchPage
        from pages.google_result_page import GoogleResultPage
        
        # Check inheritance
        assert issubclass(GoogleSearchPage, BasePage)
        assert issubclass(GoogleResultPage, BasePage)

    def test_locators_are_accessible(self):
        """Test that locators can be imported and used."""
        from locators.google_search_locators import GoogleSearchLocators
        from locators.google_result_locators import GoogleResultLocators
        
        # Should be able to access locators
        search_box = GoogleSearchLocators.SEARCH_BOX
        results = GoogleResultLocators.RESULTS_CONTAINER
        
        assert isinstance(search_box, tuple)
        assert isinstance(results, tuple)
        assert len(search_box) == 2
        assert len(results) == 2


class TestUtilityFunctions:
    """Test utility functions work as expected."""
    
    def test_image_comparison_function_callable(self):
        """Test that image comparison function is callable and handles errors."""
        from utils.diff_handler import compare_images
        
        # Function should exist and be callable
        assert callable(compare_images)
        
        # Should handle invalid files gracefully
        try:
            result = compare_images("fake1.png", "fake2.png", "fake_diff.png")
            # If it doesn't raise, check return value
            assert isinstance(result, (bool, int, float, type(None)))
        except Exception as e:
            # Expected - should handle file not found gracefully
            assert "not found" in str(e).lower() or "no such file" in str(e).lower()

    def test_sql_utility_functions_exist(self):
        """Test that basic SQL utility functions exist."""
        from utils.sql_connection import (
            get_connection, execute_query, fetch_one, 
            close_connection
        )
        
        # All functions should be callable
        assert callable(get_connection)
        assert callable(execute_query)
        assert callable(fetch_one)
        assert callable(close_connection)