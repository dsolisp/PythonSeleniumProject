"""
Enhanced Base Page with comprehensive functionality and error handling.
"""

import time
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    StaleElementReferenceException
)
from pathlib import Path
from config.simple_settings import settings


class BasePage:
    """Enhanced base page with comprehensive functionality and error handling."""
    
    def __init__(self, driver):
        self.driver = driver[0]
        self.sql = driver[1]
        self.wait = WebDriverWait(self.driver, settings.TIMEOUT)
        self.actions = ActionChains(self.driver)
    
    # Enhanced element finding methods
    def find_element(self, locator, timeout=None, retry_count=3):
        """Find a single element with retry logic."""
        timeout = timeout or settings.TIMEOUT
        
        for attempt in range(retry_count):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
                
            except StaleElementReferenceException:
                if attempt < retry_count - 1:
                    print(f"Stale element, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5)
                    continue
                else:
                    raise
            except TimeoutException:
                print(f"Element not found: {locator}")
                return None
    
    def find_elements(self, locator, timeout=None):
        """Find multiple elements."""
        timeout = timeout or settings.TIMEOUT
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            print(f"Elements not found: {locator}")
            return []
    
    # Original methods with enhancements
    def wait_for_element(self, locator, timeout=None):
        """Wait for element to be visible (enhanced original method)."""
        timeout = timeout or settings.TIMEOUT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            print(f"Element not visible: {locator}")
            return None

    def refresh_page(self):
        """Refresh the current page (enhanced original method)."""
        try:
            self.driver.refresh()
            print("Page refreshed successfully")
            return True
        except Exception as e:
            print(f"Error refreshing page: {e}")
            return False

    def get_title(self, timeout=None):
        """Get the page title with timeout (enhanced original method)."""
        timeout = timeout or settings.TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.title != "")
            title = self.driver.title
            print(f"Page title: {title}")
            return title
        except TimeoutException:
            print("Page title not available within timeout")
            return False
    
    # New enhanced methods
    def click(self, locator, timeout=None, use_js=False):
        """Click an element with enhanced error handling."""
        element = self.wait_for_element_clickable(locator, timeout)
        if not element:
            return False
        
        try:
            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            print(f"Clicked element: {locator}")
            return True
            
        except ElementNotInteractableException:
            if not use_js:
                return self.click(locator, timeout, use_js=True)
            else:
                print(f"Element not interactable: {locator}")
                return False
    
    def send_keys(self, locator, text, clear_first=True, timeout=None):
        """Send keys to an element."""
        element = self.wait_for_element(locator, timeout)
        if not element:
            return False
        
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            print(f"Sent keys to element: {locator}")
            return True
        except Exception as e:
            print(f"Error sending keys: {e}")
            return False
    
    def get_text(self, locator, timeout=None):
        """Get text from an element."""
        element = self.wait_for_element(locator, timeout)
        if not element:
            return None
        
        try:
            text = element.text.strip()
            print(f"Got text from element: {text}")
            return text
        except Exception as e:
            print(f"Error getting text: {e}")
            return None
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """Wait for element to be clickable."""
        timeout = timeout or settings.TIMEOUT
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            print(f"Element not clickable: {locator}")
            return None
    
    def take_screenshot(self, filename=None):
        """Take a screenshot of the current page."""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = settings.SCREENSHOTS_DIR / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.driver.save_screenshot(str(screenshot_path))
            print(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return None
    
    def scroll_to_element(self, locator, timeout=None):
        """Scroll to an element."""
        element = self.find_element(locator, timeout)
        if not element:
            return False
        
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            print(f"Scrolled to element: {locator}")
            return True
        except Exception as e:
            print(f"Error scrolling to element: {e}")
            return False
    
    def is_element_present(self, locator, timeout=1):
        """Check if element is present in DOM."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator, timeout=1):
        """Check if element is visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_page_load(self, timeout=None):
        """
        Wait for page to fully load by checking document ready state.
        
        Args:
            timeout (int, optional): Maximum time to wait. Defaults to settings.TIMEOUT.
            
        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        timeout = timeout or settings.TIMEOUT
        
        try:
            # Wait for document ready state to be complete
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait for any dynamic content
            time.sleep(0.5)
            
            print("✅ Page loaded successfully")
            return True
            
        except TimeoutException:
            print(f"⚠️ Page load timeout after {timeout} seconds")
            return False
        except Exception as e:
            print(f"❌ Error waiting for page load: {str(e)}")
            return False