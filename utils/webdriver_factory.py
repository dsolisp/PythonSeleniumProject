"""
WebDriver and Database factory classes for test automation.
"""

import logging
import os
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import utils.sql_connection as sql_util

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


class DatabaseFactory:
    """
    Creates and manages database connections.
    """

    @staticmethod
    def create_database_connection(db_path: str = None) -> Optional[object]:
        """Create database connection with error handling."""
        try:
            db_file = db_path or os.getenv("DB_PATH", "resources/chinook.db")

            if not os.path.exists(db_file):
                logger.warning(f"Database file not found: {db_file}")
                return None

            connection = sql_util.get_connection(db_file)
            logger.info(f"Database connected: {db_file}")
            return connection

        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            return None


def get_driver(
    browser: str = "chrome",
    headless: bool = False,
    window_size: Optional[Tuple[int, int]] = None,
) -> Tuple[webdriver.Chrome, Optional[object]]:
    """
    Factory function that creates WebDriver and Database instances.
    """
    if browser.lower() != "chrome":
        raise ValueError(f"Only Chrome supported currently. Requested: {browser}")

    # Create driver and database using specialized factories
    driver = WebDriverFactory.create_chrome_driver(headless, window_size)
    database = DatabaseFactory.create_database_connection()

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
