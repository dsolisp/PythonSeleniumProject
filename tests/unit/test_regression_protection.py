"""Regression protection tests to ensure framework stability."""
import pytest
import os
import sys
from hamcrest import (
    assert_that, is_, equal_to, not_none, none, greater_than, less_than, 
    greater_than_or_equal_to, less_than_or_equal_to, has_length, instance_of, 
    has_key, contains_string, has_property, is_in, is_not
)


class TestRegressionProtection:
    """Tests to prevent regressions in core framework functionality."""
    
    def test_core_modules_importable(self):
        """Test that all core modules can be imported without errors."""
        try:
            from pages.base_page import BasePage
            from utils.webdriver_factory import WebDriverFactory
            from utils.sql_connection import get_connection
            assert_that(True, is_(True)), "All core modules imported successfully"
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")
    
    def test_webdriver_factory_exists(self):
        """Test that WebDriverFactory class exists and has required methods."""
        from utils.webdriver_factory import WebDriverFactory
        
        factory = WebDriverFactory()
        assert_that(factory, has_property('create_chrome_driver')), "WebDriverFactory missing create_chrome_driver method"
        assert_that(factory, has_property('create_firefox_driver')), "WebDriverFactory missing create_firefox_driver method"
    
    def test_base_page_exists(self):
        """Test that BasePage class exists and has required methods."""
        from pages.base_page import BasePage
        
        # Test that BasePage has essential methods
        assert_that(BasePage, has_property('__init__')), "BasePage missing __init__ method"
        # Note: We don't instantiate BasePage to avoid WebDriver dependency
    
    def test_database_connection_function_exists(self):
        """Test that database connection function exists."""
        from utils.sql_connection import get_connection
        assert_that(callable(get_connection), is_(True)), "get_connection is not callable"
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and contains expected dependencies."""
        requirements_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'requirements.txt')
        assert_that(os.path.exists(requirements_path), is_(True)), "requirements.txt file not found"
        
        with open(requirements_path, 'r') as f:
            content = f.read()
            assert_that(content, contains_string('selenium')), "selenium not found in requirements.txt"
            assert_that(content, contains_string('pytest')), "pytest not found in requirements.txt"
    
    def test_config_directory_structure(self):
        """Test that essential directories exist."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        essential_dirs = ['pages', 'utils', 'tests', 'locators']
        for dir_name in essential_dirs:
            dir_path = os.path.join(base_dir, dir_name)
            assert_that(os.path.exists(dir_path), is_(True)), f"Essential directory '{dir_name}' not found"
    
    def test_pytest_configuration(self):
        """Test that pytest configuration exists."""
        pytest_ini_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'pytest.ini')
        assert_that(os.path.exists(pytest_ini_path), is_(True)), "pytest.ini configuration file not found"