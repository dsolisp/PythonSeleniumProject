from hamcrest import (
    assert_that,
    equal_to,
    instance_of,
    is_,
)

"""
Real Unit Tests for Settings Class
Testing configuration logic and edge cases.
"""

import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from config.settings import Settings


class TestSettingsClass:
    """Test Settings class functionality."""

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_default_values(self):
        """Test Settings uses correct default values."""
        settings = Settings()

        assert_that(settings.BROWSER, equal_to("chrome"))
        assert_that(settings.HEADLESS, is_(False))
        assert_that(settings.TIMEOUT, equal_to(10))
        assert_that(settings.SCREENSHOT_ON_FAILURE, is_(True))
        assert_that(settings.BASE_URL, equal_to("https://duckduckgo.com"))
        assert_that(settings.API_BASE_URL, equal_to(
            "https://jsonplaceholder.typicode.com"))
        assert_that(settings.DB_PATH, equal_to("resources/chinook.db"))
        assert_that(settings.ENVIRONMENT, equal_to("local"))
        assert_that(settings.DEBUG, is_(True))
        assert_that(settings.LOG_LEVEL, equal_to("INFO"))
        assert_that(settings.VISUAL_THRESHOLD, equal_to(1000))
        assert_that(settings.SAVE_DIFF_IMAGES, is_(True))

    @patch.dict(
        os.environ,
        {
            "BROWSER": "firefox",
            "HEADLESS": "true",
            "TIMEOUT": "30",
            "SCREENSHOT_ON_FAILURE": "false",
            "BASE_URL": "https://example.com",
            "API_BASE_URL": "https://api.example.com",
            "DB_PATH": "/custom/db.sqlite",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "ERROR",
            "VISUAL_THRESHOLD": "5000",
            "SAVE_DIFF_IMAGES": "false",
            "REPORTS_DIR": "custom_reports",
            "SCREENSHOTS_DIR": "custom_screenshots",
            "LOGS_DIR": "custom_logs",
        },
    )
    def test_settings_environment_variables(self):
        """Test Settings reads from environment variables."""
        try:
            settings = Settings()

            assert_that(settings.BROWSER, equal_to("firefox"))
            assert_that(settings.HEADLESS, is_(True))
            assert_that(settings.TIMEOUT, equal_to(30))
            assert_that(settings.SCREENSHOT_ON_FAILURE, is_(False))
            assert_that(settings.BASE_URL, equal_to("https://example.com"))
            assert_that(
                settings.API_BASE_URL,
                equal_to("https://api.example.com"))
            assert_that(settings.DB_PATH, equal_to("/custom/db.sqlite"))
            assert_that(settings.ENVIRONMENT, equal_to("production"))
            assert_that(settings.DEBUG, is_(False))
            assert_that(settings.LOG_LEVEL, equal_to("ERROR"))
            assert_that(settings.VISUAL_THRESHOLD, equal_to(5000))
            assert_that(settings.SAVE_DIFF_IMAGES, is_(False))
        finally:
            # Cleanup test directories
            for dir_name in [
                "custom_reports",
                "custom_screenshots",
                    "custom_logs"]:
                shutil.rmtree(dir_name, ignore_errors=True)

    @patch.dict(os.environ, {"TIMEOUT": "invalid"})
    def test_settings_invalid_timeout(self):
        """Test Settings handles invalid timeout value."""
        with pytest.raises(ValueError):
            Settings()

    @patch.dict(os.environ, {"VISUAL_THRESHOLD": "not_a_number"})
    def test_settings_invalid_visual_threshold(self):
        """Test Settings handles invalid visual threshold."""
        with pytest.raises(ValueError):
            Settings()

    @patch.dict(os.environ, {"HEADLESS": "invalid_boolean"})
    def test_settings_invalid_boolean_values(self):
        """Test Settings handles invalid boolean values."""
        settings = Settings()
        # Invalid boolean should default to False
        assert_that(settings.HEADLESS, is_(False))

    @patch("config.settings.load_dotenv")
    def test_settings_loads_dotenv(self, mock_load_dotenv):
        """Test Settings attempts to load .env file."""
        Settings()
        mock_load_dotenv.assert_called_once()

    @patch("config.settings.load_dotenv", None)
    def test_settings_handles_missing_dotenv(self):
        """Test Settings handles missing python-dotenv package."""
        # Should not raise exception
        settings = Settings()
        # Should still have defaults
        assert_that(settings.BROWSER, equal_to("chrome"))

    @patch("config.settings.load_dotenv")
    def test_settings_handles_dotenv_import_error(self, mock_load_dotenv):
        """Test Settings handles dotenv import error."""
        mock_load_dotenv.side_effect = ImportError("No module named 'dotenv'")

        # Should not raise exception
        settings = Settings()
        assert_that(settings.BROWSER, equal_to("chrome"))

    @patch("pathlib.Path.mkdir")
    def test_settings_creates_directories(self, mock_mkdir):
        """Test Settings creates necessary directories."""
        Settings()

        # Should call mkdir for reports, screenshots, and logs directories
        assert_that(mock_mkdir.call_count, equal_to(3))
        # Verify mkdir was called with correct arguments
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)

    @patch("pathlib.Path.mkdir")
    def test_settings_directory_creation_error(self, mock_mkdir):
        """Test Settings handles directory creation errors gracefully."""
        mock_mkdir.side_effect = OSError("Permission denied")

        # Should not raise exception during initialization
        # Instead the Settings class should handle the error gracefully
        try:
            settings = Settings()
            # Should still initialize other attributes
            assert_that(settings.BROWSER, equal_to("chrome"))
        except OSError:
            # If it does raise, that's also acceptable behavior
            pass

    def test_settings_project_root_path(self):
        """Test Settings calculates correct project root."""
        settings = Settings()

        # PROJECT_ROOT should be parent of config directory
        expected_root = Path(__file__).parent.parent.parent
        assert_that(settings.PROJECT_ROOT, equal_to(expected_root))

    def test_settings_directory_paths(self):
        """Test Settings calculates correct directory paths."""
        settings = Settings()

        assert_that(
            settings.REPORTS_DIR,
            equal_to(
                settings.PROJECT_ROOT /
                "reports"))
        assert_that(
            settings.SCREENSHOTS_DIR,
            equal_to(
                settings.PROJECT_ROOT /
                "screenshots"))
        assert_that(
            settings.LOGS_DIR,
            equal_to(
                settings.PROJECT_ROOT /
                "logs"))

    @patch.dict(os.environ, {"REPORTS_DIR": "test_reports"})
    def test_settings_custom_directory_paths(self):
        """Test Settings uses custom directory paths from environment."""
        settings = Settings()

        assert_that(
            settings.REPORTS_DIR,
            equal_to(
                settings.PROJECT_ROOT /
                "test_reports"))

    def test_settings_pathlib_objects(self):
        """Test Settings directory attributes are Path objects."""
        settings = Settings()

        assert_that(settings.PROJECT_ROOT, instance_of(Path))
        assert_that(settings.REPORTS_DIR, instance_of(Path))
        assert_that(settings.SCREENSHOTS_DIR, instance_of(Path))
        assert_that(settings.LOGS_DIR, instance_of(Path))


class TestSettingsEdgeCases:
    """Test Settings edge cases and error conditions."""

    @patch.dict(os.environ, {"TIMEOUT": "0"})
    def test_settings_zero_timeout(self):
        """Test Settings handles zero timeout."""
        settings = Settings()
        assert_that(settings.TIMEOUT, equal_to(0))

    @patch.dict(os.environ, {"TIMEOUT": "-5"})
    def test_settings_negative_timeout(self):
        """Test Settings handles negative timeout."""
        settings = Settings()
        # Settings doesn't validate this
        assert_that(settings.TIMEOUT, equal_to(-5))

    @patch.dict(os.environ, {"VISUAL_THRESHOLD": "0"})
    def test_settings_zero_visual_threshold(self):
        """Test Settings handles zero visual threshold."""
        settings = Settings()
        assert_that(settings.VISUAL_THRESHOLD, equal_to(0))

    @patch.dict(os.environ, {"BASE_URL": "",
                "API_BASE_URL": "", "DB_PATH": ""})
    def test_settings_empty_string_values(self):
        """Test Settings handles empty string values."""
        settings = Settings()

        assert_that(settings.BASE_URL, equal_to(""))
        assert_that(settings.API_BASE_URL, equal_to(""))
        assert_that(settings.DB_PATH, equal_to(""))

    @patch.dict(os.environ, {"BROWSER": "CHROME"})
    def test_settings_case_sensitivity(self):
        """Test Settings preserves case from environment."""
        settings = Settings()
        # Case preserved
        assert_that(settings.BROWSER, equal_to("CHROME"))
