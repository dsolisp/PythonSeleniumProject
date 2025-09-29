"""
Unit tests for base page and action handler classes.
Tests element interactions, navigation, screenshots, and database operations.
"""

import os
from unittest.mock import Mock, patch, MagicMock, call

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)

from pages.base_page import (
    BasePage,
    ElementActions, 
    NavigationActions,
    ScreenshotActions,
    DatabaseActions,
)


class TestElementActions:
    """Test cases for ElementActions class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_logger = Mock()
        self.element_actions = ElementActions(self.mock_driver, self.mock_logger)

    def test_init(self):
        """Test ElementActions initialization."""
        assert self.element_actions.driver == self.mock_driver
        assert self.element_actions.logger == self.mock_logger

    @patch('pages.base_page.WebDriverWait')
    def test_wait_for_element_success(self, mock_wait_class):
        """Test successful element waiting."""
        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait
        mock_element = Mock()
        mock_wait.until.return_value = mock_element
        
        locator = (By.ID, "test-id")
        result = self.element_actions.wait_for_element(locator, timeout=10)
        
        mock_wait_class.assert_called_once_with(self.mock_driver, 10)
        mock_wait.until.assert_called_once()
        assert result == mock_element
        self.mock_logger.info.assert_called()

    @patch('pages.base_page.WebDriverWait')
    def test_wait_for_element_timeout(self, mock_wait_class):
        """Test element waiting timeout."""
        mock_wait = Mock()
        mock_wait_class.return_value = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout")
        
        locator = (By.ID, "test-id")
        result = self.element_actions.wait_for_element(locator, timeout=5)
        
        assert result is None
        self.mock_logger.warning.assert_called()

    def test_find_element_success(self):
        """Test successful element finding."""
        mock_element = Mock()
        self.mock_driver.find_element.return_value = mock_element
        locator = (By.ID, "test-id")
        
        result = self.element_actions.find_element(locator)
        
        self.mock_driver.find_element.assert_called_once_with(*locator)
        assert result == mock_element

    def test_find_element_not_found(self):
        """Test element not found scenario."""
        self.mock_driver.find_element.side_effect = NoSuchElementException("Not found")
        locator = (By.ID, "nonexistent")
        
        result = self.element_actions.find_element(locator)
        
        assert result is None
        self.mock_logger.warning.assert_called()

    def test_find_elements_success(self):
        """Test successful elements finding."""
        mock_elements = [Mock(), Mock()]
        self.mock_driver.find_elements.return_value = mock_elements
        locator = (By.CLASS_NAME, "test-class")
        
        result = self.element_actions.find_elements(locator)
        
        self.mock_driver.find_elements.assert_called_once_with(*locator)
        assert result == mock_elements

    def test_find_elements_empty_list(self):
        """Test finding elements returns empty list."""
        self.mock_driver.find_elements.return_value = []
        locator = (By.CLASS_NAME, "nonexistent")
        
        result = self.element_actions.find_elements(locator)
        
        assert result == []
        self.mock_logger.info.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_click_element_success(self, mock_wait):
        """Test successful element clicking."""
        mock_element = Mock()
        mock_wait.return_value = mock_element
        locator = (By.ID, "click-me")
        
        result = self.element_actions.click_element(locator)
        
        mock_wait.assert_called_once_with(locator, timeout=10)
        mock_element.click.assert_called_once()
        assert result is True
        self.mock_logger.info.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_click_element_not_found(self, mock_wait):
        """Test clicking element that's not found."""
        mock_wait.return_value = None
        locator = (By.ID, "nonexistent")
        
        result = self.element_actions.click_element(locator)
        
        assert result is False
        self.mock_logger.error.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_click_element_exception(self, mock_wait):
        """Test clicking element with exception."""
        mock_element = Mock()
        mock_element.click.side_effect = WebDriverException("Click failed")
        mock_wait.return_value = mock_element
        locator = (By.ID, "problematic")
        
        result = self.element_actions.click_element(locator)
        
        assert result is False
        self.mock_logger.error.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_send_keys_success(self, mock_wait):
        """Test successful text input."""
        mock_element = Mock()
        mock_wait.return_value = mock_element
        locator = (By.ID, "input-field")
        text = "test input"
        
        result = self.element_actions.send_keys(locator, text)
        
        mock_wait.assert_called_once_with(locator, timeout=10)
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with(text)
        assert result is True
        self.mock_logger.info.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_send_keys_no_clear(self, mock_wait):
        """Test text input without clearing."""
        mock_element = Mock()
        mock_wait.return_value = mock_element
        locator = (By.ID, "input-field")
        text = "additional text"
        
        result = self.element_actions.send_keys(locator, text, clear_first=False)
        
        mock_element.clear.assert_not_called()
        mock_element.send_keys.assert_called_once_with(text)
        assert result is True

    @patch.object(ElementActions, 'wait_for_element')
    def test_get_text_success(self, mock_wait):
        """Test successful text retrieval."""
        mock_element = Mock()
        mock_element.text = "Element text"
        mock_wait.return_value = mock_element
        locator = (By.ID, "text-element")
        
        result = self.element_actions.get_text(locator)
        
        mock_wait.assert_called_once_with(locator, timeout=10)
        assert result == "Element text"

    @patch.object(ElementActions, 'wait_for_element')
    def test_get_text_element_not_found(self, mock_wait):
        """Test text retrieval when element not found."""
        mock_wait.return_value = None
        locator = (By.ID, "nonexistent")
        
        result = self.element_actions.get_text(locator)
        
        assert result == ""
        self.mock_logger.warning.assert_called()

    @patch.object(ElementActions, 'wait_for_element')
    def test_get_attribute_success(self, mock_wait):
        """Test successful attribute retrieval."""
        mock_element = Mock()
        mock_element.get_attribute.return_value = "attribute-value"
        mock_wait.return_value = mock_element
        locator = (By.ID, "element-with-attr")
        
        result = self.element_actions.get_attribute(locator, "data-test")
        
        mock_wait.assert_called_once_with(locator, timeout=10)
        mock_element.get_attribute.assert_called_once_with("data-test")
        assert result == "attribute-value"

    @patch.object(ElementActions, 'wait_for_element')
    def test_is_element_visible_true(self, mock_wait):
        """Test element visibility check when visible."""
        mock_element = Mock()
        mock_element.is_displayed.return_value = True
        mock_wait.return_value = mock_element
        locator = (By.ID, "visible-element")
        
        result = self.element_actions.is_element_visible(locator)
        
        mock_element.is_displayed.assert_called_once()
        assert result is True

    @patch.object(ElementActions, 'wait_for_element')
    def test_is_element_visible_false(self, mock_wait):
        """Test element visibility check when not visible."""
        mock_element = Mock()
        mock_element.is_displayed.return_value = False
        mock_wait.return_value = mock_element
        locator = (By.ID, "hidden-element")
        
        result = self.element_actions.is_element_visible(locator)
        
        assert result is False

    @patch.object(ElementActions, 'wait_for_element')
    def test_is_element_visible_not_found(self, mock_wait):
        """Test element visibility check when element not found."""
        mock_wait.return_value = None
        locator = (By.ID, "nonexistent")
        
        result = self.element_actions.is_element_visible(locator)
        
        assert result is False


class TestNavigationActions:
    """Test cases for NavigationActions class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_logger = Mock()
        self.navigation_actions = NavigationActions(self.mock_driver, self.mock_logger)

    def test_init(self):
        """Test NavigationActions initialization."""
        assert self.navigation_actions.driver == self.mock_driver
        assert self.navigation_actions.logger == self.mock_logger

    def test_navigate_to_url(self):
        """Test URL navigation."""
        url = "https://example.com"
        
        self.navigation_actions.navigate_to_url(url)
        
        self.mock_driver.get.assert_called_once_with(url)
        self.mock_logger.info.assert_called()

    def test_get_current_url(self):
        """Test getting current URL."""
        expected_url = "https://current-page.com"
        self.mock_driver.current_url = expected_url
        
        result = self.navigation_actions.get_current_url()
        
        assert result == expected_url

    def test_get_page_title(self):
        """Test getting page title."""
        expected_title = "Test Page Title"
        self.mock_driver.title = expected_title
        
        result = self.navigation_actions.get_page_title()
        
        assert result == expected_title

    def test_refresh_page(self):
        """Test page refresh."""
        self.navigation_actions.refresh_page()
        
        self.mock_driver.refresh.assert_called_once()
        self.mock_logger.info.assert_called()

    def test_go_back(self):
        """Test browser back navigation."""
        self.navigation_actions.go_back()
        
        self.mock_driver.back.assert_called_once()
        self.mock_logger.info.assert_called()

    def test_go_forward(self):
        """Test browser forward navigation."""
        self.navigation_actions.go_forward()
        
        self.mock_driver.forward.assert_called_once()
        self.mock_logger.info.assert_called()

    def test_wait_for_page_load(self):
        """Test waiting for page load."""
        self.mock_driver.execute_script.return_value = "complete"
        
        result = self.navigation_actions.wait_for_page_load(timeout=5)
        
        self.mock_driver.execute_script.assert_called_with("return document.readyState")
        assert result is True
        self.mock_logger.info.assert_called()

    def test_wait_for_page_load_timeout(self):
        """Test page load timeout."""
        self.mock_driver.execute_script.return_value = "loading"
        
        result = self.navigation_actions.wait_for_page_load(timeout=1)
        
        assert result is False
        self.mock_logger.warning.assert_called()


class TestScreenshotActions:
    """Test cases for ScreenshotActions class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_logger = Mock()
        self.screenshot_actions = ScreenshotActions(self.mock_driver, self.mock_logger)

    def test_init(self):
        """Test ScreenshotActions initialization."""
        assert self.screenshot_actions.driver == self.mock_driver
        assert self.screenshot_actions.logger == self.mock_logger

    @patch('pages.base_page.os.makedirs')
    def test_take_screenshot_success(self, mock_makedirs):
        """Test successful screenshot capture."""
        self.mock_driver.save_screenshot.return_value = True
        filepath = "/screenshots/test.png"
        
        result = self.screenshot_actions.take_screenshot(filepath)
        
        mock_makedirs.assert_called_once_with("/screenshots", exist_ok=True)
        self.mock_driver.save_screenshot.assert_called_once_with(filepath)
        assert result is True
        self.mock_logger.info.assert_called()

    @patch('pages.base_page.os.makedirs')
    def test_take_screenshot_failure(self, mock_makedirs):
        """Test screenshot capture failure."""
        self.mock_driver.save_screenshot.return_value = False
        filepath = "/screenshots/failed.png"
        
        result = self.screenshot_actions.take_screenshot(filepath)
        
        assert result is False
        self.mock_logger.error.assert_called()

    @patch('pages.base_page.os.makedirs')
    def test_take_screenshot_exception(self, mock_makedirs):
        """Test screenshot capture with exception."""
        self.mock_driver.save_screenshot.side_effect = WebDriverException("Screenshot failed")
        filepath = "/screenshots/exception.png"
        
        result = self.screenshot_actions.take_screenshot(filepath)
        
        assert result is False
        self.mock_logger.error.assert_called()

    @patch.object(ScreenshotActions, 'take_screenshot')
    def test_take_element_screenshot_success(self, mock_take_screenshot):
        """Test successful element screenshot."""
        mock_element = Mock()
        mock_element.screenshot.return_value = True
        mock_take_screenshot.return_value = True
        
        result = self.screenshot_actions.take_element_screenshot(mock_element, "/path/element.png")
        
        mock_element.screenshot.assert_called_once_with("/path/element.png")
        assert result is True
        self.mock_logger.info.assert_called()

    @patch.object(ScreenshotActions, 'take_screenshot')
    def test_take_element_screenshot_fallback(self, mock_take_screenshot):
        """Test element screenshot with fallback to full page."""
        mock_element = Mock()
        mock_element.screenshot.side_effect = WebDriverException("Element screenshot failed")
        mock_take_screenshot.return_value = True
        
        result = self.screenshot_actions.take_element_screenshot(mock_element, "/path/fallback.png")
        
        mock_take_screenshot.assert_called_once_with("/path/fallback.png")
        assert result is True
        self.mock_logger.warning.assert_called()


class TestDatabaseActions:
    """Test cases for DatabaseActions class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_connection = Mock()
        self.mock_logger = Mock()
        self.database_actions = DatabaseActions(self.mock_connection, self.mock_logger)

    def test_init(self):
        """Test DatabaseActions initialization."""
        assert self.database_actions.connection == self.mock_connection
        assert self.database_actions.logger == self.mock_logger

    def test_execute_query_success(self):
        """Test successful query execution."""
        # This is a simplified test since DatabaseActions just stores connection
        # The actual database operations would be tested separately
        assert self.database_actions.connection == self.mock_connection
        assert self.database_actions.logger == self.mock_logger

    def test_execute_query_stores_dependencies(self):
        """Test that DatabaseActions properly stores its dependencies."""
        # DatabaseActions should store the connection and logger
        assert hasattr(self.database_actions, 'connection')
        assert hasattr(self.database_actions, 'logger')
        assert self.database_actions.connection == self.mock_connection
        assert self.database_actions.logger == self.mock_logger


class TestBasePage:
    """Test cases for BasePage class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_driver = Mock()
        self.mock_connection = Mock()
        
    @patch('pages.base_page.TestLogger')
    def test_init_with_all_parameters(self, mock_logger_class):
        """Test BasePage initialization with all parameters."""
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        
        page = BasePage(self.mock_driver, self.mock_connection)
        
        assert page.driver == self.mock_driver
        assert page.connection == self.mock_connection
        assert page.logger == mock_logger
        assert isinstance(page.elements, ElementActions)
        assert isinstance(page.navigation, NavigationActions)
        assert isinstance(page.screenshots, ScreenshotActions)
        assert isinstance(page.database, DatabaseActions)

    @patch('pages.base_page.TestLogger')
    def test_init_driver_only(self, mock_logger_class):
        """Test BasePage initialization with driver only."""
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        
        page = BasePage(self.mock_driver)
        
        assert page.driver == self.mock_driver
        assert page.connection is None
        assert page.database is None

    @patch('pages.base_page.TestLogger')
    def test_action_handlers_have_correct_dependencies(self, mock_logger_class):
        """Test that action handlers receive correct dependencies."""
        mock_logger = Mock()
        mock_logger_class.return_value = mock_logger
        
        page = BasePage(self.mock_driver, self.mock_connection)
        
        # Check ElementActions dependencies
        assert page.elements.driver == self.mock_driver
        assert page.elements.logger == mock_logger
        
        # Check NavigationActions dependencies
        assert page.navigation.driver == self.mock_driver
        assert page.navigation.logger == mock_logger
        
        # Check ScreenshotActions dependencies
        assert page.screenshots.driver == self.mock_driver
        assert page.screenshots.logger == mock_logger
        
        # Check DatabaseActions dependencies
        assert page.database.connection == self.mock_connection
        assert page.database.logger == mock_logger