"""
Unit tests for WebDriver factory module.
Tests WebDriver creation, configuration, and database connections.
"""

import sqlite3
from unittest.mock import Mock, patch, MagicMock

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from utils.webdriver_factory import WebDriverFactory, DatabaseFactory, get_driver


class TestWebDriverFactory:
    """Test cases for WebDriverFactory class."""

    @patch('utils.webdriver_factory.webdriver.Chrome')
    @patch('utils.webdriver_factory.ChromeDriverManager')
    def test_create_chrome_driver_headless_true(self, mock_driver_manager, mock_chrome):
        """Test Chrome driver creation with headless mode enabled."""
        # Mock the driver manager
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        driver = WebDriverFactory.create_chrome_driver(headless=True)
        
        # Verify driver manager was called
        mock_driver_manager.assert_called_once()
        mock_driver_manager.return_value.install.assert_called_once()
        
        # Verify Chrome was instantiated
        mock_chrome.assert_called_once()
        
        # Verify the options passed to Chrome
        call_args = mock_chrome.call_args
        service = call_args[1]['service']
        options = call_args[1]['options']
        
        assert isinstance(service, ChromeService)
        assert isinstance(options, ChromeOptions)
        assert driver == mock_driver

    @patch('utils.webdriver_factory.webdriver.Chrome')
    @patch('utils.webdriver_factory.ChromeDriverManager')
    def test_create_chrome_driver_headless_false(self, mock_driver_manager, mock_chrome):
        """Test Chrome driver creation with headless mode disabled."""
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        driver = WebDriverFactory.create_chrome_driver(headless=False)
        
        # Verify Chrome was instantiated
        mock_chrome.assert_called_once()
        assert driver == mock_driver

    @patch('utils.webdriver_factory.webdriver.Chrome')
    @patch('utils.webdriver_factory.ChromeDriverManager')
    def test_chrome_options_configuration(self, mock_driver_manager, mock_chrome):
        """Test that Chrome options are configured correctly."""
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        WebDriverFactory.create_chrome_driver(headless=True)
        
        # Get the options that were passed
        call_args = mock_chrome.call_args
        options = call_args[1]['options']
        
        # Verify options are ChromeOptions instance
        assert isinstance(options, ChromeOptions)
        
        # Note: Testing specific options requires access to internal state
        # which may not be directly accessible

    def test_create_chrome_driver_default_parameters(self):
        """Test that create_chrome_driver works with default parameters."""
        with patch('utils.webdriver_factory.webdriver.Chrome') as mock_chrome:
            with patch('utils.webdriver_factory.ChromeDriverManager') as mock_driver_manager:
                mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
                mock_driver = Mock()
                mock_chrome.return_value = mock_driver
                
                # Should work without specifying headless parameter
                driver = WebDriverFactory.create_chrome_driver()
                assert driver == mock_driver

    @patch('utils.webdriver_factory.webdriver.Chrome')
    @patch('utils.webdriver_factory.ChromeDriverManager')
    def test_create_chrome_driver_exception_handling(self, mock_driver_manager, mock_chrome):
        """Test exception handling in Chrome driver creation."""
        mock_driver_manager.return_value.install.side_effect = Exception("Driver download failed")
        
        with pytest.raises(Exception):
            WebDriverFactory.create_chrome_driver()

    @patch('utils.webdriver_factory.webdriver.Firefox')
    @patch('utils.webdriver_factory.GeckoDriverManager')
    def test_create_firefox_driver(self, mock_driver_manager, mock_firefox):
        """Test Firefox driver creation."""
        mock_driver_manager.return_value.install.return_value = "/path/to/geckodriver"
        mock_driver = Mock()
        mock_firefox.return_value = mock_driver
        
        driver = WebDriverFactory.create_firefox_driver(headless=True)
        
        mock_driver_manager.assert_called_once()
        mock_firefox.assert_called_once()
        assert driver == mock_driver

    @patch('utils.webdriver_factory.webdriver.Edge')
    @patch('utils.webdriver_factory.EdgeChromiumDriverManager')
    def test_create_edge_driver(self, mock_driver_manager, mock_edge):
        """Test Edge driver creation."""
        mock_driver_manager.return_value.install.return_value = "/path/to/edgedriver"
        mock_driver = Mock()
        mock_edge.return_value = mock_driver
        
        driver = WebDriverFactory.create_edge_driver(headless=False)
        
        mock_driver_manager.assert_called_once()
        mock_edge.assert_called_once()
        assert driver == mock_driver


class TestDatabaseFactory:
    """Test cases for DatabaseFactory class."""

    @patch('utils.webdriver_factory.sqlite3.connect')
    def test_create_database_connection_default_path(self, mock_connect):
        """Test database connection with default path."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection = DatabaseFactory.create_database_connection()
        
        mock_connect.assert_called_once_with("resources/chinook.db")
        assert connection == mock_connection

    @patch('utils.webdriver_factory.sqlite3.connect')
    def test_create_database_connection_custom_path(self, mock_connect):
        """Test database connection with custom path."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        custom_path = "/custom/path/to/database.db"
        
        connection = DatabaseFactory.create_database_connection(custom_path)
        
        mock_connect.assert_called_once_with(custom_path)
        assert connection == mock_connection

    @patch('utils.webdriver_factory.sqlite3.connect')
    def test_database_connection_row_factory(self, mock_connect):
        """Test that database connection has Row factory set."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        connection = DatabaseFactory.create_database_connection()
        
        # Verify row_factory was set to sqlite3.Row
        assert mock_connection.row_factory == sqlite3.Row

    @patch('utils.webdriver_factory.sqlite3.connect')
    def test_database_connection_exception_handling(self, mock_connect):
        """Test exception handling in database connection."""
        mock_connect.side_effect = sqlite3.Error("Database connection failed")
        
        with pytest.raises(sqlite3.Error):
            DatabaseFactory.create_database_connection()


class TestGetDriverFunction:
    """Test cases for get_driver convenience function."""

    @patch('utils.webdriver_factory.WebDriverFactory.create_chrome_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_chrome_default(self, mock_db_factory, mock_chrome_factory):
        """Test get_driver function with Chrome (default browser)."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_chrome_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        
        driver_tuple = get_driver()
        
        mock_chrome_factory.assert_called_once_with(headless=False)
        mock_db_factory.assert_called_once_with(None)
        assert driver_tuple == (mock_driver, mock_db)

    @patch('utils.webdriver_factory.WebDriverFactory.create_chrome_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_chrome_headless(self, mock_db_factory, mock_chrome_factory):
        """Test get_driver function with Chrome in headless mode."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_chrome_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        
        driver_tuple = get_driver(browser="chrome", headless=True)
        
        mock_chrome_factory.assert_called_once_with(headless=True)
        assert driver_tuple == (mock_driver, mock_db)

    @patch('utils.webdriver_factory.WebDriverFactory.create_firefox_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_firefox(self, mock_db_factory, mock_firefox_factory):
        """Test get_driver function with Firefox."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_firefox_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        
        driver_tuple = get_driver(browser="firefox", headless=False)
        
        mock_firefox_factory.assert_called_once_with(headless=False)
        mock_db_factory.assert_called_once_with(None)
        assert driver_tuple == (mock_driver, mock_db)

    @patch('utils.webdriver_factory.WebDriverFactory.create_edge_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_edge(self, mock_db_factory, mock_edge_factory):
        """Test get_driver function with Edge."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_edge_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        
        driver_tuple = get_driver(browser="edge", headless=True)
        
        mock_edge_factory.assert_called_once_with(headless=True)
        mock_db_factory.assert_called_once_with(None)
        assert driver_tuple == (mock_driver, mock_db)

    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_unsupported_browser(self, mock_db_factory):
        """Test get_driver function with unsupported browser."""
        mock_db = Mock()
        mock_db_factory.return_value = mock_db
        
        with pytest.raises(ValueError, match="Unsupported browser: safari"):
            get_driver(browser="safari")

    @patch('utils.webdriver_factory.WebDriverFactory.create_chrome_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_custom_db_path(self, mock_db_factory, mock_chrome_factory):
        """Test get_driver function with custom database path."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_chrome_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        custom_db_path = "/custom/path/to/db.sqlite"
        
        driver_tuple = get_driver(db_path=custom_db_path)
        
        mock_db_factory.assert_called_once_with(custom_db_path)
        assert driver_tuple == (mock_driver, mock_db)

    @patch('utils.webdriver_factory.WebDriverFactory.create_chrome_driver')
    @patch('utils.webdriver_factory.DatabaseFactory.create_database_connection')
    def test_get_driver_all_parameters(self, mock_db_factory, mock_chrome_factory):
        """Test get_driver function with all parameters specified."""
        mock_driver = Mock()
        mock_db = Mock()
        mock_chrome_factory.return_value = mock_driver
        mock_db_factory.return_value = mock_db
        
        driver_tuple = get_driver(
            browser="chrome",
            headless=True,
            db_path="/custom/db.sqlite"
        )
        
        mock_chrome_factory.assert_called_once_with(headless=True)
        mock_db_factory.assert_called_once_with("/custom/db.sqlite")
        assert driver_tuple == (mock_driver, mock_db)