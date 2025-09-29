"""
Solid Base Page - Clean, Practical, and Maintainable
A well-designed base page class for Selenium automation that provides
essential functionality without over-engineering.
"""

from typing import Any, List, Optional, Tuple
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class BasePage:
    """
    Solid base page class that provides essential functionality for page objects.
    
    Design principles:
    - Simple and focused
    - Easy to understand and maintain  
    - Provides common patterns without over-engineering
    - Graceful error handling
    - Flexible timeout management
    """

    def __init__(self, driver: webdriver.Chrome, database=None, timeout: int = 10):
        """
        Initialize base page with driver and optional database connection.
        
        Args:
            driver: Selenium WebDriver instance or tuple (driver, database)
            database: Optional database connection
            timeout: Default timeout for waits (seconds)
        """
        # Handle both new style (driver, database) and legacy tuple format
        if isinstance(driver, tuple):
            self.driver = driver[0]
            self.database = driver[1] if len(driver) > 1 else database
        else:
            self.driver = driver
            self.database = database
            
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, timeout)
        
    # === ELEMENT INTERACTION METHODS ===
    
    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """
        Find element with optional timeout.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds
            
        Returns:
            WebElement if found, None if not found
        """
        try:
            if timeout:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
            else:
                element = self.driver.find_element(*locator)
            return element
        except (TimeoutException, NoSuchElementException):
            return None
    
    def find_elements(self, locator: Tuple[str, str]) -> List[Any]:
        """
        Find multiple elements.
        
        Args:
            locator: Tuple of (By method, selector)
            
        Returns:
            List of WebElements (empty list if none found)
        """
        try:
            return self.driver.find_elements(*locator)
        except NoSuchElementException:
            return []
    
    def wait_for_element(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """
        Wait for element to be visible.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds (uses default if None)
            
        Returns:
            WebElement if found and visible, None if timeout
        """
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return None
    
    def wait_for_clickable(self, locator: Tuple[str, str], timeout: int = None) -> Optional[Any]:
        """
        Wait for element to be clickable.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds
            
        Returns:
            WebElement if clickable, None if timeout
        """
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            return None
    
    def click(self, locator: Tuple[str, str], timeout: int = None) -> bool:
        """
        Click element with wait.
        
        Args:
            locator: Tuple of (By method, selector)  
            timeout: Wait timeout in seconds
            
        Returns:
            True if clicked successfully, False otherwise
        """
        element = self.wait_for_clickable(locator, timeout)
        if element:
            try:
                element.click()
                return True
            except WebDriverException:
                return False
        return False
    
    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: int = None) -> bool:
        """
        Send keys to element.
        
        Args:
            locator: Tuple of (By method, selector)
            text: Text to type
            clear_first: Whether to clear field first
            timeout: Wait timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        element = self.wait_for_element(locator, timeout)
        if element:
            try:
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            except WebDriverException:
                return False
        return False
    
    def get_text(self, locator: Tuple[str, str], timeout: int = None) -> str:
        """
        Get element text.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds
            
        Returns:
            Element text or empty string if not found
        """
        element = self.wait_for_element(locator, timeout)
        if element:
            try:
                return element.text
            except WebDriverException:
                return ""
        return ""
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: int = None) -> str:
        """
        Get element attribute.
        
        Args:
            locator: Tuple of (By method, selector)
            attribute: Attribute name
            timeout: Wait timeout in seconds
            
        Returns:
            Attribute value or empty string if not found
        """
        element = self.wait_for_element(locator, timeout)
        if element:
            try:
                return element.get_attribute(attribute) or ""
            except WebDriverException:
                return ""
        return ""
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 1) -> bool:
        """
        Check if element is visible.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds (short default)
            
        Returns:
            True if visible, False otherwise
        """
        return self.wait_for_element(locator, timeout) is not None
    
    def is_element_present(self, locator: Tuple[str, str]) -> bool:
        """
        Check if element is present in DOM (not necessarily visible).
        
        Args:
            locator: Tuple of (By method, selector)
            
        Returns:
            True if present, False otherwise
        """
        return self.find_element(locator) is not None
    
    # === NAVIGATION METHODS ===
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.get(url)
            return True
        except WebDriverException:
            return False
    
    def refresh_page(self) -> bool:
        """
        Refresh current page.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.refresh()
            return True
        except WebDriverException:
            return False
    
    def get_current_url(self) -> str:
        """
        Get current page URL.
        
        Returns:
            Current URL or empty string if error
        """
        try:
            return self.driver.current_url
        except WebDriverException:
            return ""
    
    def get_title(self, timeout: int = None) -> str:
        """
        Get page title with optional wait for non-empty title.
        
        Args:
            timeout: Wait timeout in seconds
            
        Returns:
            Page title or empty string if error/timeout
        """
        try:
            if timeout:
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: driver.title != ""
                )
            return self.driver.title
        except (TimeoutException, WebDriverException):
            return ""
    
    def go_back(self) -> bool:
        """
        Go back in browser history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.back()
            return True
        except WebDriverException:
            return False
    
    def go_forward(self) -> bool:
        """
        Go forward in browser history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.forward()
            return True
        except WebDriverException:
            return False
    
    def wait_for_page_load(self, timeout: int = None) -> bool:
        """
        Wait for page to load (document ready state).
        
        Args:
            timeout: Wait timeout in seconds
            
        Returns:
            True if page loaded, False if timeout
        """
        wait_time = timeout or self.timeout
        try:
            WebDriverWait(self.driver, wait_time).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except TimeoutException:
            return False
    
    # === UTILITY METHODS ===
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        Take screenshot of current page.
        
        Args:
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved screenshot or empty string if failed
        """
        try:
            import os
            import time
            
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            screenshot_dir = "screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception:
            return ""
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript on the page.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to script
            
        Returns:
            Script return value or None if error
        """
        try:
            return self.driver.execute_script(script, *args)
        except WebDriverException:
            return None
    
    def scroll_to_element(self, locator: Tuple[str, str], timeout: int = None) -> bool:
        """
        Scroll element into view.
        
        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        element = self.wait_for_element(locator, timeout)
        if element:
            try:
                ActionChains(self.driver).move_to_element(element).perform()
                return True
            except WebDriverException:
                return False
        return False
    
    # === DATABASE METHODS (if database connection provided) ===
    
    def execute_query(self, query: str, parameters: tuple = None) -> List[dict]:
        """
        Execute database query if database connection available.
        
        Args:
            query: SQL query string
            parameters: Query parameters tuple
            
        Returns:
            List of result dictionaries or empty list if no database/error
        """
        if not self.database:
            return []
        
        try:
            # Import here to avoid dependency if not using database features
            from utils.sql_connection import execute_query, fetch_all
            
            cursor = execute_query(self.database, query, parameters)
            if cursor:
                return fetch_all(cursor) or []
        except Exception:
            pass
        
        return []