"""
WebDriver and Database factory classes for test automation.
"""

import logging
import os
import sqlite3
from typing import Optional, Tuple

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
        headless: bool = False, window_size: Optional[Tuple[int, int]] = None
    ) -> webdriver.Chrome:
        """Create Chrome driver with anti-detection configuration."""
        options = ChromeOptions()

        # Anti-detection options to avoid Google CAPTCHA
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # User agent to appear more like a real browser
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        options.add_argument(f"--user-agent={user_agent}")

        if headless:
            options.add_argument("--headless=new")  # Use new headless mode

        if window_size:
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Remove webdriver property that Google detects
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        if not headless and not window_size:
            driver.maximize_window()

        return driver

    @staticmethod
    def create_firefox_driver(
        headless: bool = False, window_size: Optional[Tuple[int, int]] = None
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
        headless: bool = False, window_size: Optional[Tuple[int, int]] = None
    ) -> webdriver.Edge:
        """Create Edge driver with configuration."""
        options = EdgeOptions()

        # Edge options similar to Chrome
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

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
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        if not headless and not window_size:
            driver.maximize_window()

        return driver


class DatabaseFactory:
    """
    Creates and manages database connections.
    """

    @staticmethod
    def create_database_connection(db_path: str = None) -> Optional[object]:
        """Create database connection with error handling."""
        try:
            db_file = db_path or os.getenv("DB_PATH", "resources/chinook.db")

            # For custom paths (like in tests), attempt connection directly
            if db_path:
                connection = sqlite3.connect(db_file)
                logger.info(f"Database connected: {db_file}")
                return connection

            # For default path, use sqlite3.connect directly (for test
            # compatibility)
            if not os.path.exists(db_file):
                logger.warning(f"Database file not found: {db_file}")
                return None

            # Use sqlite3 directly for test compatibility
            connection = sqlite3.connect(db_file)
            connection.row_factory = sqlite3.Row  # Match test expectations
            logger.info(f"Database connected: {db_file}")
            return connection

        except sqlite3.Error as e:
            # Re-raise SQL errors for test compatibility
            raise e
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return None


def get_driver(
    browser: str = "chrome",
    headless: bool = False,
    window_size: Optional[Tuple[int, int]] = None,
    db_path: str = None,
) -> Tuple[object, Optional[object]]:
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
        raise ValueError(f"Unsupported browser: {browser}")

    # Create database connection with optional custom path
    database = DatabaseFactory.create_database_connection(db_path)

    # Set implicit wait
    timeout = int(os.getenv("IMPLICIT_WAIT", "10"))
    driver.implicitly_wait(timeout)

    return driver, database


def create_headless_driver() -> Tuple[webdriver.Chrome, Optional[object]]:
    """Convenience method for creating headless drivers."""
    return get_driver(headless=True)


def cleanup_driver_and_database(
    driver: webdriver.Chrome, database: Optional[object]
) -> None:
    """Clean resource cleanup following DRY principle."""
    try:
        if driver:
            driver.quit()
            logger.info("Driver closed successfully")
    except Exception as e:
        logger.error(f"Error closing driver: {e}")

    try:
        if database and hasattr(database, "close"):
            database.close()
            logger.info("Database closed successfully")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
