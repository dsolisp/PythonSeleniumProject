"""
Base Page - Clean implementation of the Page Object Model pattern.
Provides common Selenium operations with practical error handling.
"""

import contextlib
import logging
import time
from pathlib import Path

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

# Timeout constants - centralized for consistency
TIMEOUT_DEFAULT = 20  # Standard operations (element visibility, clicks, etc.)
TIMEOUT_SLOW = 45  # Slow-loading elements (page loads, complex operations)


class BasePage:
    """
    Base Page for Page Object Model.
    Provides common Selenium operations with error handling.
    """

    def __init__(self, driver):
        """Initialize base page with WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(self.driver, TIMEOUT_DEFAULT)
        self.logger = logging.getLogger(__name__)

    # === ELEMENT INTERACTION METHODS ===

    def find_element(self, locator):
        """Find element immediately. Returns WebElement or None."""
        try:
            return self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException) as e:
            self.logger.debug("Element not found: %s", format_error(e))
            return None

    def find_elements(self, locator):
        """Find multiple elements. Returns list of WebElements or empty list."""
        try:
            return self.driver.find_elements(*locator)
        except NoSuchElementException:
            return []

    def wait_for_element(self, locator):
        """Wait for element to be visible. Returns WebElement or None."""
        try:
            return WebDriverWait(self.driver, TIMEOUT_DEFAULT).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return None

    def wait_for_element_slow(self, locator):
        """Wait for slow-loading element. Returns WebElement or None."""
        try:
            return WebDriverWait(self.driver, TIMEOUT_SLOW).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return None

    def wait_for_clickable(self, locator):
        """Wait for element to be clickable. Returns WebElement or None."""
        try:
            return WebDriverWait(self.driver, TIMEOUT_DEFAULT).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            return None

    def click(self, locator, *, scroll_to_element=True, force_click=False):
        """Click element. Returns True on success, False on failure."""
        try:
            element = self.wait_for_clickable(locator)
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

    def send_keys(self, locator, text, *, clear_first=True):
        """Send keys to element. Returns True on success, False on failure."""
        try:
            element = self.wait_for_element(locator)
            if not element:
                return False

            if clear_first:
                with contextlib.suppress(Exception):
                    self.driver.execute_script("arguments[0].value = '';", element)
                with contextlib.suppress(Exception):
                    element.clear()

            with contextlib.suppress(Exception):
                element.send_keys(text)

            # Verify and use JS fallback if needed
            entered = element.get_attribute("value") or ""
            if entered != text:
                js = "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
                with contextlib.suppress(Exception):
                    self.driver.execute_script(js, element, text)

            return True

        except (WebDriverException, TimeoutException, ValueError):
            return False

    def get_text(self, locator):
        """Get element text. Returns text string or empty string."""
        element = self.wait_for_element(locator)
        try:
            return element.text if element else ""
        except WebDriverException:
            return ""

    def get_attribute(self, locator, attribute):
        """Get element attribute value. Returns string or empty string."""
        element = self.wait_for_element(locator)
        try:
            return (element.get_attribute(attribute) or "") if element else ""
        except WebDriverException:
            return ""

    def is_element_visible(self, locator):
        """Check if element is visible. Returns True or False."""
        try:
            return (
                WebDriverWait(self.driver, 2).until(
                    EC.visibility_of_element_located(locator)
                )
                is not None
            )
        except TimeoutException:
            return False

    def is_element_present(self, locator):
        """Check if element exists in DOM. Returns True or False."""
        return self.find_element(locator) is not None

    # === NAVIGATION METHODS ===

    def navigate_to(self, url):
        """Navigate to URL. Returns True on success."""
        try:
            self.driver.get(url)
            return True
        except WebDriverException:
            return False

    def refresh_page(self):
        """Refresh current page. Returns True on success."""
        try:
            self.driver.refresh()
            return True
        except WebDriverException:
            return False

    def get_current_url(self):
        """Get current page URL. Returns URL string or empty string."""
        try:
            return self.driver.current_url
        except WebDriverException:
            return ""

    def get_title(self):
        """Get page title. Returns title string or empty string."""
        try:
            return self.driver.title
        except WebDriverException:
            return ""

    def go_back(self):
        """Navigate back in browser history. Returns True on success."""
        try:
            self.driver.back()
            return True
        except WebDriverException:
            return False

    def go_forward(self):
        """Navigate forward in browser history. Returns True on success."""
        try:
            self.driver.forward()
            return True
        except WebDriverException:
            return False

    def wait_for_page_load(self):
        """Wait for page to fully load. Returns True on success."""
        try:
            WebDriverWait(self.driver, TIMEOUT_SLOW).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False

    # === UTILITY METHODS ===

    def take_screenshot(self, filename=None):
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

    def execute_script(self, script, *args):
        """Execute JavaScript. Returns result or None on error."""
        try:
            return self.driver.execute_script(script, *args)
        except WebDriverException:
            return None

    def scroll_to_element(self, locator):
        """Scroll element into view. Returns True on success."""
        element = self.wait_for_element(locator)
        if not element:
            return False
        try:
            ActionChains(self.driver).move_to_element(element).perform()
            return True
        except WebDriverException:
            return False
