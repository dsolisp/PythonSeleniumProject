"""
Enhanced Base Page with comprehensive functionality,
error handling, and modern Selenium practices.
"""

import time
from typing import List, Optional, Dict, Any, Tuple, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException
)
from pathlib import Path
import json

from config.settings import settings
from utils.logger import test_logger
from utils.sql_connection_enhanced import DatabaseManager


class BasePage:
    """Enhanced base page with comprehensive functionality and error handling."""
    
    def __init__(self, driver_tuple: Tuple[webdriver.Remote, DatabaseManager]):
        """
        Initialize the base page.
        
        Args:
            driver_tuple: Tuple containing (webdriver, database_manager)
        """
        self.driver = driver_tuple[0]
        self.db_manager = driver_tuple[1]
        self.wait = WebDriverWait(self.driver, settings.explicit_wait)
        self.actions = ActionChains(self.driver)
        
    # Element Finding Methods
    
    def find_element(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None,
        retry_count: int = 3
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        Find a single element with retry logic.
        
        Args:
            locator: Tuple of (By strategy, locator value)
            timeout: Custom timeout (uses default if None)
            retry_count: Number of retries for stale element exceptions
            
        Returns:
            WebElement or None if not found
        """
        timeout = timeout or settings.explicit_wait
        
        for attempt in range(retry_count):
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                return element
                
            except StaleElementReferenceException:
                if attempt < retry_count - 1:
                    test_logger.logger.warning(f"Stale element, retrying... (attempt {attempt + 1})")
                    time.sleep(0.5)
                    continue
                else:
                    raise
            except TimeoutException:
                test_logger.logger.warning(f"Element not found: {locator}")
                return None
            except Exception as e:
                test_logger.log_error(e, {
                    "locator": str(locator),
                    "operation": "find_element"
                })
                return None
    
    def find_elements(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None
    ) -> List[webdriver.remote.webelement.WebElement]:
        """
        Find multiple elements.
        
        Args:
            locator: Tuple of (By strategy, locator value)
            timeout: Custom timeout (uses default if None)
            
        Returns:
            List of WebElements
        """
        timeout = timeout or settings.explicit_wait
        
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            test_logger.logger.warning(f"Elements not found: {locator}")
            return []
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "find_elements"
            })
            return []
    
    # Wait Methods
    
    def wait_for_element_visible(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for element to be visible."""
        timeout = timeout or settings.explicit_wait
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            test_logger.logger.warning(f"Element not visible: {locator}")
            return None
    
    def wait_for_element_clickable(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for element to be clickable."""
        timeout = timeout or settings.explicit_wait
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            test_logger.logger.warning(f"Element not clickable: {locator}")
            return None
    
    def wait_for_element_invisible(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None
    ) -> bool:
        """Wait for element to become invisible."""
        timeout = timeout or settings.explicit_wait
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
        except TimeoutException:
            return False
    
    def wait_for_text_in_element(
        self, 
        locator: Tuple[By, str], 
        text: str, 
        timeout: int = None
    ) -> bool:
        """Wait for specific text to appear in element."""
        timeout = timeout or settings.explicit_wait
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
        except TimeoutException:
            return False
    
    def wait_for_url_contains(self, url_fragment: str, timeout: int = None) -> bool:
        """Wait for URL to contain specific text."""
        timeout = timeout or settings.explicit_wait
        
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.url_contains(url_fragment)
            )
        except TimeoutException:
            return False
    
    # Interaction Methods
    
    def click(
        self, 
        locator: Tuple[By, str], 
        timeout: int = None,
        use_js: bool = False
    ) -> bool:
        """
        Click an element with enhanced error handling.
        
        Args:
            locator: Element locator
            timeout: Custom timeout
            use_js: Use JavaScript click if regular click fails
            
        Returns:
            True if successful, False otherwise
        """
        element = self.wait_for_element_clickable(locator, timeout)
        if not element:
            return False
        
        try:
            if use_js:
                self.driver.execute_script("arguments[0].click();", element)
            else:
                element.click()
            
            test_logger.log_step(f"Clicked element: {locator}")
            return True
            
        except ElementNotInteractableException:
            if not use_js:
                # Retry with JavaScript click
                return self.click(locator, timeout, use_js=True)
            else:
                test_logger.log_error(
                    Exception("Element not interactable"),
                    {"locator": str(locator), "operation": "click"}
                )
                return False
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "click"
            })
            return False
    
    def send_keys(
        self, 
        locator: Tuple[By, str], 
        text: str, 
        clear_first: bool = True,
        timeout: int = None
    ) -> bool:
        """
        Send keys to an element.
        
        Args:
            locator: Element locator
            text: Text to send
            clear_first: Clear element before typing
            timeout: Custom timeout
            
        Returns:
            True if successful, False otherwise
        """
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return False
        
        try:
            if clear_first:
                element.clear()
            element.send_keys(text)
            
            test_logger.log_step(f"Sent keys to element: {locator}", {"text": "***" if "password" in str(locator).lower() else text})
            return True
            
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "send_keys"
            })
            return False
    
    def get_text(self, locator: Tuple[By, str], timeout: int = None) -> Optional[str]:
        """Get text from an element."""
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return None
        
        try:
            text = element.text.strip()
            test_logger.log_step(f"Got text from element: {locator}", {"text": text})
            return text
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "get_text"
            })
            return None
    
    def get_attribute(
        self, 
        locator: Tuple[By, str], 
        attribute: str, 
        timeout: int = None
    ) -> Optional[str]:
        """Get attribute value from an element."""
        element = self.find_element(locator, timeout)
        if not element:
            return None
        
        try:
            value = element.get_attribute(attribute)
            test_logger.log_step(f"Got attribute '{attribute}' from element: {locator}", {"value": value})
            return value
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "attribute": attribute,
                "operation": "get_attribute"
            })
            return None
    
    def select_dropdown_by_text(
        self, 
        locator: Tuple[By, str], 
        text: str, 
        timeout: int = None
    ) -> bool:
        """Select dropdown option by visible text."""
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return False
        
        try:
            select = Select(element)
            select.select_by_visible_text(text)
            test_logger.log_step(f"Selected dropdown option: {text}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "text": text,
                "operation": "select_dropdown_by_text"
            })
            return False
    
    def select_dropdown_by_value(
        self, 
        locator: Tuple[By, str], 
        value: str, 
        timeout: int = None
    ) -> bool:
        """Select dropdown option by value."""
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return False
        
        try:
            select = Select(element)
            select.select_by_value(value)
            test_logger.log_step(f"Selected dropdown value: {value}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "value": value,
                "operation": "select_dropdown_by_value"
            })
            return False
    
    # Advanced Interaction Methods
    
    def hover_over_element(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Hover over an element."""
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return False
        
        try:
            self.actions.move_to_element(element).perform()
            test_logger.log_step(f"Hovered over element: {locator}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "hover_over_element"
            })
            return False
    
    def double_click(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Double click an element."""
        element = self.wait_for_element_clickable(locator, timeout)
        if not element:
            return False
        
        try:
            self.actions.double_click(element).perform()
            test_logger.log_step(f"Double clicked element: {locator}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "double_click"
            })
            return False
    
    def right_click(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Right click an element."""
        element = self.wait_for_element_clickable(locator, timeout)
        if not element:
            return False
        
        try:
            self.actions.context_click(element).perform()
            test_logger.log_step(f"Right clicked element: {locator}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "right_click"
            })
            return False
    
    def drag_and_drop(
        self, 
        source_locator: Tuple[By, str], 
        target_locator: Tuple[By, str], 
        timeout: int = None
    ) -> bool:
        """Drag and drop from source to target element."""
        source = self.wait_for_element_visible(source_locator, timeout)
        target = self.wait_for_element_visible(target_locator, timeout)
        
        if not source or not target:
            return False
        
        try:
            self.actions.drag_and_drop(source, target).perform()
            test_logger.log_step(f"Dragged from {source_locator} to {target_locator}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "source_locator": str(source_locator),
                "target_locator": str(target_locator),
                "operation": "drag_and_drop"
            })
            return False
    
    # Page Navigation Methods
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to a URL."""
        try:
            self.driver.get(url)
            test_logger.log_step(f"Navigated to: {url}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "url": url,
                "operation": "navigate_to"
            })
            return False
    
    def refresh_page(self) -> bool:
        """Refresh the current page."""
        try:
            self.driver.refresh()
            test_logger.log_step("Page refreshed")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "refresh_page"})
            return False
    
    def go_back(self) -> bool:
        """Navigate back in browser history."""
        try:
            self.driver.back()
            test_logger.log_step("Navigated back")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "go_back"})
            return False
    
    def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        try:
            self.driver.forward()
            test_logger.log_step("Navigated forward")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "go_forward"})
            return False
    
    # Page Information Methods
    
    def get_title(self, timeout: int = None) -> Optional[str]:
        """Get the page title with timeout."""
        timeout = timeout or settings.explicit_wait
        
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.title != ""
            )
            title = self.driver.title
            test_logger.log_step("Got page title", {"title": title})
            return title
        except TimeoutException:
            test_logger.logger.warning("Page title not available within timeout")
            return None
        except Exception as e:
            test_logger.log_error(e, {"operation": "get_title"})
            return None
    
    def get_current_url(self) -> str:
        """Get the current URL."""
        try:
            url = self.driver.current_url
            test_logger.log_step("Got current URL", {"url": url})
            return url
        except Exception as e:
            test_logger.log_error(e, {"operation": "get_current_url"})
            return ""
    
    def get_page_source(self) -> str:
        """Get the page source."""
        try:
            return self.driver.page_source
        except Exception as e:
            test_logger.log_error(e, {"operation": "get_page_source"})
            return ""
    
    # Screenshot Methods
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """
        Take a screenshot of the current page.
        
        Args:
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to screenshot file or None if failed
        """
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = settings.screenshots_dir / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.driver.save_screenshot(str(screenshot_path))
            test_logger.log_screenshot(str(screenshot_path), "page_screenshot")
            
            return str(screenshot_path)
            
        except Exception as e:
            test_logger.log_error(e, {"operation": "take_screenshot"})
            return None
    
    def take_element_screenshot(
        self, 
        locator: Tuple[By, str], 
        filename: str = None,
        timeout: int = None
    ) -> Optional[str]:
        """
        Take a screenshot of a specific element.
        
        Args:
            locator: Element locator
            filename: Optional filename, auto-generated if None
            timeout: Custom timeout
            
        Returns:
            Path to screenshot file or None if failed
        """
        element = self.wait_for_element_visible(locator, timeout)
        if not element:
            return None
        
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"element_screenshot_{timestamp}.png"
            
            screenshot_path = settings.screenshots_dir / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            element.screenshot(str(screenshot_path))
            test_logger.log_screenshot(str(screenshot_path), "element_screenshot")
            
            return str(screenshot_path)
            
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "take_element_screenshot"
            })
            return None
    
    # JavaScript Execution Methods
    
    def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript in the browser."""
        try:
            result = self.driver.execute_script(script, *args)
            test_logger.log_step("Executed JavaScript", {"script": script[:100] + "..." if len(script) > 100 else script})
            return result
        except Exception as e:
            test_logger.log_error(e, {
                "script": script,
                "operation": "execute_script"
            })
            return None
    
    def scroll_to_element(self, locator: Tuple[By, str], timeout: int = None) -> bool:
        """Scroll to an element."""
        element = self.find_element(locator, timeout)
        if not element:
            return False
        
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            test_logger.log_step(f"Scrolled to element: {locator}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "locator": str(locator),
                "operation": "scroll_to_element"
            })
            return False
    
    def scroll_to_top(self) -> bool:
        """Scroll to the top of the page."""
        try:
            self.driver.execute_script("window.scrollTo(0, 0);")
            test_logger.log_step("Scrolled to top of page")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "scroll_to_top"})
            return False
    
    def scroll_to_bottom(self) -> bool:
        """Scroll to the bottom of the page."""
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            test_logger.log_step("Scrolled to bottom of page")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "scroll_to_bottom"})
            return False
    
    # Utility Methods
    
    def is_element_present(self, locator: Tuple[By, str], timeout: int = 1) -> bool:
        """Check if element is present in DOM."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator: Tuple[By, str], timeout: int = 1) -> bool:
        """Check if element is visible."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(self, locator: Tuple[By, str], timeout: int = 1) -> bool:
        """Check if element is clickable."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def get_window_handles(self) -> List[str]:
        """Get all window handles."""
        return self.driver.window_handles
    
    def switch_to_window(self, window_handle: str) -> bool:
        """Switch to a specific window."""
        try:
            self.driver.switch_to.window(window_handle)
            test_logger.log_step(f"Switched to window: {window_handle}")
            return True
        except Exception as e:
            test_logger.log_error(e, {
                "window_handle": window_handle,
                "operation": "switch_to_window"
            })
            return False
    
    def close_current_window(self) -> bool:
        """Close the current window."""
        try:
            self.driver.close()
            test_logger.log_step("Closed current window")
            return True
        except Exception as e:
            test_logger.log_error(e, {"operation": "close_current_window"})
            return False