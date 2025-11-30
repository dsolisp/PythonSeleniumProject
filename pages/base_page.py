"""
Base Page - Clean implementation of the Page Object Model pattern.
Demonstrates advanced Selenium features with practical error handling
and optional performance monitoring.
"""

import contextlib
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

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

from utils.error_handler import SmartErrorHandler
from utils.sql_connection import execute_query, fetch_all
from utils.test_data_manager import TestDataManager


class BasePage:
    """
    Base Page for Page Object Model with optional advanced features.
    Provides common Selenium operations with intelligent error handling.
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
        Initialize base page.

        Args:
            driver: WebDriver instance or (driver, database) tuple
            database: Optional database connection
            timeout: Default wait timeout in seconds
            test_name: Name of the test for reporting
            environment: Environment name (test, staging, prod)
        """
        # Handle tuple format for backwards compatibility
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

        # Initialize tracking
        self.performance_metrics: dict[str, list[float]] = {}
        self.interaction_history: list[dict[str, Any]] = []
        self._action_start_time: Optional[float] = None

        # Initialize utilities
        self.error_handler = SmartErrorHandler()
        self.test_data_manager = TestDataManager()

    # === ELEMENT INTERACTION METHODS ===

    def find_element(
        self, locator: tuple[str, str], timeout: Optional[int] = None
    ) -> Optional[Any]:
        """Find element with optional timeout. Returns None if not found."""
        self._track_start("find_element")
        try:
            if timeout:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
            else:
                element = self.driver.find_element(*locator)
            self._track_end("find_element", locator, "SUCCESS")
            return element
        except (TimeoutException, NoSuchElementException) as e:
            self._track_end("find_element", locator, "FAILED", str(e))
            # Attempt recovery
            if self.error_handler.handle_error(e, self.driver, self.test_name):
                return self.find_element(locator, timeout)
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
        self._track_start("click")
        try:
            element = self.wait_for_clickable(locator, timeout)
            if not element:
                self._track_end("click", locator, "FAILED", "Element not clickable")
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

            self._track_end("click", locator, "SUCCESS")
            return True

        except (WebDriverException, TimeoutException) as e:
            self._track_end("click", locator, "FAILED", str(e))
            if self.error_handler.handle_error(e, self.driver, self.test_name):
                return self.click(
                    locator,
                    timeout=timeout,
                    scroll_to_element=scroll_to_element,
                    force_click=force_click,
                )
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
        self._track_start("send_keys")
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
                self._track_end("send_keys", locator, "FAILED", "Element not found")
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

            self._track_end("send_keys", locator, "SUCCESS", f"Text: {actual_text}")
            return True

        except (WebDriverException, TimeoutException, ValueError) as e:
            self._track_end("send_keys", locator, "FAILED", str(e))
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

    # === DATABASE METHODS ===

    def execute_query(
        self, query: str, parameters: Optional[tuple] = None
    ) -> list[Any]:
        """Execute database query. Returns results for SELECT or empty list."""
        if not self.database:
            return []
        try:
            # Check if it's a SELECT query (needs fetch) or write query
            if query.strip().upper().startswith("SELECT"):
                return fetch_all(self.database, query, parameters)
            else:
                # For INSERT/UPDATE/DELETE, execute and commit
                execute_query(self.database, query, parameters)
                self.database.commit()
                return []
        except Exception:
            return []

    # === ADVANCED FEATURES (Showcase Section) ===

    # NOTE: wait_for_element_advanced was removed as part of P1 code cleanup
    # (it was never used). Use wait_for_element() instead.

    def is_element_healthy(self, locator: tuple[str, str]) -> dict[str, Any]:
        """Check element health: exists, visible, enabled, has size, clickable."""
        try:
            el = self.driver.find_element(*locator)
            checks = {
                "exists": True,
                "visible": el.is_displayed(),
                "enabled": el.is_enabled(),
                "has_size": el.size["width"] > 0 and el.size["height"] > 0,
                "has_content": bool(el.text or el.get_attribute("value")),
            }
            # Check for stale reference
            try:
                _ = el.tag_name
                checks["not_stale"] = True
            except StaleElementReferenceException:
                checks["not_stale"] = False

            passed = sum(checks.values())
            health = (
                "excellent"
                if passed >= 5
                else "good"
                if passed >= 4
                else "fair"
                if passed >= 3
                else "poor"
            )
            return {
                "locator": locator,
                "checks": checks,
                "overall_health": health,
                "timestamp": datetime.now(datetime.UTC),
            }
        except NoSuchElementException:
            return {
                "locator": locator,
                "checks": {"exists": False},
                "overall_health": "critical",
            }

    def load_test_scenario(self, scenario_name: str) -> dict[str, Any]:
        """Load test scenario from TestDataManager."""
        for scenario in self.test_data_manager.get_search_scenarios(self.environment):
            if scenario.get("name") == scenario_name:
                return scenario
        raise ValueError(f"Test scenario '{scenario_name}' not found")

    def get_user_credentials(self, role: str = "standard") -> dict[str, Any]:
        """Get user credentials for role from TestDataManager."""
        users = self.test_data_manager.get_user_accounts(role, self.environment)
        return users[0] if users else self.test_data_manager.generate_test_user(role)

    def get_performance_report(self) -> dict[str, Any]:
        """Generate summary of recorded performance metrics with statistics."""
        if not self.performance_metrics:
            return {"message": "No metrics recorded"}

        report = {
            "total_actions": sum(len(t) for t in self.performance_metrics.values()),
            "action_metrics": {},
        }
        for action, times in self.performance_metrics.items():
            if times:
                report["action_metrics"][action] = {
                    "count": len(times),
                    "avg": round(statistics.mean(times), 3),
                    "min": round(min(times), 3),
                    "max": round(max(times), 3),
                }
        # Calculate overall performance score
        if report["action_metrics"]:
            avg = statistics.mean(m["avg"] for m in report["action_metrics"].values())
            report["overall"] = (
                "excellent"
                if avg < 1
                else "good"
                if avg < 3
                else "fair"
                if avg < 5
                else "poor"
            )
        return report

    def get_interaction_summary(self) -> dict[str, Any]:
        """Summarize element interactions for debugging."""
        if not self.interaction_history:
            return {"message": "No interactions recorded"}
        total = len(self.interaction_history)
        success = sum(1 for i in self.interaction_history if i["status"] == "SUCCESS")
        actions = {}
        for i in self.interaction_history:
            actions[i["action"]] = actions.get(i["action"], 0) + 1
        return {
            "total": total,
            "success": success,
            "rate": round(success / total * 100, 2),
            "actions": actions,
            "recent_failures": [
                i for i in self.interaction_history[-10:] if i["status"] == "FAILED"
            ],
        }

    def take_screenshot_with_context(self, name: Optional[str] = None) -> str:
        """Take screenshot and save a companion JSON file with page context."""
        ts = datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        filename = name or f"{self.test_name}_{ts}"
        path = f"screenshots/{filename}.png"

        try:
            Path("screenshots").mkdir(exist_ok=True)
            self.driver.save_screenshot(path)
            # Save context
            context = {
                "test": self.test_name,
                "url": self.driver.current_url,
                "title": self.driver.title,
                "window": self.driver.get_window_size(),
                "performance": self.get_performance_report(),
                "interactions": self.interaction_history[-5:],
            }
            with open(f"screenshots/{filename}_context.json", "w") as f:
                json.dump(context, f, indent=2, default=str)
        except (WebDriverException, OSError):
            return self.take_screenshot(f"{filename}.png")
        return path

    # === PRIVATE TRACKING METHODS ===

    def _track_start(self, action: str) -> None:
        """Start performance tracking."""
        self._action_start_time = time.time()

    def _track_end(
        self,
        action: str,
        locator: tuple[str, str],
        status: str,
        details: Optional[str] = None,
    ) -> None:
        """End tracking and record metrics/interaction."""
        if self._action_start_time:
            duration = time.time() - self._action_start_time
            self.performance_metrics.setdefault(action, []).append(duration)
            self._action_start_time = None

        # Record interaction (limit to 100 entries)
        self.interaction_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "action": action,
                "locator": locator,
                "status": status,
                "details": details,
                "url": self.driver.current_url,
            }
        )
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
