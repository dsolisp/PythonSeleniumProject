"""
Simple Enhanced Configuration - Working Version
Basic improvements to the original framework without breaking changes.
"""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Simple settings class without complex dependencies."""
    
    def __init__(self):
        # Load from environment or use defaults
        self.BROWSER = os.getenv('BROWSER', 'chrome')
        self.HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'
        self.TIMEOUT = int(os.getenv('TIMEOUT', '10'))
        self.SCREENSHOT_ON_FAILURE = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
        
        # Paths
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.REPORTS_DIR = self.PROJECT_ROOT / 'reports'
        self.SCREENSHOTS_DIR = self.PROJECT_ROOT / 'screenshots'
        self.LOGS_DIR = self.PROJECT_ROOT / 'logs'
        
        # Create directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories."""
        for directory in [self.REPORTS_DIR, self.SCREENSHOTS_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()