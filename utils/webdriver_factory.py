"""
WebDriver and Database factory classes for test automation.
"""

import logging
import os
import shutil
import socket
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)


class WebDriverFactory:
    """
    Creates and configures WebDriver instances for different browsers.
    """

    @staticmethod
    def create_chrome_driver(
        *,
        headless: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    ) -> webdriver.Chrome:
        """Create Chrome driver with anti-detection configuration."""
        options = ChromeOptions()

        # Create a unique temporary user data directory to avoid conflicts
        # Use UUID to ensure uniqueness even in parallel test execution
        unique_id = str(uuid.uuid4())
        temp_user_data_dir = tempfile.mkdtemp(prefix=f"chrome_profile_{unique_id}_")
        options.add_argument(f"--user-data-dir={temp_user_data_dir}")

        # Add unique remote debugging port to avoid conflicts in parallel execution

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.listen(1)
            port = s.getsockname()[1]
        options.add_argument(f"--remote-debugging-port={port}")

        # Anti-detection options for search engines
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", value=False)

        # User agent to appear more like a real browser
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={user_agent}")

        if headless:
            options.add_argument("--headless=new")  # Use new headless mode

        if window_size:
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Store the temp directory path for cleanup
        driver._temp_user_data_dir = temp_user_data_dir  # noqa: SLF001

        # Remove webdriver property for bot detection
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
        )

        if not headless and not window_size:
            driver.maximize_window()

        return driver

    @staticmethod
    def create_firefox_driver(
        *,
        headless: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    ) -> webdriver.Firefox:
        """Create Firefox driver with configuration."""
        options = FirefoxOptions()

        # Basic Firefox options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # User agent to appear more like a real browser
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:119.0) "
            "Gecko/20100101 Firefox/119.0"
        )
        options.set_preference("general.useragent.override", user_agent)

        if headless:
            options.add_argument("--headless")

        if window_size:
            options.add_argument(f"--width={window_size[0]}")
            options.add_argument(f"--height={window_size[1]}")

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        if not headless and not window_size:
            driver.maximize_window()

        return driver

    @staticmethod
    def create_edge_driver(
        *,
        headless: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    ) -> webdriver.Edge:
        """Create Edge driver with configuration."""
        options = EdgeOptions()

        # Edge options similar to Chrome
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", value=False)

        # User agent to appear more like a real browser
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
        )
        options.add_argument(f"--user-agent={user_agent}")

        if headless:
            options.add_argument("--headless=new")

        if window_size:
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        service = EdgeService(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

        # Remove webdriver property that can be detected
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
        )

        if not headless and not window_size:
            driver.maximize_window()

        return driver

    @staticmethod
    def create_headless_chrome_for_testing() -> webdriver.Chrome:
        """
        Create a lightweight headless Chrome driver optimized for testing.

        This is a simplified version of create_chrome_driver specifically for
        unit and integration tests where anti-detection features are not needed.

        Returns:
            webdriver.Chrome: Configured headless Chrome driver

        Example:
            >>> driver = WebDriverFactory.create_headless_chrome_for_testing()
            >>> driver.get("https://example.com")
            >>> driver.quit()
        """
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        return webdriver.Chrome(options=options)


class DatabaseFactory:
    """
    Creates and manages database connections.
    """

    @staticmethod
    def create_database_connection(
        db_path: Optional[str] = None,
    ) -> Optional[sqlite3.Connection]:
        """Create database connection with error handling."""
        try:
            db_file = db_path or os.getenv("DB_PATH", "resources/chinook.db")

            # For custom paths (like in tests), attempt connection directly
            if db_path:
                connection = sqlite3.connect(db_file)
                connection.row_factory = sqlite3.Row  # Match test expectations
                logger.info("Database connected: %s", db_file)
            else:
                # For default path, use sqlite3.connect directly
                # (for test compatibility)
                if not Path(db_file).exists():
                    logger.warning("Database file not found: %s", db_file)
                    return None
                connection = sqlite3.connect(db_file)
                connection.row_factory = sqlite3.Row  # Match test expectations
                logger.info(
                    "Database connected: %s",
                    db_file,
                )
        except sqlite3.Error:
            # Re-raise SQL errors for test compatibility
            raise
        except Exception:
            logger.exception("Database connection failed")
            return None
        return connection


def get_driver(
    browser: str = "chrome",
    *,
    headless: bool = False,
    window_size: Optional[tuple[int, int]] = None,
    db_path: Optional[str] = None,
) -> tuple[object, Optional[object]]:
    """
    Factory function that creates WebDriver and Database instances.
    """
    browser_lower = browser.lower()

    # Create driver based on browser type
    driver_kwargs = {"headless": headless}
    if window_size:
        driver_kwargs["window_size"] = window_size

    if browser_lower == "chrome":
        driver = WebDriverFactory.create_chrome_driver(**driver_kwargs)
    elif browser_lower == "firefox":
        driver = WebDriverFactory.create_firefox_driver(**driver_kwargs)
    elif browser_lower == "edge":
        driver = WebDriverFactory.create_edge_driver(**driver_kwargs)
    else:
        message = f"Unsupported browser: {browser}"
        raise ValueError(message)

    # Create database connection with optional custom path
    database = DatabaseFactory.create_database_connection(db_path)

    # Set implicit wait
    timeout = int(os.getenv("IMPLICIT_WAIT", "10"))
    driver.implicitly_wait(timeout)

    return driver, database


def create_headless_driver() -> tuple[webdriver.Chrome, Optional[object]]:
    """Convenience method for creating headless drivers."""
    return get_driver(headless=True)


def cleanup_driver_and_database(
    driver: webdriver.Chrome,
    database: Optional[object],
) -> None:
    """Clean resource cleanup following DRY principle."""
    temp_dir = None
    try:
        if driver:
            # Store temp directory path before quitting
            temp_dir = getattr(driver, "_temp_user_data_dir", None)
            driver.quit()
            logger.info("Driver closed successfully")

            # Clean up temporary user data directory
            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info("Cleaned up temp user data dir: %s", temp_dir)
                except (OSError, PermissionError) as e:
                    logger.warning(
                        "Could not remove temp directory %s: %s",
                        temp_dir,
                        e,
                    )
    except Exception:
        logger.exception("Error closing driver")

    try:
        if database and hasattr(database, "close"):
            database.close()
            logger.info("Database closed successfully")
    except Exception:
        logger.exception("Error closing database")
