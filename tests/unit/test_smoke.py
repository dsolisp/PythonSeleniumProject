"""
Smoke Tests - Quick Framework Health Checks
These tests verify that the framework is in a working state.
"""

import pytest
from unittest.mock import Mock, patch


class TestFrameworkSmoke:
    """Quick smoke tests to verify framework health."""
    
    def test_all_core_imports_work(self):
        """Test that all core framework components can be imported."""
        # This is the most important test - if imports fail, nothing works
        try:
            from utils.webdriver_factory import get_driver
            from pages.base_page import BasePage
            from pages.google_search_page import GoogleSearchPage
            from pages.google_result_page import GoogleResultPage
            from locators.google_search_locators import GoogleSearchLocators
            from locators.google_result_locators import GoogleResultLocators
            from utils.sql_connection import get_connection
            from utils.diff_handler import compare_images
            from config.settings import Settings
            
            # If we get here, all imports worked
            assert True
            
        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")
    
    def test_basic_workflow_can_be_mocked(self):
        """Test that a basic automation workflow can be mocked successfully."""
        with patch('utils.webdriver_factory.webdriver.Chrome') as mock_chrome, \
             patch('utils.webdriver_factory.sqlite3.connect') as mock_db:
            
            # Mock the driver and database
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            mock_sql = Mock()
            mock_db.return_value = mock_sql
            
            # Test the workflow
            from utils.webdriver_factory import get_driver
            from pages.google_search_page import GoogleSearchPage
            
            # Get driver
            driver, sql = get_driver("chrome")
            assert driver is not None
            assert sql is not None
            
            # Create page object
            search_page = GoogleSearchPage(driver)
            assert search_page is not None
            
            # Verify page has expected attributes
            assert hasattr(search_page, 'driver')

    def test_settings_provide_expected_values(self):
        """Test that settings provide sensible default values."""
        from config.settings import Settings
        
        settings = Settings()
        
        # Should have basic required settings
        assert hasattr(settings, 'BROWSER')
        assert hasattr(settings, 'BASE_URL')
        assert hasattr(settings, 'TIMEOUT')
        
        # Values should be reasonable
        assert settings.BROWSER in ['chrome', 'firefox', 'edge', 'safari']
        assert 'http' in settings.BASE_URL.lower()
        assert isinstance(settings.TIMEOUT, int)
        assert settings.TIMEOUT > 0

    def test_locators_have_valid_format(self):
        """Test that locators follow the expected format."""
        from locators.google_search_locators import GoogleSearchLocators
        from selenium.webdriver.common.by import By
        
        # Check a few key locators
        search_box = GoogleSearchLocators.SEARCH_BOX
        search_button = GoogleSearchLocators.SEARCH_BUTTON
        
        # Should be tuples with (By.METHOD, "selector")
        assert isinstance(search_box, tuple)
        assert len(search_box) == 2
        assert hasattr(By, search_box[0].upper()) or search_box[0] in [By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME, By.XPATH, By.CSS_SELECTOR]
        assert isinstance(search_box[1], str)
        assert len(search_box[1]) > 0
        
        assert isinstance(search_button, tuple)
        assert len(search_button) == 2

    def test_framework_can_handle_basic_exceptions(self):
        """Test that framework components handle basic exceptions gracefully."""
        from pages.base_page import BasePage
        from config.settings import Settings
        
        # Should not crash when given None or mock objects
        try:
            mock_driver = Mock()
            mock_sql = Mock()
            
            base_page = BasePage(mock_driver, mock_sql)
            assert base_page is not None
            
            settings = Settings()
            assert settings is not None
            
        except Exception as e:
            pytest.fail(f"Framework crashed on basic operations: {e}")


class TestDependenciesAvailable:
    """Test that required dependencies are available."""
    
    def test_selenium_available(self):
        """Test that Selenium is properly installed."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            assert True
        except ImportError as e:
            pytest.fail(f"Selenium not properly installed: {e}")
    
    def test_sqlite_available(self):
        """Test that SQLite support is available."""
        try:
            import sqlite3
            # Test basic SQLite functionality
            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()
            assert result[0] == 1
        except Exception as e:
            pytest.fail(f"SQLite not working properly: {e}")
    
    def test_image_processing_available(self):
        """Test that image processing dependencies are available."""
        try:
            from PIL import Image
            import numpy as np
            assert True
        except ImportError:
            # PIL/numpy might not be installed, that's ok for basic framework
            pytest.skip("PIL/numpy not available - image processing features may be limited")