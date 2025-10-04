"""
Smoke Tests - Quick Framework Health Checks
These tests verify that the framework is in a working state.
"""

import pytest
from unittest.mock import Mock, patch
from hamcrest import (
    assert_that, is_, equal_to, not_none, none, greater_than, less_than, 
    greater_than_or_equal_to, less_than_or_equal_to, has_length, instance_of, 
    has_key, contains_string, has_property, is_in, is_not
)


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
            assert_that(True, is_(True))
            
        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")
    
    def test_settings_provide_expected_values(self):
        """Test that settings provide sensible default values."""
        from config.settings import Settings
        
        settings = Settings()
        
        # Should have basic required settings
        assert_that(settings, has_property('BROWSER'))
        assert_that(settings, has_property('BASE_URL'))
        assert_that(settings, has_property('TIMEOUT'))
        
        # Values should be reasonable
        assert_that(settings.BROWSER, is_in(['chrome', 'firefox', 'edge', 'safari']))
        assert_that(settings.BASE_URL.lower(), contains_string('http'))
        assert_that(settings.TIMEOUT, instance_of(int))
        assert_that(settings.TIMEOUT, greater_than(0))

    def test_locators_have_valid_format(self):
        """Test that locators follow the expected format."""
        from locators.google_search_locators import GoogleSearchLocators
        from selenium.webdriver.common.by import By
        
        # Check a few key locators
        search_box = GoogleSearchLocators.SEARCH_BOX
        search_button = GoogleSearchLocators.SEARCH_BUTTON
        
        # Should be tuples with (By.METHOD, "selector")
        assert_that(search_box, instance_of(tuple))
        assert_that(len(search_box), equal_to(2))
        assert_that(search_box[0], is_in([By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME, By.XPATH, By.CSS_SELECTOR]))
        assert_that(search_box[1], instance_of(str))
        assert_that(len(search_box[1]), greater_than(0))
        
        assert_that(search_button, instance_of(tuple))
        assert_that(len(search_button), equal_to(2))


class TestDependenciesAvailable:
    """Test that required dependencies are available."""
    
    def test_selenium_available(self):
        """Test that Selenium is properly installed."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            assert_that(True, is_(True))
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
            assert_that(result[0], equal_to(1))
        except Exception as e:
            pytest.fail(f"SQLite not working properly: {e}")
    
    def test_image_processing_available(self):
        """Test that image processing dependencies are available."""
        try:
            from PIL import Image
            import numpy as np
            assert_that(True, is_(True))
        except ImportError:
            # PIL/numpy might not be installed, that's ok for basic framework
            pytest.skip("PIL/numpy not available - image processing features may be limited")