"""
Simple Configuration - Working Version
Basic improvements to the original framework without breaking changes.
"""

import os
from pathlib import Path

# Import dotenv at module level so it can be mocked in tests
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class Settings:
    """Simple settings class without complex dependencies."""

    def __init__(self):
        # Load environment variables from .env file if it exists
        try:
            if load_dotenv is not None:
                load_dotenv()
        except ImportError:
            # Handle case where dotenv import fails
            pass
        # Load from environment or use defaults
        self.BROWSER = os.getenv("BROWSER", "chrome")
        self.HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
        self.TIMEOUT = int(os.getenv("TIMEOUT", "10"))
        self.SCREENSHOT_ON_FAILURE = (
            os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
        )

        # URLs
        self.BASE_URL = os.getenv("BASE_URL", "https://www.bing.com")
        self.API_BASE_URL = os.getenv(
            "API_BASE_URL",
            "https://jsonplaceholder.typicode.com",
        )
        self.SEARCH_URL = os.getenv("SEARCH_URL", "https://www.bing.com/search?q=test")

        # Test URLs for different testing scenarios
        self.TEST_API_URL = os.getenv("TEST_API_URL", "https://httpbin.org/json")
        self.TEST_HTML_URL = os.getenv("TEST_HTML_URL", "https://httpbin.org/html")
        self.EXAMPLE_URL = os.getenv("EXAMPLE_URL", "https://example.com")
        self.TEST_URL = os.getenv("TEST_URL", "https://test.com")
        self.API_TEST_URL = os.getenv("API_TEST_URL", "https://api.test.com/data")
        self.INVALID_URL = os.getenv(
            "INVALID_URL",
            "https://nonexistent-domain-12345.com",
        )

        # Test Data - Search Terms
        self.DEFAULT_SEARCH_TERM = os.getenv(
            "DEFAULT_SEARCH_TERM",
            "Python automation testing",
        )
        self.SELENIUM_SEARCH_TERM = os.getenv("SELENIUM_SEARCH_TERM", "Selenium Python")
        self.PERFORMANCE_SEARCH_TERM = os.getenv(
            "PERFORMANCE_SEARCH_TERM",
            "selenium testing performance",
        )
        self.PLAYWRIGHT_SEARCH_TERM = os.getenv(
            "PLAYWRIGHT_SEARCH_TERM",
            "Python automation testing playwright",
        )

        # Test Data - Lists
        search_terms_str = os.getenv(
            "SEARCH_TERMS_LIST",
            "Python automation,Selenium WebDriver,Test framework",
        )
        self.SEARCH_TERMS_LIST = [term.strip() for term in search_terms_str.split(",")]

        # Database
        self.DB_PATH = os.getenv("DB_PATH", "resources/chinook.db")

        # Test configuration
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Reporting configuration
        self.ENABLE_ALLURE = os.getenv("ENABLE_ALLURE", "true").lower() == "true"

        # Visual testing
        self.VISUAL_THRESHOLD = int(os.getenv("VISUAL_THRESHOLD", "1000"))
        self.SAVE_DIFF_IMAGES = os.getenv("SAVE_DIFF_IMAGES", "true").lower() == "true"

        # Paths
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.REPORTS_DIR = self.PROJECT_ROOT / os.getenv("REPORTS_DIR", "reports")
        self.SCREENSHOTS_DIR = self.PROJECT_ROOT / os.getenv(
            "SCREENSHOTS_DIR",
            "screenshots",
        )
        self.LOGS_DIR = self.PROJECT_ROOT / os.getenv("LOGS_DIR", "logs")

        # Create directories
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories."""
        for directory in [
            self.REPORTS_DIR,
            self.SCREENSHOTS_DIR,
            self.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
