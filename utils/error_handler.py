"""
Error handling utilities with retry and recovery support.
"""

import functools
import logging
import re
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import psutil
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# === DATA CLASSES ===


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
    browser_logs: Optional[list[str]] = None
    retry_count: int = 0


class ErrorSeverity(Enum):
    LOW, MEDIUM, HIGH, CRITICAL = "low", "medium", "high", "critical"


class RecoveryStrategy(Enum):
    RETRY, REFRESH, NAVIGATE, RESTART_DRIVER, SKIP, FAIL = (
        "retry",
        "refresh",
        "navigate",
        "restart_driver",
        "skip",
        "fail",
    )


@dataclass
class RecoveryAction:
    """Recovery action configuration."""

    strategy: RecoveryStrategy
    max_attempts: int
    wait_time: float
    custom_action: Optional[Callable] = None
    success_validation: Optional[Callable] = None


# === SCREENSHOT SERVICE ===


class ScreenshotService:
    """Dedicated service for capturing error screenshots. Follows SRP."""

    def __init__(self, screenshots_dir: Optional[str] = None):
        self.screenshots_dir = (
            Path(screenshots_dir) if screenshots_dir else Path("screenshots")
        )
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def capture(self, driver, test_name: str, prefix: str = "error") -> Optional[str]:
        """Capture a screenshot from the driver."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.screenshots_dir / f"{prefix}_{test_name}_{ts}.png"
        try:
            driver.save_screenshot(str(path))
            return str(path)
        except Exception:
            self.logger.warning("Screenshot capture failed")
            return None


# === SYSTEM MONITOR ===


class SystemMonitor:
    """Monitors system resources. Follows SRP."""

    @staticmethod
    def get_memory_usage() -> dict[str, Any]:
        """Return process memory/CPU usage."""
        p = psutil.Process()
        mem = p.memory_info()
        return {
            "current_memory_mb": mem.rss / (1024 * 1024),
            "memory_percent": p.memory_percent(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# === ERROR CLASSIFIER ===


class ErrorClassifier:
    """Classifies Selenium errors by type and severity to determine recovery strategy."""

    # Error patterns with classification metadata
    PATTERNS = {
        r"timeout|timed out": ("timeout", ErrorSeverity.MEDIUM, RecoveryStrategy.RETRY),
        r"element not found|no such element|unable to locate": (
            "element_not_found",
            ErrorSeverity.HIGH,
            RecoveryStrategy.REFRESH,
        ),
        r"stale element|element is not attached": (
            "stale_element",
            ErrorSeverity.MEDIUM,
            RecoveryStrategy.RETRY,
        ),
        r"click intercepted": (
            "click_intercepted",
            ErrorSeverity.MEDIUM,
            RecoveryStrategy.RETRY,
        ),
        r"connection refused|connection reset|network|dns": (
            "connection",
            ErrorSeverity.HIGH,
            RecoveryStrategy.RESTART_DRIVER,
        ),
        r"webdriver|driver|session": (
            "webdriver",
            ErrorSeverity.CRITICAL,
            RecoveryStrategy.RESTART_DRIVER,
        ),
    }

    # Fallback by exception type
    TYPE_MAP = {
        "TimeoutException": ("timeout", ErrorSeverity.MEDIUM, RecoveryStrategy.RETRY),
        "NoSuchElementException": (
            "element_not_found",
            ErrorSeverity.HIGH,
            RecoveryStrategy.REFRESH,
        ),
        "StaleElementReferenceException": (
            "stale_element",
            ErrorSeverity.MEDIUM,
            RecoveryStrategy.RETRY,
        ),
        "WebDriverException": (
            "webdriver",
            ErrorSeverity.CRITICAL,
            RecoveryStrategy.RESTART_DRIVER,
        ),
    }

    def classify_error(
        self, error: Exception, _context: Optional[ErrorContext] = None
    ) -> dict[str, Any]:
        """Classify error and suggest recovery strategy."""
        msg, etype = str(error).lower(), type(error).__name__

        # Try pattern matching first (higher confidence)
        for pattern, (cat, sev, rec) in self.PATTERNS.items():
            if re.search(pattern, msg):
                return {
                    "classification": {
                        "category": cat,
                        "severity": sev,
                        "suggested_recovery": rec,
                    },
                    "error_type": etype,
                    "pattern_matched": pattern,
                    "confidence": 0.8,
                }

        # Fallback to exception type
        if etype in self.TYPE_MAP:
            cat, sev, rec = self.TYPE_MAP[etype]
            return {
                "classification": {
                    "category": cat,
                    "severity": sev,
                    "suggested_recovery": rec,
                },
                "error_type": etype,
                "pattern_matched": "type_fallback",
                "confidence": 0.6,
            }

        # Unknown
        return {
            "classification": {
                "category": "unknown",
                "severity": ErrorSeverity.HIGH,
                "suggested_recovery": RecoveryStrategy.FAIL,
            },
            "error_type": etype,
            "pattern_matched": "unknown",
            "confidence": 0.3,
        }


# === RECOVERY MANAGER ===


class RecoveryManager:
    """Executes recovery strategies for error handling."""

    def __init__(
        self,
        driver_factory: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """Initialize RecoveryManager."""
        self.driver_factory = driver_factory
        self.logger = logger or logging.getLogger(__name__)
        self.recovery_history: list[dict[str, Any]] = []

    def execute_recovery(
        self, driver, error_context: ErrorContext, action: RecoveryAction
    ) -> bool:
        """Execute recovery strategy and record results."""
        self.logger.info("Executing recovery: %s", action.strategy.value)
        start = datetime.now(timezone.utc)

        try:
            if action.strategy == RecoveryStrategy.RETRY:
                success = self._retry(driver, error_context, action)
            elif action.strategy == RecoveryStrategy.REFRESH:
                success = self._refresh(driver, error_context, action)
            elif action.strategy == RecoveryStrategy.NAVIGATE:
                success = self._navigate(driver, error_context, action)
            elif action.strategy == RecoveryStrategy.RESTART_DRIVER:
                success = self._restart_driver(driver, error_context, action)
            elif action.strategy == RecoveryStrategy.SKIP:
                success = True
            else:
                success = False
        except Exception:
            self.logger.exception("Recovery failed")
            success = False

        self.recovery_history.append(
            {
                "strategy": action.strategy.value,
                "success": success,
                "duration": (datetime.now(timezone.utc) - start).total_seconds(),
                "timestamp": start,
            }
        )
        return success

    def _retry(self, driver, _ctx: ErrorContext, action: RecoveryAction) -> bool:
        for _ in range(action.max_attempts):
            time.sleep(action.wait_time)
            try:
                if action.success_validation and action.success_validation(driver):
                    return True
                if action.custom_action:
                    action.custom_action(driver)
                    return True
                return True  # Default: assume success after wait
            except Exception as e:
                self.logger.warning("Retry failed: %s", e)
        return False

    def _refresh(self, driver, _ctx: ErrorContext, action: RecoveryAction) -> bool:
        try:
            driver.refresh()
            WebDriverWait(driver, action.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return (
                action.success_validation(driver) if action.success_validation else True
            )
        except Exception:
            return False

    def _navigate(self, driver, ctx: ErrorContext, action: RecoveryAction) -> bool:
        try:
            if action.custom_action:
                action.custom_action(driver)
            else:
                driver.get(ctx.page_url)
            WebDriverWait(driver, action.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            return (
                action.success_validation(driver) if action.success_validation else True
            )
        except Exception:
            return False

    def _restart_driver(
        self, driver, ctx: ErrorContext, action: RecoveryAction
    ) -> bool:
        if not self.driver_factory:
            self.logger.error("No driver factory for restart")
            return False
        try:
            try:
                driver.quit()
            except Exception:
                pass
            new_driver = self.driver_factory.create_driver()
            if ctx.page_url:
                new_driver.get(ctx.page_url)
            return (
                action.success_validation(new_driver)
                if action.success_validation
                else True
            )
        except Exception:
            return False

    def get_recovery_statistics(self) -> dict[str, Any]:
        """Get recovery performance statistics."""
        if not self.recovery_history:
            return {"message": "No recovery attempts recorded"}
        total = len(self.recovery_history)
        success = sum(1 for r in self.recovery_history if r["success"])
        stats = {}
        for r in self.recovery_history:
            s = r["strategy"]
            stats.setdefault(s, {"total": 0, "successful": 0})
            stats[s]["total"] += 1
            if r["success"]:
                stats[s]["successful"] += 1
        return {
            "total_recovery_attempts": total,
            "successful_recoveries": success,
            "success_rate": round(success / total * 100, 2),
            "strategy_performance": stats,
            "average_recovery_time": round(
                sum(r["duration"] for r in self.recovery_history) / total, 2
            ),
        }


class SmartErrorHandler:
    """Coordinates error handling with classification and recovery strategies."""

    # Default recovery configurations
    RECOVERY_CONFIGS = {
        RecoveryStrategy.RETRY: RecoveryAction(
            RecoveryStrategy.RETRY, max_attempts=3, wait_time=2.0
        ),
        RecoveryStrategy.REFRESH: RecoveryAction(
            RecoveryStrategy.REFRESH, max_attempts=2, wait_time=5.0
        ),
        RecoveryStrategy.NAVIGATE: RecoveryAction(
            RecoveryStrategy.NAVIGATE, max_attempts=2, wait_time=10.0
        ),
        RecoveryStrategy.RESTART_DRIVER: RecoveryAction(
            RecoveryStrategy.RESTART_DRIVER, max_attempts=1, wait_time=15.0
        ),
    }

    def __init__(self, driver_factory=None, screenshots_dir: Optional[str] = None):
        self.classifier = ErrorClassifier()
        self.recovery_manager = RecoveryManager(driver_factory)
        self.screenshot_service = ScreenshotService(screenshots_dir)
        self.system_monitor = SystemMonitor()
        self.logger = logging.getLogger(__name__)
        self.recovery_configs = dict(self.RECOVERY_CONFIGS)  # Instance copy

    def monitor_memory_usage(self) -> dict[str, Any]:
        """Return process memory/CPU usage."""
        return self.system_monitor.get_memory_usage()

    def handle_error(
        self,
        error: Exception,
        driver,
        test_name: str,
        custom_recovery: Optional[RecoveryAction] = None,
    ) -> bool:
        """Main error handling entry point."""
        ctx = self._create_error_context(error, driver, test_name)
        ctx.screenshot_path = self.screenshot_service.capture(driver, test_name)

        classification = self.classifier.classify_error(error, ctx)
        category = classification["classification"]["category"]
        self.logger.error("Error: %s - %s", category, error)

        action = custom_recovery or self.recovery_configs.get(
            classification["classification"]["suggested_recovery"]
        )
        if not action:
            self.logger.error("No recovery strategy")
            return False

        success = self.recovery_manager.execute_recovery(driver, ctx, action)
        self.logger.info("Recovery %s", "successful" if success else "failed")
        return success

    def _create_error_context(
        self, error: Exception, driver, test_name: str
    ) -> ErrorContext:
        try:
            url = driver.current_url
        except Exception:
            url = "unknown"
        try:
            logs = driver.get_log("browser")
        except Exception:
            logs = None
        return ErrorContext(
            type(error).__name__,
            str(error),
            datetime.now(timezone.utc),
            test_name,
            url,
            stack_trace=traceback.format_exc(),
            browser_logs=logs,
        )

    def execute_with_retry(
        self,
        operation: Callable,
        *args,
        max_attempts: int = 3,
        retry_exceptions: Optional[tuple] = None,
        **kwargs,
    ) -> Any:
        """Execute operation with tenacity retry on common Selenium exceptions."""
        if not retry_exceptions:
            retry_exceptions = (
                TimeoutException,
                StaleElementReferenceException,
                ElementNotInteractableException,
                NoSuchElementException,
            )
        wait = wait_exponential(multiplier=1, min=1, max=10)
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait,
            retry=retry_if_exception_type(retry_exceptions),
        ):
            with attempt:
                return operation(*args, **kwargs)
        return None


def smart_retry(
    max_attempts: int = 3, wait_time: float = 2.0, exceptions: tuple = (Exception,)
):
    """Decorator for automatic retry with configurable attempts and wait time."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if i < max_attempts - 1:
                        time.sleep(wait_time)
            if last_exc:
                raise last_exc
            return None

        return wrapper

    return decorator
