"""
Lightweight error handling with clean, human-readable output.

Design principles:
- Simple, readable exception formatting
- Minimal abstraction, maximum clarity
- Works with any exception type
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import psutil
from tenacity import Retrying, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


# === CLEAN ERROR INFO ===


@dataclass
class ErrorInfo:
    """Minimal error information for clean output."""

    error_type: str
    message: str
    file: str
    line: int

    def __str__(self):
        """Human-readable single-line format."""
        return f"[{self.error_type}] {self.message} ({self.file}:{self.line})"

    def __repr__(self):
        return self.__str__()


def extract_error_info(exc):
    """Extract essential info from any exception."""
    exc_type = type(exc).__name__
    message = str(exc).split("\n")[0].strip()  # First line only

    # Get location from traceback
    tb = exc.__traceback__
    file, line = "unknown", 0

    if tb:
        # Walk to the deepest frame (actual error location)
        while tb.tb_next:
            tb = tb.tb_next
        file = Path(tb.tb_frame.f_code.co_filename).name
        line = tb.tb_lineno

    return ErrorInfo(exc_type, message, file, line)


def format_error(exc):
    """Format any exception as a clean, single-line string."""
    return str(extract_error_info(exc))


# === CLEAN EXCEPTION ===


class CleanException(Exception):
    """
    Exception wrapper that provides clean, human-readable output.

    Usage:
        raise CleanException("User-friendly message")
        raise CleanException("Message", cause=original_exception)
        raise CleanException.wrap(original_exception)
    """

    def __init__(self, message, cause=None):
        self.clean_message = message
        self.cause = cause
        self._info = None

        if cause:
            self._info = extract_error_info(cause)
            super().__init__(f"{message}: {self._info}")
        else:
            super().__init__(message)

    @classmethod
    def wrap(cls, exc, message=None):
        """Wrap an existing exception with clean formatting."""
        info = extract_error_info(exc)
        msg = message or info.message
        wrapped = cls(msg, cause=exc)
        wrapped._info = info
        return wrapped

    @property
    def info(self):
        """Get error info if available."""
        return self._info

    def __str__(self):
        if self._info:
            return f"[{self._info.error_type}] {self.clean_message} ({self._info.file}:{self._info.line})"
        return self.clean_message


# === SCREENSHOT SERVICE (minimal) ===


class ScreenshotService:
    """Simple screenshot capture for error documentation."""

    def __init__(self, screenshots_dir=None):
        self.screenshots_dir = Path(screenshots_dir or "screenshots")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, driver, test_name, prefix="error"):
        """Capture screenshot. Returns path or None on failure."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.screenshots_dir / f"{prefix}_{test_name}_{ts}.png"
        try:
            driver.save_screenshot(str(path))
            return str(path)
        except Exception:
            logger.warning("Screenshot capture failed")
            return None


# === SIMPLE ERROR HANDLER ===


class SmartErrorHandler:
    """
    Simplified error handler focused on logging and screenshots.

    Removed over-engineering:
    - No ErrorClassifier (use Selenium's native exception types)
    - No RecoveryManager (use tenacity for retries)
    - No complex recovery strategies
    """

    def __init__(self, driver_factory=None, screenshots_dir=None):
        self.driver_factory = driver_factory
        self.screenshot_service = ScreenshotService(screenshots_dir)

    def handle_error(self, error, driver, test_name, custom_recovery=None):  # noqa: ARG002
        """
        Log error with clean formatting and capture screenshot.
        Returns False (no automatic recovery - use tenacity instead).
        """
        clean_error = format_error(error)
        logger.error("Test '%s' failed: %s", test_name, clean_error)

        # Capture screenshot for debugging
        self.screenshot_service.capture(driver, test_name)

        return False  # No automatic recovery

    def monitor_memory_usage(self):
        """Return process memory/CPU usage."""
        p = psutil.Process()
        mem = p.memory_info()
        return {
            "current_memory_mb": mem.rss / (1024 * 1024),
            "memory_percent": p.memory_percent(),
            "cpu_percent": p.cpu_percent(interval=0.1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def execute_with_retry(
        self,
        operation,
        *args,
        max_attempts=3,
        retry_exceptions=None,
        **kwargs,
    ):
        """Execute operation with tenacity retry."""
        retry_exceptions = retry_exceptions or (Exception,)
        wait = wait_exponential(multiplier=1, min=1, max=10)

        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait,
        ):
            with attempt:
                return operation(*args, **kwargs)
        return None
