"""
Smart Error Handling and Recovery System
Intelligent error classification and automatic recovery mechanisms with
retry strategies. Integrates tenacity and retry libraries for robust
error handling.
"""

import functools
import logging
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Retry libraries for robust error handling
try:
    from retry import retry
    from tenacity import (
        Retrying,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )

    RETRY_AVAILABLE = True
except ImportError:
    RETRY_AVAILABLE = False
    Retrying = None
    retry = None

# Memory and performance monitoring
try:
    import memory_profiler
    import psutil

    PROFILING_AVAILABLE = True
except ImportError:
    PROFILING_AVAILABLE = False
    psutil = None
    memory_profiler = None

from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Recovery strategy types."""

    RETRY = "retry"
    REFRESH = "refresh"
    NAVIGATE = "navigate"
    RESTART_DRIVER = "restart_driver"
    SKIP = "skip"
    FAIL = "fail"


@dataclass
class ErrorContext:
    """Context information for error handling."""

    error_type: str
    error_message: str
    timestamp: datetime
    test_name: str
    page_url: str
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
    browser_logs: Optional[List[str]] = None
    element_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0


@dataclass
class RecoveryAction:
    """Recovery action definition."""

    strategy: RecoveryStrategy
    max_attempts: int
    wait_time: float
    custom_action: Optional[Callable] = None
    success_validation: Optional[Callable] = None


class ErrorClassifier:
    """
    Intelligent error classification system.
    Categorizes errors and suggests appropriate recovery strategies.
    """

    def __init__(self):
        """Initialize error classifier with predefined patterns."""
        self.error_patterns = {
            # Timeout related errors
            r"timeout|timed out|time out": {
                "category": "timeout",
                "severity": ErrorSeverity.MEDIUM,
                "suggested_recovery": RecoveryStrategy.RETRY,
                "common_causes": [
                    "Slow page load",
                    "Network issues",
                    "Server delays",
                ],
            },
            # Element interaction errors
            r"element not found|no such element|unable to locate": {
                "category": "element_not_found",
                "severity": ErrorSeverity.HIGH,
                "suggested_recovery": RecoveryStrategy.REFRESH,
                "common_causes": [
                    "Dynamic content loading",
                    "Element locator changes",
                    "Timing issues",
                ],
            },
            # Stale element errors
            r"stale element|element is not attached": {
                "category": "stale_element",
                "severity": ErrorSeverity.MEDIUM,
                "suggested_recovery": RecoveryStrategy.RETRY,
                "common_causes": [
                    "DOM updates",
                    "Page refresh",
                    "Dynamic content",
                ],
            },
            # Click interception errors
            r"click intercepted|element click intercepted": {
                "category": "click_intercepted",
                "severity": ErrorSeverity.MEDIUM,
                "suggested_recovery": RecoveryStrategy.RETRY,
                "common_causes": [
                    "Overlapping elements",
                    "Modal dialogs",
                    "Loading overlays",
                ],
            },
            # Connection errors
            r"connection refused|connection reset|network|dns": {
                "category": "connection",
                "severity": ErrorSeverity.HIGH,
                "suggested_recovery": RecoveryStrategy.RESTART_DRIVER,
                "common_causes": [
                    "Network connectivity",
                    "Server unavailable",
                    "DNS issues",
                ],
            },
            # WebDriver errors
            r"webdriver|driver|session": {
                "category": "webdriver",
                "severity": ErrorSeverity.CRITICAL,
                "suggested_recovery": RecoveryStrategy.RESTART_DRIVER,
                "common_causes": [
                    "Driver crash",
                    "Browser closed",
                    "Session expired",
                ],
            },
        }

    def classify_error(self, error: Exception,
                       context: ErrorContext) -> Dict[str, Any]:
        """
        Classify error and return detailed information.

        Args:
            error: The exception that occurred
            context: Error context information

        Returns:
            Dictionary containing error classification details
        """
        import re

        error_message = str(error).lower()
        error_type = type(error).__name__

        # Match against patterns
        for pattern, info in self.error_patterns.items():
            if re.search(pattern, error_message):
                return {
                    "classification": info,
                    "error_type": error_type,
                    "pattern_matched": pattern,
                    "confidence": 0.8,  # High confidence for pattern matches
                }

        # Fallback classification based on exception type
        type_mapping = {
            "TimeoutException": {
                "category": "timeout",
                "severity": ErrorSeverity.MEDIUM,
                "suggested_recovery": RecoveryStrategy.RETRY,
            },
            "NoSuchElementException": {
                "category": "element_not_found",
                "severity": ErrorSeverity.HIGH,
                "suggested_recovery": RecoveryStrategy.REFRESH,
            },
            "StaleElementReferenceException": {
                "category": "stale_element",
                "severity": ErrorSeverity.MEDIUM,
                "suggested_recovery": RecoveryStrategy.RETRY,
            },
            "WebDriverException": {
                "category": "webdriver",
                "severity": ErrorSeverity.CRITICAL,
                "suggested_recovery": RecoveryStrategy.RESTART_DRIVER,
            },
        }

        if error_type in type_mapping:
            return {
                "classification": type_mapping[error_type],
                "error_type": error_type,
                "pattern_matched": "type_fallback",
                "confidence": 0.6,  # Lower confidence for type-only matches
            }

        # Unknown error type
        return {
            "classification": {
                "category": "unknown",
                "severity": ErrorSeverity.HIGH,
                "suggested_recovery": RecoveryStrategy.FAIL,
            },
            "error_type": error_type,
            "pattern_matched": "unknown",
            "confidence": 0.3,
        }


class RecoveryManager:
    """
    Intelligent recovery manager that executes recovery strategies.
    """

    def __init__(self, driver_factory=None, logger=None):
        """Initialize recovery manager."""
        self.driver_factory = driver_factory
        self.logger = logger or logging.getLogger(__name__)
        self.recovery_history: List[Dict[str, Any]] = []

    def execute_recovery(
        self,
        driver,
        error_context: ErrorContext,
        recovery_action: RecoveryAction,
    ) -> bool:
        """
        Execute recovery strategy.

        Args:
            driver: WebDriver instance
            error_context: Context of the error
            recovery_action: Recovery action to execute

        Returns:
            True if recovery was successful, False otherwise
        """
        self.logger.info(
            f"Executing recovery strategy: {
                recovery_action.strategy.value}"
        )

        recovery_start = datetime.now()
        success = False

        try:
            if recovery_action.strategy == RecoveryStrategy.RETRY:
                success = self._retry_recovery(
                    driver, error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.REFRESH:
                success = self._refresh_recovery(
                    driver, error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.NAVIGATE:
                success = self._navigate_recovery(
                    driver, error_context, recovery_action
                )
            elif recovery_action.strategy == RecoveryStrategy.RESTART_DRIVER:
                success = self._restart_driver_recovery(
                    driver, error_context, recovery_action
                )
            elif recovery_action.strategy == RecoveryStrategy.SKIP:
                success = True  # Skip always "succeeds"
            else:
                success = False

        except Exception as e:
            self.logger.error(f"Recovery strategy failed: {str(e)}")
            success = False

        # Record recovery attempt
        recovery_record = {
            "strategy": recovery_action.strategy.value,
            "success": success,
            "duration": (datetime.now() - recovery_start).total_seconds(),
            "error_context": error_context,
            "timestamp": recovery_start,
        }
        self.recovery_history.append(recovery_record)

        return success

    def _retry_recovery(
        self,
        driver,
        error_context: ErrorContext,
        recovery_action: RecoveryAction,
    ) -> bool:
        """Execute retry recovery strategy."""
        for attempt in range(recovery_action.max_attempts):
            try:
                time.sleep(recovery_action.wait_time)

                if recovery_action.success_validation:
                    if recovery_action.success_validation(driver):
                        return True
                elif recovery_action.custom_action:
                    recovery_action.custom_action(driver)
                    return True
                else:
                    # Default retry behavior - wait and assume success
                    return True

            except Exception as e:
                self.logger.warning(
                    f"Retry attempt {
                        attempt +
                        1} failed: {
                        str(e)}")
                continue

        return False

    def _refresh_recovery(
        self,
        driver,
        error_context: ErrorContext,
        recovery_action: RecoveryAction,
    ) -> bool:
        """Execute page refresh recovery strategy."""
        try:
            current_url = driver.current_url
            driver.refresh()

            # Wait for page to load
            WebDriverWait(driver, recovery_action.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Validate success
            if recovery_action.success_validation:
                return recovery_action.success_validation(driver)

            # Default validation - check if URL is accessible
            return driver.current_url == current_url

        except Exception as e:
            self.logger.error(f"Refresh recovery failed: {str(e)}")
            return False

    def _navigate_recovery(
        self,
        driver,
        error_context: ErrorContext,
        recovery_action: RecoveryAction,
    ) -> bool:
        """Execute navigation recovery strategy."""
        try:
            if recovery_action.custom_action:
                recovery_action.custom_action(driver)
            else:
                # Default navigation - go to current URL
                driver.get(error_context.page_url)

            # Wait for navigation to complete
            WebDriverWait(driver, recovery_action.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            if recovery_action.success_validation:
                return recovery_action.success_validation(driver)

            return True

        except Exception as e:
            self.logger.error(f"Navigate recovery failed: {str(e)}")
            return False

    def _restart_driver_recovery(
        self,
        driver,
        error_context: ErrorContext,
        recovery_action: RecoveryAction,
    ) -> bool:
        """Execute driver restart recovery strategy."""
        try:
            if not self.driver_factory:
                self.logger.error(
                    "No driver factory available for restart recovery")
                return False

            # Close current driver
            try:
                driver.quit()
            except BaseException:
                pass

            # Create new driver
            new_driver = self.driver_factory.create_driver()

            # Navigate to original URL
            if error_context.page_url:
                new_driver.get(error_context.page_url)

            if recovery_action.success_validation:
                return recovery_action.success_validation(new_driver)

            return True

        except Exception as e:
            self.logger.error(f"Driver restart recovery failed: {str(e)}")
            return False

    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Get recovery performance statistics."""
        if not self.recovery_history:
            return {"message": "No recovery attempts recorded"}

        total_attempts = len(self.recovery_history)
        successful_attempts = sum(
            1 for r in self.recovery_history if r["success"])

        strategy_stats = {}
        for record in self.recovery_history:
            strategy = record["strategy"]
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {"total": 0, "successful": 0}
            strategy_stats[strategy]["total"] += 1
            if record["success"]:
                strategy_stats[strategy]["successful"] += 1

        return {
            "total_recovery_attempts": total_attempts,
            "successful_recoveries": successful_attempts,
            "success_rate": round((successful_attempts / total_attempts) * 100, 2),
            "strategy_performance": strategy_stats,
            "average_recovery_time": round(
                sum(r["duration"] for r in self.recovery_history) / total_attempts,
                2,
            ),
        }


class SmartErrorHandler:
    """
    Main error handling coordinator that combines classification and recovery.
    """

    def __init__(self, driver_factory=None, screenshots_dir: str = None):
        """Initialize smart error handler."""
        self.classifier = ErrorClassifier()
        self.recovery_manager = RecoveryManager(driver_factory)
        self.screenshots_dir = (
            Path(screenshots_dir) if screenshots_dir else Path("screenshots")
        )
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Recovery configurations
        self.recovery_configs = {
            RecoveryStrategy.RETRY: RecoveryAction(
                strategy=RecoveryStrategy.RETRY, max_attempts=3, wait_time=2.0
            ),
            RecoveryStrategy.REFRESH: RecoveryAction(
                strategy=RecoveryStrategy.REFRESH,
                max_attempts=2,
                wait_time=5.0,
            ),
            RecoveryStrategy.NAVIGATE: RecoveryAction(
                strategy=RecoveryStrategy.NAVIGATE,
                max_attempts=2,
                wait_time=10.0,
            ),
            RecoveryStrategy.RESTART_DRIVER: RecoveryAction(
                strategy=RecoveryStrategy.RESTART_DRIVER,
                max_attempts=1,
                wait_time=15.0,
            ),
        }

    def handle_error(
        self,
        error: Exception,
        driver,
        test_name: str,
        custom_recovery: Optional[RecoveryAction] = None,
    ) -> bool:
        """
        Main error handling entry point.

        Args:
            error: The exception that occurred
            driver: WebDriver instance
            test_name: Name of the test that failed
            custom_recovery: Custom recovery action (optional)

        Returns:
            True if error was recovered, False if recovery failed
        """
        # Create error context
        error_context = self._create_error_context(error, driver, test_name)

        # Take screenshot for debugging
        screenshot_path = self._capture_error_screenshot(driver, test_name)
        error_context.screenshot_path = screenshot_path

        # Classify the error
        classification = self.classifier.classify_error(error, error_context)

        self.logger.error(
            f"Error classified as: {
                classification['classification']['category']}"
        )
        self.logger.error(f"Error message: {str(error)}")

        # Determine recovery strategy
        if custom_recovery:
            recovery_action = custom_recovery
        else:
            suggested_strategy = classification["classification"]["suggested_recovery"]
            recovery_action = self.recovery_configs.get(suggested_strategy)

        if not recovery_action:
            self.logger.error("No recovery strategy available")
            return False

        # Execute recovery
        recovery_success = self.recovery_manager.execute_recovery(
            driver, error_context, recovery_action
        )

        if recovery_success:
            self.logger.info("Error recovery successful")
        else:
            self.logger.error("Error recovery failed")

        return recovery_success

    def _create_error_context(
        self, error: Exception, driver, test_name: str
    ) -> ErrorContext:
        """Create error context with available information."""
        try:
            current_url = driver.current_url
        except BaseException:
            current_url = "unknown"

        try:
            browser_logs = driver.get_log("browser")
        except BaseException:
            browser_logs = None

        return ErrorContext(
            error_type=type(error).__name__,
            error_message=str(error),
            timestamp=datetime.now(),
            test_name=test_name,
            page_url=current_url,
            stack_trace=traceback.format_exc(),
            browser_logs=browser_logs,
        )

    def _capture_error_screenshot(
            self, driver, test_name: str) -> Optional[str]:
        """Capture screenshot when error occurs."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_{test_name}_{timestamp}.png"
            file_path = self.screenshots_dir / filename

            driver.save_screenshot(str(file_path))
            return str(file_path)

        except Exception as e:
            self.logger.warning(
                f"Failed to capture error screenshot: {
                    str(e)}"
            )
            return None

    def monitor_memory_usage(self) -> Dict[str, Any]:
        """
        Monitor memory usage during test execution using psutil.
        """
        if not PROFILING_AVAILABLE:
            return {"memory_monitoring": "Not available - psutil not installed"}

        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "current_memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "memory_percent": round(process.memory_percent(), 2),
            "cpu_percent": round(process.cpu_percent(), 2),
            "timestamp": datetime.now().isoformat(),
        }

    def execute_with_tenacity_retry(
        self,
        operation: Callable,
        *args,
        max_attempts: int = 3,
        wait_strategy: str = "exponential",
        **kwargs,
    ) -> Any:
        """
        Execute operation with tenacity-based retry logic.
        Provides robust retry mechanisms with different wait strategies.
        """
        if not RETRY_AVAILABLE:
            # Fallback to basic retry if tenacity not available
            return self._basic_retry(
                operation, *args, max_attempts=max_attempts, **kwargs
            )

        # Configure wait strategy
        if wait_strategy == "exponential":
            wait_func = wait_exponential(multiplier=1, min=1, max=10)
        else:
            wait_func = wait_exponential(multiplier=1, min=1, max=3)

        # Use tenacity for robust retries
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_func,
            retry=retry_if_exception_type((Exception,)),
        ):
            with attempt:
                return operation(*args, **kwargs)

    def _basic_retry(
        self, operation: Callable, *args, max_attempts: int = 3, **kwargs
    ) -> Any:
        """Basic retry mechanism without tenacity."""
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2**attempt)  # Exponential backoff

        raise last_exception


def smart_retry(
    max_attempts: int = 3,
    wait_time: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator for automatic retry with smart error handling.

    Args:
        max_attempts: Maximum number of retry attempts
        wait_time: Time to wait between attempts
        exceptions: Exceptions to catch and retry

    Usage:
        @smart_retry(max_attempts=3, exceptions=(TimeoutException,))
        def click_element(self, locator):
            element = self.driver.find_element(*locator)
            element.click()
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        raise last_exception

            return None

        return wrapper

    return decorator


def with_error_recovery(
    error_handler: SmartErrorHandler,
    recovery_strategy: Optional[RecoveryStrategy] = None,
):
    """
    Decorator for automatic error recovery.

    Args:
        error_handler: SmartErrorHandler instance
        recovery_strategy: Specific recovery strategy to use

    Usage:
        @with_error_recovery(error_handler, RecoveryStrategy.RETRY)
        def navigate_to_page(self, url):
            self.driver.get(url)
    """

    def execute_with_tenacity_retry(
        self,
        operation: Callable,
        *args,
        max_attempts: int = 3,
        wait_strategy: str = "exponential",
        **kwargs,
    ) -> Any:
        """
        Execute operation with tenacity-based retry logic.
        Provides robust retry mechanisms with different wait strategies.
        """
        if not RETRY_AVAILABLE:
            # Fallback to basic retry if tenacity not available
            return self._basic_retry(
                operation, *args, max_attempts=max_attempts, **kwargs
            )

        # Configure wait strategy
        if wait_strategy == "exponential":
            wait_func = wait_exponential(multiplier=1, min=1, max=10)
        else:
            wait_func = wait_exponential(multiplier=1, min=1, max=3)

        # Use tenacity for robust retries
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_func,
            retry=retry_if_exception_type(
                (
                    TimeoutException,
                    NoSuchElementException,
                    ElementNotInteractableException,
                    StaleElementReferenceException,
                )
            ),
        ):
            with attempt:
                try:
                    result = operation(*args, **kwargs)
                    self.logger.info(
                        f"Operation succeeded on attempt {
                            attempt.retry_state.attempt_number}"
                    )
                    return result
                except Exception as e:
                    self.logger.warning(
                        f"Attempt {
                            attempt.retry_state.attempt_number} failed: {
                            str(e)}"
                    )
                    if attempt.retry_state.attempt_number == max_attempts:
                        self.logger.error(
                            f"All {max_attempts} attempts failed")
                    raise

    def _basic_retry(
        self, operation: Callable, *args, max_attempts: int = 3, **kwargs
    ) -> Any:
        """Fallback retry mechanism when tenacity is not available."""
        last_exception = None

        for attempt in range(max_attempts):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(2**attempt)  # Exponential backoff

        raise last_exception

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Try to recover from error
                test_name = getattr(self, "_test_name", func.__name__)

                custom_recovery = None
                if recovery_strategy:
                    custom_recovery = error_handler.recovery_configs.get(
                        recovery_strategy
                    )

                recovery_success = error_handler.handle_error(
                    e, self.driver, test_name, custom_recovery
                )

                if recovery_success:
                    # Retry the original function after recovery
                    return func(self, *args, **kwargs)
                else:
                    # Re-raise the original exception if recovery failed
                    raise e

        return wrapper

    return decorator


# Global error handler instance
smart_error_handler = SmartErrorHandler()
