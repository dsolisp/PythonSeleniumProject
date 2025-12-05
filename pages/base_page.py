"""
Base Page - Clean implementation of the Page Object Model pattern.
Provides common Selenium operations with practical error handling.
"""

import contextlib
import logging
import time
from pathlib import Path
from typing import Any, Optional

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.error_handler import format_error


class BasePage:
    """
    Base Page for Page Object Model.
    Provides common Selenium operations with error handling.
    """

    def __init__(
        self,
        driver,
        timeout: int = 10,
    ):
        """
        Initialize base page.

        Args:
            driver: WebDriver instance
            timeout: Default wait timeout in seconds
        """
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, timeout)
        self.logger = logging.getLogger(__name__)

    # === ELEMENT INTERACTION METHODS ===

    def find_element(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Find element with optional timeout. Returns None if not found."""
        try:
            if timeout:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
            else:
                element = self.driver.find_element(*locator)
            return element
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.debug("Element not found: %s", format_error(e))
            return None

    def find_elements(self, locator: tuple[str, str]) -> list[Any]:
        """Find multiple elements. Returns empty list if none found."""
        try:
            return self.driver.find_elements(*locator)
        except NoSuchElementException:
            return []

    def wait_for_element(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Wait for element to be visible. Returns element or None on timeout."""
        try:
            return WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return None

    def wait_for_clickable(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Wait for element to be clickable. Returns element or None on timeout."""
        try:
            return WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            return None

    def click(
        self,
        locator: tuple[str, str],
        *,
        timeout: Optional[int] = None,
        scroll_to_element: bool = True,
        force_click: bool = False,
    ) -> bool:
        """Click element with scroll and JS fallback options."""
        try:
            element = self.wait_for_clickable(locator, timeout)
            if not element:
                return False

            if scroll_to_element:
                self.scroll_to_element(locator)

            try:
                element.click()
            except ElementClickInterceptedException:
                if force_click:
                    self.driver.execute_script("arguments[0].click();", element)
                else:
                    raise

            return True

        except (WebDriverException, TimeoutException) as e:
            self.logger.debug("Click failed: %s", format_error(e))
            return False

    def send_keys(
        self,
        locator: tuple[str, str],
        text: str,
        *,
        clear_first: bool = True,
        timeout: Optional[int] = None,
        use_test_data: bool = False,
        data_key: Optional[str] = None,
    ) -> bool:
        """Send keys to element with optional test data lookup and verification."""
        try:
            # Resolve text from test data if requested
            actual_text = text
            if use_test_data and self.test_data_manager:
                test_data = self.test_data_manager.load_test_data(
                    "test_data", self.environment
                )
                actual_text = test_data.get(data_key or text, text)

            element = self.wait_for_element(locator, timeout)
            if not element:
                return False

            # Clear field using multiple fallback strategies
            if clear_first:
                with contextlib.suppress(Exception):
                    self.driver.execute_script("arguments[0].value = '';", element)
                with contextlib.suppress(Exception):
                    element.clear()

            # Send keys with JS fallback for verification
            with contextlib.suppress(Exception):
                element.send_keys(actual_text)

            # Verify and use JS fallback if needed
            entered = element.get_attribute("value") or ""
            if entered != actual_text:
                js = "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                with contextlib.suppress(Exception):
                    self.driver.execute_script(js, element, actual_text)

            return True

        except (WebDriverException, TimeoutException, ValueError):
            return False

    def get_text(self, locator: tuple[str, str], timeout: Optional[int] = None) -> str:
        """Get element text. Returns empty string if not found."""
        element = self.wait_for_element(locator, timeout)
        try:
            return element.text if element else ""
        except WebDriverException:
            return ""

    def get_attribute(
        self, locator: tuple[str, str], attribute: str, timeout: Optional[int] = None
    ) -> str:
        """Get element attribute. Returns empty string if not found."""
        element = self.wait_for_element(locator, timeout)
        try:
            return (element.get_attribute(attribute) or "") if element else ""
        except WebDriverException:
            return ""

    def is_element_visible(self, locator: tuple[str, str], timeout: int = 1) -> bool:
        """Check if element is visible within timeout."""
        return self.wait_for_element(locator, timeout) is not None

    def is_element_present(self, locator: tuple[str, str]) -> bool:
        """Check if element exists in DOM (not necessarily visible)."""
        return self.find_element(locator) is not None

    # === NAVIGATION METHODS ===

    def navigate_to(self, url: str) -> bool:
        """Navigate to URL. Returns True on success."""
        try:
            self.driver.get(url)
            return True
        except WebDriverException:
            return False

    def refresh_page(self) -> bool:
        """Refresh current page. Returns True on success."""
        try:
            self.driver.refresh()
            return True
        except WebDriverException:
            return False

    def get_current_url(self) -> str:
        """Get current page URL."""
        try:
            return self.driver.current_url
        except WebDriverException:
            return ""

    def get_title(self, timeout: Optional[int] = None) -> str:
        """Get page title, optionally waiting for non-empty title."""
        try:
            if timeout:
                WebDriverWait(self.driver, timeout).until(lambda d: d.title != "")
            return self.driver.title
        except (TimeoutException, WebDriverException):
            return ""

    def go_back(self) -> bool:
        """Navigate back in browser history."""
        try:
            self.driver.back()
            return True
        except WebDriverException:
            return False

    def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        try:
            self.driver.forward()
            return True
        except WebDriverException:
            return False

    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
        """Wait for document.readyState to be 'complete'."""
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False

    # === UTILITY METHODS ===

    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take screenshot. Returns filepath or empty string on failure."""
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            filepath = Path(filename)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except (WebDriverException, OSError):
            return ""

    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript. Returns result or None on error."""
        try:
            return self.driver.execute_script(script, *args)
        except WebDriverException:
            return None

    def scroll_to_element(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> bool:
        """Scroll element into view using ActionChains."""
        element = self.wait_for_element(locator, timeout)
        if not element:
            return False
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            return True
        except WebDriverException:
            return False
