"""
Advanced Base Page - Clean, Practical, and Maintainable
A well-designed base page class for Selenium automation that provides
essential functionality with intelligent error handling, performance monitoring,
and test data integration.
"""

import contextlib
import json
import statistics
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.sql_connection import execute_query, fetch_all

# Import advanced features
try:
    from utils.error_handler import SmartErrorHandler
    from utils.test_data_manager import TestDataManager
    from utils.test_reporter import AdvancedTestReporter

    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    # Graceful fallback if advanced features not installed
    ADVANCED_FEATURES_AVAILABLE = False
    SmartErrorHandler = None
    TestDataManager = None
    AdvancedTestReporter = None

from typing import Optional, Union


class BasePage:
    """
    Base Page for Page Object Model
    Provides common functionality for all page objects with advanced
    features. Integrates YAML configuration, tenacity retry mechanisms,
    and performance monitoring.
    """

    def __init__(
        self,
        driver,
        database=None,
        timeout: int = 10,
        test_name: Optional[str] = None,
        environment: str = "test",
    ):
        """
        Initialize base page with optional advanced features.

        Args:
            driver: Selenium WebDriver instance or tuple (driver, database)
            database: Optional database connection
            timeout: Default timeout for waits (seconds)
            test_name: Current test name for reporting and analytics
            environment: Test environment (local, dev, qa, prod)
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
        self.test_name = test_name or "unknown_test"
        self.environment = environment

        # Initialize advanced features if available
        if ADVANCED_FEATURES_AVAILABLE:
            self.error_handler = SmartErrorHandler()
            self.test_data_manager = TestDataManager()
            self.test_reporter = AdvancedTestReporter()

            # Performance tracking
            self.action_start_time = None
            self.performance_metrics = {}

            # Element interaction history
            self.interaction_history: list[dict[str, Any]] = []
        else:
            self.error_handler = None
            self.test_data_manager = None
            self.test_reporter = None
            self.performance_metrics = {}
            self.interaction_history = []

    # === ELEMENT INTERACTION METHODS ===

    def find_element(
        self,
        locator: tuple[str, str],
        timeout: Optional[int] = None,
    ) -> Optional[Any]:
        """
        Find element with optional timeout and enhanced error handling.

        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds

        Returns:
            WebElement if found, None if not found
        """
        if ADVANCED_FEATURES_AVAILABLE:
            self._start_performance_tracking("find_element")

        try:
            if timeout:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator),
                )
            else:
                element = self.driver.find_element(*locator)
        except (TimeoutException, NoSuchElementException) as e:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction("find_element", locator, "FAILED", str(e))
                self._end_performance_tracking("find_element")

                # Try error recovery
                if self.error_handler and self.error_handler.handle_error(
                    e,
                    self.driver,
                    self.test_name,
                ):
                    # Retry after recovery
                    return self.find_element(locator, timeout)

            return None
        else:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction("find_element", locator, "SUCCESS")
                self._end_performance_tracking("find_element")

            return element

    def find_elements(self, locator: tuple[str, str]) -> list[Any]:
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

    def wait_for_element(
        self,
        locator: tuple[str, str],
        timeout: Optional[int] = None,
    ) -> Optional[Any]:
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
                EC.visibility_of_element_located(locator),
            )
        except TimeoutException:
            return None

    def wait_for_clickable(
        self,
        locator: tuple[str, str],
        timeout: Optional[int] = None,
    ) -> Optional[Any]:
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
                EC.element_to_be_clickable(locator),
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
        """
        Click element with enhanced features and error recovery.

        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds
            scroll_to_element: Whether to scroll element into view
            force_click: Use JavaScript click if normal click fails

        Returns:
            True if clicked successfully, False otherwise
        """
        if ADVANCED_FEATURES_AVAILABLE:
            self._start_performance_tracking("click")

        try:
            element = self.wait_for_clickable(locator, timeout)
            if element:
                # Scroll to element if requested
                if scroll_to_element:
                    self.scroll_to_element(locator)

                # Wait for any overlays to disappear
                time.sleep(0.5)

                try:
                    element.click()
                except ElementClickInterceptedException:
                    if force_click:
                        # Use JavaScript click as fallback
                        self.driver.execute_script("arguments[0].click();", element)
                        if ADVANCED_FEATURES_AVAILABLE:
                            self._record_interaction(
                                "click",
                                locator,
                                "SUCCESS",
                                "Used JS click",
                            )
                            self._end_performance_tracking("click")
                        return True
                    raise

                if ADVANCED_FEATURES_AVAILABLE:
                    self._record_interaction("click", locator, "SUCCESS")
                    self._end_performance_tracking("click")
                return True

        except (WebDriverException, TimeoutException) as e:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction("click", locator, "FAILED", str(e))
                self._end_performance_tracking("click")

                # Try error recovery
                if self.error_handler and self.error_handler.handle_error(
                    e,
                    self.driver,
                    self.test_name,
                ):
                    # Retry after recovery
                    return self.click(locator, timeout, scroll_to_element, force_click)

            return False
        else:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction(
                    "click",
                    locator,
                    "FAILED",
                    "Element not clickable",
                )
                self._end_performance_tracking("click")
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
        """
        Send keys to element with enhanced features.

        Args:
            locator: Tuple of (By method, selector)
            text: Text to type (or data key if use_test_data=True)
            clear_first: Whether to clear field first
            timeout: Wait timeout in seconds
            use_test_data: Whether to load text from test data manager
            data_key: Key for test data lookup

        Returns:
            True if successful, False otherwise
        """
        if ADVANCED_FEATURES_AVAILABLE:
            self._start_performance_tracking("send_keys")

        try:
            # Get text from test data if requested
            if use_test_data and ADVANCED_FEATURES_AVAILABLE and self.test_data_manager:
                test_data = self.test_data_manager.load_test_data(
                    "test_data",
                    self.environment,
                )
                actual_text = test_data.get(data_key or text, text)
            else:
                actual_text = text


            element = self.wait_for_element(locator, timeout)
            if element:
                # Clear existing value using several fallbacks;
                # suppress non-critical errors
                if clear_first:
                    with contextlib.suppress(Exception):
                        self.driver.execute_script(
                            "arguments[0].value = '';",
                            element,
                        )
                    with contextlib.suppress(Exception):
                        element.clear()
                    with contextlib.suppress(Exception):
                        element.send_keys("\ue009a\ue003")  # CTRL+A, DEL (may vary)

                # Attempt to send keys; fall back to JS if necessary
                with contextlib.suppress(Exception):
                    element.send_keys(actual_text)

                # Post-type verification and JS fallback
                entered_value = element.get_attribute("value")
                if entered_value != actual_text:
                    js_script = (
                        "arguments[0].value = arguments[1];"
                        "arguments[0].dispatchEvent(new Event('input', "
                        "{ bubbles: true }));"
                    )
                    with contextlib.suppress(Exception):
                        self.driver.execute_script(
                            js_script,
                            element,
                            actual_text,
                        )
                    entered_value = element.get_attribute("value")

                # Final verification
                if entered_value != actual_text:
                    message = (
                        f"Text verification failed. Expected: {actual_text}, "
                        f"Got: {entered_value}"
                    )
                    raise ValueError(message)

                if ADVANCED_FEATURES_AVAILABLE:
                    self._record_interaction(
                        "send_keys",
                        locator,
                        "SUCCESS",
                        f"Text: {actual_text}",
                    )
                    self._end_performance_tracking("send_keys")
                return True

        except (WebDriverException, TimeoutException) as e:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction("send_keys", locator, "FAILED", str(e))
                self._end_performance_tracking("send_keys")
            return False
        else:
            if ADVANCED_FEATURES_AVAILABLE:
                self._record_interaction(
                    "send_keys",
                    locator,
                    "FAILED",
                    "Element not found",
                )
                self._end_performance_tracking("send_keys")
            return False

    def get_text(self, locator: tuple[str, str], timeout: Optional[int] = None) -> str:
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

    def get_attribute(
        self,
        locator: tuple[str, str],
        attribute: str,
        timeout: Optional[int] = None,
    ) -> str:
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

    def is_element_visible(self, locator: tuple[str, str], timeout: int = 1) -> bool:
        """
        Check if element is visible.

        Args:
            locator: Tuple of (By method, selector)
            timeout: Wait timeout in seconds (short default)

        Returns:
            True if visible, False otherwise
        """
        return self.wait_for_element(locator, timeout) is not None

    def is_element_present(self, locator: tuple[str, str]) -> bool:
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
        except WebDriverException:
            return False
        else:
            return True

    def refresh_page(self) -> bool:
        """
        Refresh current page.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.refresh()
        except WebDriverException:
            return False
        else:
            return True

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

    def get_title(self, timeout: Optional[int] = None) -> str:
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
                    lambda driver: driver.title != "",
                )
        except (TimeoutException, WebDriverException):
            return ""
        else:
            return self.driver.title

    def go_back(self) -> bool:
        """
        Go back in browser history.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.back()
        except WebDriverException:
            return False
        else:
            return True

    def go_forward(self) -> bool:
        """
        Go forward in browser history.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.driver.forward()
        except WebDriverException:
            return False
        else:
            return True

    def wait_for_page_load(self, timeout: Optional[int] = None) -> bool:
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
                lambda driver: driver.execute_script("return document.readyState")
                == "complete",
            )
        except TimeoutException:
            return False
        else:
            return True

    # === UTILITY METHODS ===

    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """
        Take screenshot of current page.

        Args:
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to saved screenshot or empty string if failed
        """
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"

            # Ensure screenshots directory exists
            screenshot_dir = "screenshots"
            Path(screenshot_dir).mkdir(parents=True, exist_ok=True)

            filepath = str(Path(screenshot_dir) / filename)
            self.driver.save_screenshot(filepath)
        except (WebDriverException, TimeoutException):
            return ""
        else:
            return filepath

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

    def scroll_to_element(
        self,
        locator: tuple[str, str],
        timeout: Optional[int] = None,
    ) -> bool:
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
            except WebDriverException:
                return False
            else:
                return True
        return False

    # === DATABASE METHODS (if database connection provided) ===

    def execute_query(
        self, query: str, parameters: Optional[tuple] = None,
    ) -> list[dict]:
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
            cursor = execute_query(self.database, query, parameters)
            if cursor:
                return fetch_all(cursor) or []
        except (WebDriverException, TimeoutException):
            pass

        return []

    # === ADVANCED FEATURES ===

    def wait_for_element_advanced(
        self,
        locator: tuple[str, str],
        condition: str = "visible",
        timeout: Optional[int] = None,
        poll_frequency: float = 0.5,
    ) -> Any:
        """
        Enhanced waiting with multiple conditions and smart polling.

        Args:
            locator: Tuple of (By strategy, locator value)
            condition: Wait condition (present, visible, clickable, invisible)
            timeout: Custom timeout
            poll_frequency: How often to check condition

        Returns:
            WebElement when condition is met
        """
        if not ADVANCED_FEATURES_AVAILABLE:
            # Fallback to basic wait
            if condition == "visible":
                return self.wait_for_element(locator, timeout)
            if condition == "clickable":
                return self.wait_for_clickable(locator, timeout)
            return self.find_element(locator, timeout)

        self._start_performance_tracking("wait_for_element")

        wait_time = timeout or self.timeout
        wait = WebDriverWait(self.driver, wait_time, poll_frequency)

        condition_map = {
            "present": EC.presence_of_element_located(locator),
            "visible": EC.visibility_of_element_located(locator),
            "clickable": EC.element_to_be_clickable(locator),
            "invisible": EC.invisibility_of_element_located(locator),
            "text_present": lambda driver: len(driver.find_element(*locator).text) > 0,
        }

        if condition not in condition_map:
            message = f"Unknown condition: {condition}"
            raise ValueError(message)

        try:
            element = wait.until(condition_map[condition])
            self._record_interaction(
                "wait_for_element",
                locator,
                "SUCCESS",
                f"Condition: {condition}",
            )
            self._end_performance_tracking("wait_for_element")
        except TimeoutException:
            self._record_interaction(
                "wait_for_element",
                locator,
                "FAILED",
                f"Timeout waiting for {condition}",
            )
            self._end_performance_tracking("wait_for_element")
            raise
        else:
            return element

    def is_element_healthy(self, locator: tuple[str, str]) -> dict[str, Any]:
        """
        Perform comprehensive element health check.

        Args:
            locator: Tuple of (By strategy, locator value)

        Returns:
            Dictionary with health check results
        """
        health_report = {
            "locator": locator,
            "timestamp": datetime.now(datetime.UTC),
            "checks": {},
            "overall_health": "unknown",
            "recommendations": [],
        }

        try:
            element = self.driver.find_element(*locator)

            # Basic existence check
            health_report["checks"]["exists"] = True

            # Visibility check
            is_visible = element.is_displayed()
            health_report["checks"]["visible"] = is_visible
            if not is_visible:
                health_report["recommendations"].append(
                    "Element exists but not visible",
                )

            # Interactability check
            is_enabled = element.is_enabled()
            health_report["checks"]["enabled"] = is_enabled
            if not is_enabled:
                health_report["recommendations"].append("Element is disabled")

            # Size and position check
            size = element.size
            location = element.location
            health_report["checks"]["has_size"] = (
                size["width"] > 0 and size["height"] > 0
            )
            health_report["checks"]["has_position"] = (
                location["x"] >= 0 and location["y"] >= 0
            )

            # Content check
            text_content = element.text
            value_content = element.get_attribute("value")
            health_report["checks"]["has_content"] = bool(text_content or value_content)

            # Stale element check
            try:
                print(element.tag_name)  # This will throw if element is stale
                health_report["checks"]["not_stale"] = True
            except StaleElementReferenceException:
                health_report["checks"]["not_stale"] = False
                health_report["recommendations"].append("Element reference is stale")

            # Calculate overall health
            passed_checks = sum(
                1 for result in health_report["checks"].values() if result
            )
            total_checks = len(health_report["checks"])
            health_percentage = (passed_checks / total_checks) * 100

            if health_percentage >= 90:
                health_report["overall_health"] = "excellent"
            elif health_percentage >= 70:
                health_report["overall_health"] = "good"
            elif health_percentage >= 50:
                health_report["overall_health"] = "fair"
            else:
                health_report["overall_health"] = "poor"

        except NoSuchElementException:
            health_report["checks"]["exists"] = False
            health_report["overall_health"] = "critical"
            health_report["recommendations"].append("Element not found")

        return health_report

    def load_test_scenario(self, scenario_name: str) -> dict[str, Any]:
        """
        Load test scenario data.

        Args:
            scenario_name: Name of the test scenario

        Returns:
            Dictionary containing scenario data
        """
        if not ADVANCED_FEATURES_AVAILABLE or not self.test_data_manager:
            return {}

        scenarios = self.test_data_manager.get_search_scenarios(self.environment)

        for scenario in scenarios:
            if scenario.get("name") == scenario_name:
                return scenario

        message = f"Test scenario '{scenario_name}' not found"
        raise ValueError(message)

    def get_user_credentials(self, role: str = "standard") -> dict[str, Any]:
        """
        Get user credentials for the specified role.

        Args:
            role: User role (admin, standard, readonly)

        Returns:
            Dictionary with user credentials
        """
        if not ADVANCED_FEATURES_AVAILABLE or not self.test_data_manager:
            return {}

        users = self.test_data_manager.get_user_accounts(role, self.environment)

        if not users:
            # Generate dynamic user if none found
            return self.test_data_manager.generate_test_user(role)

        return users[0]  # Return first user of the role

    def get_performance_report(self) -> dict[str, Any]:
        """
        Get performance metrics report.

        Returns:
            Dictionary containing performance analysis
        """
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"message": "Advanced features not available"}

        report = {
            "total_actions": sum(
                len(times) for times in self.performance_metrics.values()
            ),
            "action_metrics": {},
            "overall_performance": "unknown",
        }

        for action, times in self.performance_metrics.items():
            if times:
                report["action_metrics"][action] = {
                    "count": len(times),
                    "average_time": round(statistics.mean(times), 3),
                    "min_time": round(min(times), 3),
                    "max_time": round(max(times), 3),
                    "total_time": round(sum(times), 3),
                }

        # Calculate overall performance score
        if report["action_metrics"]:
            avg_times = [
                metrics["average_time"] for metrics in report["action_metrics"].values()
            ]
            overall_avg = sum(avg_times) / len(avg_times)

            if overall_avg < 1.0:
                report["overall_performance"] = "excellent"
            elif overall_avg < 3.0:
                report["overall_performance"] = "good"
            elif overall_avg < 5.0:
                report["overall_performance"] = "fair"
            else:
                report["overall_performance"] = "poor"

        return report

    def get_interaction_summary(self) -> dict[str, Any]:
        """
        Get summary of element interactions.

        Returns:
            Dictionary with interaction analysis
        """
        if not ADVANCED_FEATURES_AVAILABLE or not self.interaction_history:
            return {"message": "No interactions recorded"}

        total_interactions = len(self.interaction_history)
        successful_interactions = sum(
            1 for i in self.interaction_history if i["status"] == "SUCCESS"
        )

        # Action breakdown
        action_counts = {}
        for interaction in self.interaction_history:
            action = interaction["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_interactions": total_interactions,
            "successful_interactions": successful_interactions,
            "success_rate": round(
                (successful_interactions / total_interactions) * 100,
                2,
            ),
            "action_breakdown": action_counts,
            "most_recent_failures": [
                i for i in self.interaction_history[-10:] if i["status"] == "FAILED"
            ],
        }

    def take_screenshot_with_context(self, name: Optional[str] = None) -> str:
        """
        Take screenshot with additional context information.

        Args:
            name: Custom name for the screenshot

        Returns:
            Path to the saved screenshot
        """
        timestamp = datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        filename = name or f"{self.test_name}_{timestamp}"

        # Take the screenshot
        screenshot_path = f"screenshots/{filename}.png"
        try:
            self.driver.save_screenshot(screenshot_path)
        except WebDriverException:
            # Fallback to basic screenshot
            return self.take_screenshot(f"{filename}.png")

        # Add context information if advanced features available
        if ADVANCED_FEATURES_AVAILABLE:
            context = {
                "test_name": self.test_name,
                "timestamp": timestamp,
                "page_url": self.driver.current_url,
                "page_title": self.driver.title,
                "window_size": self.driver.get_window_size(),
                "performance_metrics": self.get_performance_report(),
                "recent_interactions": (
                    self.interaction_history[-5:] if self.interaction_history else []
                ),
            }

            # Save context as JSON
            context_path = f"screenshots/{filename}_context.json"
            try:
                with Path(context_path).open("w") as f:
                    json.dump(context, f, indent=2, default=str)
            except OSError:
                pass  # Context saving is optional

        return screenshot_path

    # === PRIVATE HELPER METHODS FOR ADVANCED FEATURES ===

    def _start_performance_tracking(self, _action: str) -> None:
        """Start tracking performance for an action."""
        if ADVANCED_FEATURES_AVAILABLE:
            self.action_start_time = time.time()

    def _end_performance_tracking(self, action: str) -> None:
        """End performance tracking and record metrics."""
        if ADVANCED_FEATURES_AVAILABLE and self.action_start_time:
            duration = time.time() - self.action_start_time

            if action not in self.performance_metrics:
                self.performance_metrics[action] = []

            self.performance_metrics[action].append(duration)
            self.action_start_time = None

    def load_test_configuration(
        self,
        config_name: str = "browser_config",
        environment: str = "default",
    ) -> dict[str, Any]:
        """
        Load YAML test configuration using TestDataManager.
        Demonstrates practical integration of YAML configuration management.
        """
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"config": "YAML configuration not available"}

        try:
            config = self.data_manager.load_yaml_config(config_name, environment)
            self.logger.info(
                "Loaded configuration: %s for environment: %s",
                config_name,
                environment,
            )
        except (OSError, ValueError) as e:
            self.logger.warning("Failed to load configuration: %s", e)
            return {"error": str(e)}
        else:
            return config

    def execute_with_retry_analytics(
        self,
        operation: Callable,
        operation_name: str = "operation",
        **kwargs,
    ) -> Any:
        """
        Execute operation with tenacity retry and performance analytics.
        Demonstrates integration of retry libraries with performance monitoring.
        """
        if not ADVANCED_FEATURES_AVAILABLE:
            return operation(**kwargs)

        start_time = time.time()
        memory_before = self.error_handler.monitor_memory_usage()

        try:
            # Use tenacity-based retry from error handler
            result = self.error_handler.execute_with_tenacity_retry(
                operation,
                max_attempts=3,
                wait_strategy="exponential",
                **kwargs,
            )

            duration = time.time() - start_time
            memory_after = self.error_handler.monitor_memory_usage()

            # Log performance metrics
            performance_data = {
                "operation": operation_name,
                "duration": duration,
                "memory_before_mb": memory_before.get("memory_usage_mb", 0),
                "memory_after_mb": memory_after.get("memory_usage_mb", 0),
                "success": True,
                "timestamp": datetime.now(datetime.UTC).isoformat(),
            }

            self.performance_data.append(performance_data)
            self.logger.info(
                "Operation '%s' completed in %.2fs",
                operation_name,
                duration,
            )

        except (RuntimeError, ValueError):
            duration = time.time() - start_time
            self.logger.exception(
                "Operation '%s' failed after %.2fs",
                operation_name,
                duration,
            )
            raise
        else:
            return result

    def generate_performance_report(self) -> dict[str, Any]:
        """
        Generate comprehensive performance report using pandas analytics.
        Integrates with AdvancedTestReporter for data analysis.
        """
        if not ADVANCED_FEATURES_AVAILABLE or not self.performance_data:
            return {"report": "No performance data available"}

        try:
            # Use reporter's pandas analytics for insights
            insights = self.test_reporter.get_performance_insights()
            csv_file = self.test_reporter.export_to_csv("performance_report.csv")

            return {
                "total_operations": len(self.performance_data),
                "avg_duration": sum(d["duration"] for d in self.performance_data)
                / len(self.performance_data),
                "detailed_insights": insights,
                "data_exported": csv_file,
            }

        except (OSError, RuntimeError) as e:
            self.logger.exception("Failed to generate performance report")
            return {"error": str(e)}

    def _record_interaction(
        self,
        action: str,
        locator: tuple[str, str],
        status: str,
        details: Optional[str] = None,
    ) -> None:
        """Record interaction for analysis and debugging."""
        if not ADVANCED_FEATURES_AVAILABLE:
            return

        interaction = {
            "timestamp": datetime.now(datetime.UTC),
            "action": action,
            "locator": locator,
            "status": status,
            "details": details,
            "page_url": self.driver.current_url,
        }

        self.interaction_history.append(interaction)

        # Keep only last 100 interactions to prevent memory issues
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
