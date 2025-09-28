"""
Simple Configuration - Working Version
Basic improvements to the original framework without breaking changes.
"""

import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not installed, that's okay - we'll use system env vars only
    pass


class Settings:
    """Simple settings class without complex dependencies."""

    def __init__(self):
        # Load from environment or use defaults
        self.BROWSER = os.getenv("BROWSER", "chrome")
        self.HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
        self.TIMEOUT = int(os.getenv("TIMEOUT", "10"))
        self.SCREENSHOT_ON_FAILURE = (
            os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"
        )

        # URLs
        self.BASE_URL = os.getenv("BASE_URL", "https://www.google.com")
        self.API_BASE_URL = os.getenv(
            "API_BASE_URL", "https://jsonplaceholder.typicode.com"
        )

        # Database
        self.DB_PATH = os.getenv("DB_PATH", "resources/chinook.db")

        # Test configuration
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        # Visual testing
        self.VISUAL_THRESHOLD = int(os.getenv("VISUAL_THRESHOLD", "1000"))
        self.SAVE_DIFF_IMAGES = os.getenv("SAVE_DIFF_IMAGES", "true").lower() == "true"

        # Paths
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.REPORTS_DIR = self.PROJECT_ROOT / os.getenv("REPORTS_DIR", "reports")
        self.SCREENSHOTS_DIR = self.PROJECT_ROOT / os.getenv(
            "SCREENSHOTS_DIR", "screenshots"
        )
        self.LOGS_DIR = self.PROJECT_ROOT / os.getenv("LOGS_DIR", "logs")

        # Create directories
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories."""
        for directory in [self.REPORTS_DIR, self.SCREENSHOTS_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
