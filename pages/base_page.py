"""
Base page class for web automation with specialized action handlers.
"""

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
from utils.logger import logger


class ElementActions:
    """
    Handles all element interactions and operations.
    """

    def __init__(self, driver: webdriver.Chrome, timeout: int = None):
        self.driver = driver
        self.timeout = timeout or settings.TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)
        self.actions = ActionChains(driver)

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
        logger.debug(
            f"Clicking element: {locator[1]} {'(JS)' if use_javascript else ''}"
        )
        element = self.wait_for_clickable(locator)
        if not element:
            logger.warning(f"Element not clickable: {locator[1]}")
            return False

        try:
            if use_javascript:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            logger.debug(f"Successfully clicked: {locator[1]}")
            return True
        except ElementNotInteractableException:
            if not use_javascript:
                logger.debug(f"Fallback to JS click for: {locator[1]}")
                return self.click_element(locator, use_javascript=True)
            logger.error(f"Failed to click element: {locator[1]}")
            return False

    def type_in_element(
        self, locator: Tuple[str, str], text: str, clear_first: bool = True
    ) -> bool:
        """Type text in element with error handling."""
        element = self.find_element_safely(locator)
        if not element:
            return False

        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            return True
        except Exception:
            return False

    def get_element_text(self, locator: Tuple[str, str]) -> str:
        """Get text from element safely."""
        element = self.find_element_safely(locator)
        return element.text.strip() if element else ""

    def wait_for_clickable(
        self, locator: Tuple[str, str], timeout: int = None
    ) -> Optional[Any]:
        """Wait for element to be clickable."""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            return None

    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 1) -> bool:
        """Check if element is visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False


class NavigationActions:
    """
    Handles page navigation operations.
    """

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def navigate_to_url(self, url: str) -> bool:
        """Navigate to URL safely."""
        logger.info(f"Navigating to: {url}")
        try:
            self.driver.get(url)
            logger.debug(f"Successfully navigated to: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
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
        try:
            return self.driver.title
        except Exception:
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
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            return True
        except TimeoutException:
            logger.warning(f"Page load timeout after {timeout}s")
            return False
        except Exception as e:
            logger.error(f"Error waiting for page load: {str(e)}")
            return False


class ScreenshotActions:
    """
    Handles screenshot capture operations.
    """

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def take_page_screenshot(self, filename: str = None) -> str:
        """Take screenshot with automatic naming."""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"

            screenshot_path = settings.SCREENSHOTS_DIR / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)

            self.driver.save_screenshot(str(screenshot_path))
            logger.screenshot(str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return ""


class DatabaseActions:
    """
    Handles database query operations.
    """

    def __init__(self, database_connection: Optional[object]):
        self.db_connection = database_connection

    def execute_database_query(
        self, query: str, parameters: Optional[tuple] = None
    ) -> List[dict]:
        """Execute database query safely."""
        if not self.db_connection:
            return []

        try:
            # This would need to be implemented based on your specific SQL utility
            # For now, returning empty list as placeholder
            return []
        except Exception:
            return []


class BasePage:
    """
    Base page class that coordinates specialized action handlers.
    Provides a clean interface for web automation operations.
    """

    def __init__(self, driver_and_db: Tuple[webdriver.Chrome, Optional[object]]):
        driver, database = driver_and_db

        # Initialize specialized action handlers
        self.element_actions = ElementActions(driver)
        self.navigation_actions = NavigationActions(driver)
        self.screenshot_actions = ScreenshotActions(driver)
        self.database_actions = DatabaseActions(database)

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
        """Execute DB query - delegates to DatabaseActions."""
        return self.database_actions.execute_database_query(query, parameters)

    # Convenience methods for common patterns
    def wait_for_element_clickable(
        self, locator: Tuple[str, str], timeout: int = None
    ) -> Optional[Any]:
        """Wait for clickable element."""
        return self.element_actions.wait_for_clickable(locator, timeout)

    def is_element_present(self, locator: Tuple[str, str], timeout: int = 1) -> bool:
        """Check if element exists in DOM."""
        element = self.element_actions.find_element_safely(locator, timeout)
        return element is not None
