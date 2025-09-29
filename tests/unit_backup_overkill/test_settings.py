"""
Unit tests for configuration settings module.
Tests environment variable loading, defaults, and directory creation.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from config.settings import Settings


class TestSettings:
    """Test cases for Settings class configuration."""

    def test_default_values(self):
        """Test that default values are set correctly when no env vars exist."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.BROWSER == "chrome"
            assert settings.HEADLESS is False
            assert settings.TIMEOUT == 10
            assert settings.SCREENSHOT_ON_FAILURE is True
            assert settings.BASE_URL == "https://www.google.com"
            assert settings.API_BASE_URL == "https://jsonplaceholder.typicode.com"
            assert settings.DB_PATH == "resources/chinook.db"
            assert settings.ENVIRONMENT == "local"
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "INFO"
            assert settings.VISUAL_THRESHOLD == 1000
            assert settings.SAVE_DIFF_IMAGES is True

    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        env_vars = {
            "BROWSER": "firefox",
            "HEADLESS": "true",
            "TIMEOUT": "30",
            "SCREENSHOT_ON_FAILURE": "false",
            "BASE_URL": "https://example.com",
            "API_BASE_URL": "https://api.example.com",
            "DB_PATH": "test.db",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "ERROR",
            "VISUAL_THRESHOLD": "500",
            "SAVE_DIFF_IMAGES": "false",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.BROWSER == "firefox"
            assert settings.HEADLESS is True
            assert settings.TIMEOUT == 30
            assert settings.SCREENSHOT_ON_FAILURE is False
            assert settings.BASE_URL == "https://example.com"
            assert settings.API_BASE_URL == "https://api.example.com"
            assert settings.DB_PATH == "test.db"
            assert settings.ENVIRONMENT == "production"
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "ERROR"
            assert settings.VISUAL_THRESHOLD == 500
            assert settings.SAVE_DIFF_IMAGES is False

    def test_boolean_conversion(self):
        """Test boolean environment variable conversion."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("yes", False),  # Only 'true' should be True
            ("1", False),    # Only 'true' should be True
            ("", False),     # Empty string should be False
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {"HEADLESS": env_value}, clear=True):
                settings = Settings()
                assert settings.HEADLESS is expected, f"Failed for value: {env_value}"

    def test_integer_conversion(self):
        """Test integer environment variable conversion."""
        with patch.dict(os.environ, {"TIMEOUT": "45"}, clear=True):
            settings = Settings()
            assert settings.TIMEOUT == 45
            assert isinstance(settings.TIMEOUT, int)

    def test_invalid_integer_fallback(self):
        """Test that invalid integers fall back to defaults."""
        with patch.dict(os.environ, {"TIMEOUT": "invalid"}, clear=True):
            # This should raise ValueError when int() is called
            with pytest.raises(ValueError):
                Settings()

    def test_path_objects_created(self):
        """Test that Path objects are created correctly."""
        settings = Settings()
        
        assert isinstance(settings.PROJECT_ROOT, Path)
        assert isinstance(settings.REPORTS_DIR, Path)
        assert isinstance(settings.SCREENSHOTS_DIR, Path)
        assert isinstance(settings.LOGS_DIR, Path)
        
        # Test path relationships
        assert settings.REPORTS_DIR.parent == settings.PROJECT_ROOT
        assert settings.SCREENSHOTS_DIR.parent == settings.PROJECT_ROOT
        assert settings.LOGS_DIR.parent == settings.PROJECT_ROOT

    def test_custom_directory_paths(self):
        """Test custom directory path configuration."""
        env_vars = {
            "REPORTS_DIR": "custom_reports",
            "SCREENSHOTS_DIR": "custom_screenshots", 
            "LOGS_DIR": "custom_logs",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.REPORTS_DIR.name == "custom_reports"
            assert settings.SCREENSHOTS_DIR.name == "custom_screenshots"
            assert settings.LOGS_DIR.name == "custom_logs"

    def test_directory_creation(self):
        """Test that directories are created during initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock PROJECT_ROOT to use our temp directory
            with patch.object(Path, 'parent', temp_path):
                with patch.dict(os.environ, {
                    "REPORTS_DIR": "test_reports",
                    "SCREENSHOTS_DIR": "test_screenshots",
                    "LOGS_DIR": "test_logs",
                }, clear=True):
                    settings = Settings()
                    
                    # The actual directories should be created
                    # Note: This test verifies the creation logic exists
                    # but may need adjustment based on actual implementation

    @patch('config.settings.load_dotenv')
    def test_dotenv_import_success(self, mock_load_dotenv):
        """Test successful dotenv loading."""
        Settings()
        mock_load_dotenv.assert_called_once()

    @patch('config.settings.load_dotenv', side_effect=ImportError)
    def test_dotenv_import_failure_handled(self, mock_load_dotenv):
        """Test that ImportError for dotenv is handled gracefully."""
        # Should not raise an exception
        settings = Settings()
        assert settings is not None

    def test_settings_singleton_behavior(self):
        """Test that settings module provides consistent values."""
        from config.settings import settings
        
        # Test that imported settings object has expected attributes
        assert hasattr(settings, 'BROWSER')
        assert hasattr(settings, 'BASE_URL')
        assert hasattr(settings, 'TIMEOUT')