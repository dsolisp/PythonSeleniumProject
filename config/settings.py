from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseSettings, Field, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Environment(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Centralized configuration management for the test automation framework."""
    
    # Environment Configuration
    environment: Environment = Environment.LOCAL
    debug: bool = True
    log_level: LogLevel = LogLevel.INFO
    
    # Project Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    reports_dir: Path = Field(default_factory=lambda: Path("reports"))
    screenshots_dir: Path = Field(default_factory=lambda: Path("screenshots"))
    test_data_dir: Path = Field(default_factory=lambda: Path("test_data"))
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    
    # Browser Configuration
    default_browser: BrowserType = BrowserType.CHROME
    headless: bool = False
    browser_timeout: int = 30
    implicit_wait: int = 10
    explicit_wait: int = 20
    page_load_timeout: int = 30
    window_maximize: bool = True
    
    # Test Execution Configuration
    parallel_workers: int = 4
    max_retries: int = 3
    retry_delay: int = 2
    screenshot_on_failure: bool = True
    video_recording: bool = False
    
    # Database Configuration
    db_type: str = "sqlite"
    db_file: str = "resources/chinook.db"
    db_pool_size: int = 5
    db_timeout: int = 30
    
    # API Configuration
    api_base_url: str = "https://jsonplaceholder.typicode.com"
    api_timeout: int = 30
    api_retry_count: int = 3
    
    # Visual Testing Configuration
    visual_threshold: float = 0.1
    save_diff_images: bool = True
    visual_comparison_engine: str = "pixelmatch"
    
    # Reporting Configuration
    generate_html_report: bool = True
    generate_allure_report: bool = True
    generate_json_report: bool = True
    report_retention_days: int = 30
    
    # Security Configuration
    encrypt_sensitive_data: bool = True
    mask_sensitive_logs: bool = True
    
    # Performance Configuration
    performance_monitoring: bool = False
    memory_profiling: bool = False
    
    # Notification Configuration
    slack_webhook_url: Optional[str] = None
    teams_webhook_url: Optional[str] = None
    email_notifications: bool = False
    
    # Cloud Testing Configuration
    browserstack_username: Optional[str] = None
    browserstack_access_key: Optional[str] = None
    sauce_labs_username: Optional[str] = None
    sauce_labs_access_key: Optional[str] = None
    
    # Mobile Testing Configuration
    appium_server_url: str = "http://localhost:4723"
    android_device_name: Optional[str] = None
    ios_device_name: Optional[str] = None
    app_path: Optional[str] = None
    
    @validator('parallel_workers')
    def validate_parallel_workers(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Parallel workers must be between 1 and 20')
        return v
    
    @validator('visual_threshold')
    def validate_visual_threshold(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Visual threshold must be between 0 and 1')
        return v
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.reports_dir,
            self.screenshots_dir,
            self.test_data_dir,
            self.logs_dir,
            self.reports_dir / "html",
            self.reports_dir / "json",
            self.reports_dir / "allure-results",
            self.reports_dir / "coverage",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Create necessary directories on import
settings.create_directories()


def get_browser_options(browser_type: BrowserType, additional_options: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get browser-specific options based on configuration."""
    options = {
        'headless': settings.headless,
        'window_maximize': settings.window_maximize,
        'page_load_timeout': settings.page_load_timeout,
        'implicit_wait': settings.implicit_wait
    }
    
    if additional_options:
        options['additional_arguments'] = additional_options
    
    return options


def get_database_config() -> Dict[str, Any]:
    """Get database configuration."""
    return {
        'db_type': settings.db_type,
        'db_file': settings.db_file,
        'pool_size': settings.db_pool_size,
        'timeout': settings.db_timeout
    }


def get_api_config() -> Dict[str, Any]:
    """Get API configuration."""
    return {
        'base_url': settings.api_base_url,
        'timeout': settings.api_timeout,
        'retry_count': settings.api_retry_count
    }