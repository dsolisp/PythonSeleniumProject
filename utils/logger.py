"""
Simple logging utility for test automation.
Provides clean, structured logging without over-engineering.
"""

import logging
import sys
from datetime import datetime

from config.settings import settings


class TestLogger:
    """Simple logger for test automation with file and console output."""

    def __init__(self, name: str = "TestAutomation"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Setup console and file handlers with clean formatting."""
        # Console handler - shows INFO and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)

        # File handler - captures everything
        log_file = (
            settings.LOGS_DIR
            / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def test_start(self, test_name: str):
        """Log test start."""
        self.info(f"Starting test: {test_name}")

    def test_end(self, test_name: str, status: str, duration: float):
        """Log test completion."""
        self.info(f"Test {test_name} {status} in {duration:.2f}s")

    def step(self, description: str):
        """Log test step."""
        self.info(f"Step: {description}")

    def screenshot(self, path: str):
        """Log screenshot capture."""
        self.info(f"Screenshot saved: {path}")

    def api_call(self, method: str, url: str, status_code: int):
        """Log API call."""
        self.info(f"API {method} {url} -> {status_code}")

    def database_query(self, query_type: str, table: str = ""):
        """Log database operation."""
        table_info = f" on {table}" if table else ""
        self.info(f"Database {query_type}{table_info}")


# Global logger instance
logger = TestLogger()


# Convenience functions for easy import
def info(message: str):
    logger.info(message)


def debug(message: str):
    logger.debug(message)


def warning(message: str):
    logger.warning(message)


def error(message: str):
    logger.error(message)


def test_start(test_name: str):
    logger.test_start(test_name)


def test_end(test_name: str, status: str, duration: float):
    logger.test_end(test_name, status, duration)


def step(description: str):
    logger.step(description)


def screenshot(path: str):
    logger.screenshot(path)


def api_call(method: str, url: str, status_code: int):
    logger.api_call(method, url, status_code)


def database_query(query_type: str, table: str = ""):
    logger.database_query(query_type, table)
