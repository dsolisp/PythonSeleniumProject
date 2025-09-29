"""
Base page class for web automation with specialized action handlers.
"""

import os
import time
from typing import Any, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from utils.logger import logger, TestLogger


class ElementActions:
    """
    Handles all element interactions and operations.
    """

    def __init__(self, driver: webdriver.Chrome, logger=None):
        self.driver = driver
        self.logger = logger or globals().get('logger')
        self.timeout = settings.TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)
        self.actions = ActionChains(driver)

    def wait_for_element(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """Wait for element to be present."""
        wait_timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.info(f"Element found: {locator}")
            return element
        except TimeoutException:
            self.logger.warning(f"Element not found within {wait_timeout}s: {locator}")
            return None

    def find_element(self, locator: Tuple[str, str]) -> Optional[Any]:
        """Find element without explicit wait."""
        try:
            element = self.driver.find_element(*locator)
            return element
        except Exception as e:
            self.logger.warning(f"Element not found: {locator}, Error: {e}")
            return None

    def find_elements(self, locator: Tuple[str, str]) -> List[Any]:
        """Find multiple elements."""
        self.logger.info(f"Finding elements: {locator}")
        try:
            elements = self.driver.find_elements(*locator)
            if not elements:
                self.logger.info(f"No elements found for: {locator}")
            return elements
        except Exception as e:
            self.logger.warning(f"Elements not found: {locator}, Error: {e}")
            return []

    def find_element_safely(
        self, locator: Tuple[str, str], timeout: int = None
    ) -> Optional[Any]:
        """Find element with retry logic - DRY principle applied."""
        timeout = timeout or self.timeout

        for attempt in range(3):  # Retry logic
            try:
                return self.wait.until(EC.presence_of_element_located(locator))
            except StaleElementReferenceException:
                if attempt < 2:
                    time.sleep(0.5)
                    continue
                raise
            except TimeoutException:
                return None

    def click_element(
        self, locator: Tuple[str, str], use_javascript: bool = False
    ) -> bool:
        """Click element with fallback strategy."""
        element = self.wait_for_element(locator, timeout=10)
        if not element:
            self.logger.error(f"Cannot click element - not found: {locator}")
            return False

        try:
            if use_javascript:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            self.logger.info(f"Successfully clicked element: {locator}")
            return True
        except ElementNotInteractableException:
            if not use_javascript:
                return self.click_element(locator, use_javascript=True)
            self.logger.error(f"Element not interactable: {locator}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to click element {locator}: {e}")
            return False

    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True) -> bool:
        """Send keys to element."""
        element = self.wait_for_element(locator, timeout=10)
        if not element:
            return False
        
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            self.logger.info(f"Successfully sent keys to {locator}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send keys to {locator}: {e}")
            return False

    def get_text(self, locator: Tuple[str, str]) -> str:
        """Get text from element."""
        element = self.wait_for_element(locator, timeout=10)
        if not element:
            self.logger.warning(f"Cannot get text - element not found: {locator}")
            return ""
        
        try:
            text = element.text
            self.logger.info(f"Got text from {locator}: {text}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get text from {locator}: {e}")
            return ""

    def get_attribute(self, locator: Tuple[str, str], attribute: str) -> str:
        """Get attribute from element."""
        element = self.wait_for_element(locator, timeout=10)
        if not element:
            return ""
        
        try:
            attr_value = element.get_attribute(attribute) or ""
            self.logger.info(f"Got attribute {attribute} from {locator}: {attr_value}")
            return attr_value
        except Exception as e:
            self.logger.error(f"Failed to get attribute {attribute} from {locator}: {e}")
            return ""

    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 1) -> bool:
        """Check if element is visible."""
        element = self.wait_for_element(locator, timeout=timeout)
        if not element:
            return False
        
        try:
            is_visible = element.is_displayed()
            self.logger.info(f"Element visibility check for {locator}: {is_visible}")
            return is_visible
        except Exception as e:
            self.logger.error(f"Error checking visibility of {locator}: {e}")
            return False

    def type_in_element(self, locator: Tuple[str, str], text: str, clear_first: bool = True) -> bool:
        """Type text into element - alias for send_keys."""
        return self.send_keys(locator, text, clear_first)

    def get_element_text(self, locator: Tuple[str, str]) -> str:
        """Get text from element - alias for get_text."""
        return self.get_text(locator)

    def wait_for_clickable(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """Wait for element to be clickable."""
        wait_timeout = timeout or self.timeout
        try:
            element = WebDriverWait(self.driver, wait_timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            return None


class NavigationActions:
    """
    Handles page navigation operations.
    """

    def __init__(self, driver: webdriver.Chrome, logger):
        self.driver = driver
        self.logger = logger

    def navigate_to_url(self, url: str) -> bool:
        """Navigate to URL safely."""
        self.logger.info(f"Navigating to: {url}")
        try:
            self.driver.get(url)
            self.logger.debug(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False

    def refresh_current_page(self) -> bool:
        """Refresh page safely."""
        try:
            self.driver.refresh()
            return True
        except Exception:
            return False

    def get_current_page_title(self) -> str:
        """Get page title safely."""
        self.logger.info("Getting current page title")
        try:
            title = self.driver.title
            self.logger.debug(f"Page title retrieved: {title}")
            return title
        except Exception as e:
            self.logger.warning(f"Failed to get page title: {str(e)}")
            return ""

    def get_current_url(self) -> str:
        """Get current URL safely."""
        try:
            return self.driver.current_url
        except Exception:
            return ""

    def wait_for_page_load(self, timeout: int = None) -> bool:
        """Wait for page to fully load."""
        timeout = timeout or settings.TIMEOUT
        self.logger.info(f"Waiting for page to load (timeout: {timeout}s)")
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.logger.debug("Page loaded successfully")
            return True
        except TimeoutException:
            self.logger.warning("Page load timeout exceeded")
            return False

    def get_page_title(self) -> str:
        """Get page title - alias for get_current_page_title."""
        return self.get_current_page_title()

    def refresh_page(self) -> bool:
        """Refresh the current page."""
        self.logger.info("Refreshing current page")
        try:
            self.driver.refresh()
            self.logger.debug("Page refreshed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            return False

    def go_back(self) -> bool:
        """Navigate back in browser history."""
        self.logger.info("Going back in browser history")
        try:
            self.driver.back()
            self.logger.debug("Successfully navigated back")
            return True
        except Exception as e:
            self.logger.error(f"Failed to go back: {str(e)}")
            return False

    def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        self.logger.info("Going forward in browser history")
        try:
            self.driver.forward()
            self.logger.debug("Successfully navigated forward")
            return True
        except Exception as e:
            self.logger.error(f"Failed to go forward: {str(e)}")
            return False


class ScreenshotActions:
    """
    Handles screenshot capture operations.
    """

    def __init__(self, driver: webdriver.Chrome, logger):
        self.driver = driver
        self.logger = logger

    def take_page_screenshot(self, filename: str = None) -> str:
        """Take screenshot with automatic naming."""
        try:
            from datetime import datetime
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filepath = os.path.join(screenshots_dir, filename)
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""

    def take_screenshot(self, filename: str = None) -> bool:
        """Take screenshot - returns True on success."""
        try:
            from datetime import datetime
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  
                filename = f"screenshots/screenshot_{timestamp}.png"
            
            # Ensure parent directory exists
            directory = os.path.dirname(filename)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            result = self.driver.save_screenshot(filename)
            if result:
                self.logger.info(f"Screenshot saved: {filename}")
                return True
            else:
                self.logger.error(f"Failed to save screenshot: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False

    def take_element_screenshot(self, element, filename: str = None) -> bool:
        """Take screenshot of specific element."""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"element_screenshot_{timestamp}.png"
            
            result = element.screenshot(filename)
            if result:
                self.logger.info(f"Element screenshot saved: {filename}")
                return True
            else:
                self.logger.error(f"Failed to save element screenshot: {filename}")
                return False
        except Exception as e:
            self.logger.warning(f"Element screenshot failed, using fallback: {e}")
            # Fallback to full page screenshot
            return self.take_screenshot(filename)


class DatabaseActions:
    """
    Handles database query operations.
    """

    def __init__(self, database_connection: Optional[object], logger):
        self.connection = database_connection
        self.logger = logger

    def execute_database_query(
        self, query: str, parameters: Optional[tuple] = None
    ) -> List[dict]:
        """Execute database query with error handling."""
        if not self.connection:
            logger.warning("No database connection available")
            return []

        try:
            cursor = self.connection.execute(query, parameters or ())
            results = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Database query executed successfully, {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            return []

    def execute_database_query(
        self, query: str, parameters: Optional[tuple] = None
    ) -> List[dict]:
        """Execute database query safely."""
        if not self.connection:
            return []

        try:
            # This would need to be implemented based on your specific SQL utility
            # For now, returning empty list as placeholder
            return []
        except Exception:
            return []

    def insert_data(self, table: str, data: dict) -> Optional[int]:
        """Insert data into database table."""
        if not self.connection:
            return None
        
        try:
            # Import sql_connection functions
            from utils.sql_connection import insert_data as sql_insert
            return sql_insert(self.connection, table, data)
        except Exception as e:
            self.logger.error(f"Failed to insert data: {e}")
            return None

    def fetch_single_record(self, query: str, params: tuple = None):
        """Fetch single record from database."""
        if not self.connection:
            return None
        
        try:
            from utils.sql_connection import execute_and_fetch_one
            return execute_and_fetch_one(self.connection, query, params)
        except Exception as e:
            self.logger.error(f"Failed to fetch single record: {e}")
            return None

    def fetch_multiple_records(self, query: str, params: tuple = None):
        """Fetch multiple records from database."""
        if not self.connection:
            return []
        
        try:
            from utils.sql_connection import execute_and_fetch_all
            return execute_and_fetch_all(self.connection, query, params)
        except Exception as e:
            self.logger.error(f"Failed to fetch multiple records: {e}")
            return []

    def update_data(self, table: str, data: dict, where_clause: str, where_params: tuple = None) -> int:
        """Update data in database table."""
        if not self.connection:
            return 0
        
        try:
            from utils.sql_connection import update_data as sql_update
            return sql_update(self.connection, table, data, where_clause, where_params)
        except Exception as e:
            self.logger.error(f"Failed to update data: {e}")
            return 0

    def delete_data(self, table: str, where_clause: str, where_params: tuple = None) -> int:
        """Delete data from database table."""
        if not self.connection:
            return 0
        
        try:
            from utils.sql_connection import delete_data as sql_delete
            return sql_delete(self.connection, table, where_clause, where_params)
        except Exception as e:
            self.logger.error(f"Failed to delete data: {e}")
            return 0


class BasePage:
    """
    Base page class that coordinates specialized action handlers.
    Provides a clean interface for web automation operations.
    """

    def __init__(self, driver_and_db, database_connection=None):
        # Handle both tuple and individual parameters for backward compatibility
        if isinstance(driver_and_db, tuple):
            driver, database = driver_and_db
        else:
            # Assume it's just the driver, database is from parameter
            driver = driver_and_db
            database = database_connection
            
        # Create logger instance for this page
        self.logger = TestLogger()
        
        # Store references for tests
        self.driver = driver
        self.connection = database
        
        # Initialize specialized action handlers
        self.element_actions = ElementActions(driver, self.logger)
        self.navigation_actions = NavigationActions(driver, self.logger)
        self.screenshot_actions = ScreenshotActions(driver, self.logger)
        self.database_actions = DatabaseActions(database, self.logger)
        
        # Additional aliases for backward compatibility
        self.elements = self.element_actions
        self.navigation = self.navigation_actions  
        self.screenshots = self.screenshot_actions
        self.database = self.database_actions if database else None

        # Keep direct access for backward compatibility
        self.driver = driver
        self.sql = database

    # Public API - delegates to specialized action classes
    def find_element(
        self, locator: Tuple[str, str], timeout: int = None
    ) -> Optional[Any]:
        """Find element - delegates to ElementActions."""
        return self.element_actions.find_element_safely(locator, timeout)

    def click(self, locator: Tuple[str, str], use_js: bool = False) -> bool:
        """Click element - delegates to ElementActions."""
        return self.element_actions.click_element(locator, use_js)

    def send_keys(
        self, locator: Tuple[str, str], text: str, clear_first: bool = True
    ) -> bool:
        """Type text into element."""
        return self.element_actions.type_in_element(locator, text, clear_first)

    def get_text(self, locator: Tuple[str, str]) -> str:
        """Get text - delegates to ElementActions."""
        return self.element_actions.get_element_text(locator)

    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 1) -> bool:
        """Check visibility - delegates to ElementActions."""
        return self.element_actions.is_element_visible(locator, timeout)

    def navigate_to(self, url: str) -> bool:
        """Navigate to URL - delegates to NavigationActions."""
        return self.navigation_actions.navigate_to_url(url)

    def refresh_page(self) -> bool:
        """Refresh page - delegates to NavigationActions."""
        return self.navigation_actions.refresh_current_page()

    def get_title(self) -> str:
        """Get title - delegates to NavigationActions."""
        return self.navigation_actions.get_current_page_title()

    def get_current_url(self) -> str:
        """Get URL - delegates to NavigationActions."""
        return self.navigation_actions.get_current_url()

    def wait_for_page_load(self, timeout: int = None) -> bool:
        """Wait for page load - delegates to NavigationActions."""
        return self.navigation_actions.wait_for_page_load(timeout)

    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot - delegates to ScreenshotActions."""
        return self.screenshot_actions.take_page_screenshot(filename)

    def execute_query(
        self, query: str, parameters: Optional[tuple] = None
    ) -> List[dict]:
        """Execute database query - delegates to DatabaseActions."""
        return self.database_actions.execute_database_query(query, parameters)

    def wait_for_clickable(
        self, locator: Tuple[str, str], timeout: int = None
    ) -> Optional[Any]:
        """Wait for clickable element - delegates to ElementActions."""
        return self.element_actions.wait_for_clickable(locator, timeout)

    def get_element_attribute(
        self, locator: Tuple[str, str], attribute: str, timeout: int = None
    ) -> str:
        """Get element attribute safely."""
        element = self.element_actions.find_element_safely(locator, timeout)
        return element.get_attribute(attribute) if element else ""