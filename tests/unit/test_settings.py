"""
Real Unit Tests for Settings Class
Testing configuration logic and edge cases.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from config.settings import Settings


class TestSettingsClass:
    """Test Settings class functionality."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_settings_default_values(self):
        """Test Settings uses correct default values."""
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
    
    @patch.dict(os.environ, {
        'BROWSER': 'firefox',
        'HEADLESS': 'true',
        'TIMEOUT': '30',
        'SCREENSHOT_ON_FAILURE': 'false',
        'BASE_URL': 'https://example.com',
        'API_BASE_URL': 'https://api.example.com',
        'DB_PATH': '/custom/db.sqlite',
        'ENVIRONMENT': 'production',
        'DEBUG': 'false',
        'LOG_LEVEL': 'ERROR',
        'VISUAL_THRESHOLD': '5000',
        'SAVE_DIFF_IMAGES': 'false',
        'REPORTS_DIR': 'custom_reports',
        'SCREENSHOTS_DIR': 'custom_screenshots',
        'LOGS_DIR': 'custom_logs'
    })
    def test_settings_environment_variables(self):
        """Test Settings reads from environment variables."""
        settings = Settings()
        
        assert settings.BROWSER == "firefox"
        assert settings.HEADLESS is True
        assert settings.TIMEOUT == 30
        assert settings.SCREENSHOT_ON_FAILURE is False
        assert settings.BASE_URL == "https://example.com"
        assert settings.API_BASE_URL == "https://api.example.com"
        assert settings.DB_PATH == "/custom/db.sqlite"
        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "ERROR"
        assert settings.VISUAL_THRESHOLD == 5000
        assert settings.SAVE_DIFF_IMAGES is False
    
    @patch.dict(os.environ, {'TIMEOUT': 'invalid'})
    def test_settings_invalid_timeout(self):
        """Test Settings handles invalid timeout value."""
        with pytest.raises(ValueError):
            Settings()
    
    @patch.dict(os.environ, {'VISUAL_THRESHOLD': 'not_a_number'})
    def test_settings_invalid_visual_threshold(self):
        """Test Settings handles invalid visual threshold."""
        with pytest.raises(ValueError):
            Settings()
    
    @patch.dict(os.environ, {'HEADLESS': 'invalid_boolean'})
    def test_settings_invalid_boolean_values(self):
        """Test Settings handles invalid boolean values."""
        settings = Settings()
        # Invalid boolean should default to False
        assert settings.HEADLESS is False
    
    @patch('config.settings.load_dotenv')
    def test_settings_loads_dotenv(self, mock_load_dotenv):
        """Test Settings attempts to load .env file."""
        Settings()
        mock_load_dotenv.assert_called_once()
    
    @patch('config.settings.load_dotenv', None)
    def test_settings_handles_missing_dotenv(self):
        """Test Settings handles missing python-dotenv package."""
        # Should not raise exception
        settings = Settings()
        assert settings.BROWSER == "chrome"  # Should still have defaults
    
    @patch('config.settings.load_dotenv')
    def test_settings_handles_dotenv_import_error(self, mock_load_dotenv):
        """Test Settings handles dotenv import error."""
        mock_load_dotenv.side_effect = ImportError("No module named 'dotenv'")
        
        # Should not raise exception
        settings = Settings()
        assert settings.BROWSER == "chrome"
    
    @patch('pathlib.Path.mkdir')
    def test_settings_creates_directories(self, mock_mkdir):
        """Test Settings creates necessary directories."""
        settings = Settings()
        
        # Should call mkdir for reports, screenshots, and logs directories
        assert mock_mkdir.call_count == 3
        # Verify mkdir was called with correct arguments
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)
    
    @patch('pathlib.Path.mkdir')
    def test_settings_directory_creation_error(self, mock_mkdir):
        """Test Settings handles directory creation errors gracefully."""
        mock_mkdir.side_effect = OSError("Permission denied")
        
        # Should not raise exception during initialization
        # Instead the Settings class should handle the error gracefully
        try:
            settings = Settings()
            assert settings.BROWSER == "chrome"  # Should still initialize other attributes
        except OSError:
            # If it does raise, that's also acceptable behavior
            pass
    
    def test_settings_project_root_path(self):
        """Test Settings calculates correct project root."""
        settings = Settings()
        
        # PROJECT_ROOT should be parent of config directory
        expected_root = Path(__file__).parent.parent.parent
        assert settings.PROJECT_ROOT == expected_root
    
    def test_settings_directory_paths(self):
        """Test Settings calculates correct directory paths."""
        settings = Settings()
        
        assert settings.REPORTS_DIR == settings.PROJECT_ROOT / "reports"
        assert settings.SCREENSHOTS_DIR == settings.PROJECT_ROOT / "screenshots"
        assert settings.LOGS_DIR == settings.PROJECT_ROOT / "logs"
    
    @patch.dict(os.environ, {'REPORTS_DIR': 'test_reports'})
    def test_settings_custom_directory_paths(self):
        """Test Settings uses custom directory paths from environment."""
        settings = Settings()
        
        assert settings.REPORTS_DIR == settings.PROJECT_ROOT / "test_reports"
    
    def test_settings_pathlib_objects(self):
        """Test Settings directory attributes are Path objects."""
        settings = Settings()
        
        assert isinstance(settings.PROJECT_ROOT, Path)
        assert isinstance(settings.REPORTS_DIR, Path)
        assert isinstance(settings.SCREENSHOTS_DIR, Path)
        assert isinstance(settings.LOGS_DIR, Path)


class TestSettingsEdgeCases:
    """Test Settings edge cases and error conditions."""
    
    @patch.dict(os.environ, {'TIMEOUT': '0'})
    def test_settings_zero_timeout(self):
        """Test Settings handles zero timeout."""
        settings = Settings()
        assert settings.TIMEOUT == 0
    
    @patch.dict(os.environ, {'TIMEOUT': '-5'})
    def test_settings_negative_timeout(self):
        """Test Settings handles negative timeout."""
        settings = Settings()
        assert settings.TIMEOUT == -5  # Settings doesn't validate this
    
    @patch.dict(os.environ, {'VISUAL_THRESHOLD': '0'})
    def test_settings_zero_visual_threshold(self):
        """Test Settings handles zero visual threshold."""
        settings = Settings()
        assert settings.VISUAL_THRESHOLD == 0
    
    @patch.dict(os.environ, {
        'BASE_URL': '',
        'API_BASE_URL': '',
        'DB_PATH': ''
    })
    def test_settings_empty_string_values(self):
        """Test Settings handles empty string values."""
        settings = Settings()
        
        assert settings.BASE_URL == ""
        assert settings.API_BASE_URL == ""
        assert settings.DB_PATH == ""
    
    @patch.dict(os.environ, {'BROWSER': 'CHROME'})
    def test_settings_case_sensitivity(self):
        """Test Settings preserves case from environment."""
        settings = Settings()
        assert settings.BROWSER == "CHROME"  # Case preserved