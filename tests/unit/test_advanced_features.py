"""
Unit tests for framework components with advanced capabilities.
Validates data management and error handling functionality.
"""

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
from hamcrest import (
    assert_that,
    contains_string,
    ends_with,
    equal_to,
    has_key,
    is_,
    none,
    not_none,
)

from utils.error_handler import SmartErrorHandler
from utils.test_data_manager import DataManager


class TestDataManagerTests:
    """Unit tests for DataManager."""

    def setup_method(self):
        """Setup test data manager with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataManager(self.temp_dir)

    def test_load_test_data_json(self):
        """Test loading JSON test data."""
        test_data = {"test_key": "test_value", "number": 42}
        json_file = Path(self.temp_dir) / "test_data.json"
        with Path(json_file).open("w") as f:
            json.dump(test_data, f)
        # Load and verify
        loaded_data = self.data_manager.load_test_data("test_data")
        assert_that(loaded_data, equal_to(test_data))

    def test_load_test_data_caching(self):
        """Test that data is cached after first load."""
        test_data = {"cached": True}
        json_file = Path(self.temp_dir) / "test_data.json"
        with Path(json_file).open("w") as f:
            json.dump(test_data, f)
        # Load twice
        data1 = self.data_manager.load_test_data("test_data")
        data2 = self.data_manager.load_test_data("test_data")
        assert_that(data1, equal_to(data2))
        assert_that(self.data_manager._cache, has_key("test_data_default"))  # noqa: SLF001

    def test_get_search_scenarios(self):
        """Test getting search scenarios."""
        test_data = {
            "search_scenarios": [
                {"name": "test1", "search_term": "python"},
                {"name": "test2", "search_term": "selenium"},
            ],
        }
        json_file = Path(self.temp_dir) / "test_data.json"
        with Path(json_file).open("w") as f:
            json.dump(test_data, f)
        scenarios = self.data_manager.get_search_scenarios()
        assert_that(len(scenarios), equal_to(2))
        assert_that(scenarios[0]["name"], equal_to("test1"))
        assert_that(scenarios[1]["search_term"], equal_to("selenium"))

    def test_get_user_accounts_filtered_by_role(self):
        """Test getting user accounts filtered by role."""
        test_data = {
            "user_accounts": [
                {"username": "admin1", "role": "admin"},
                {"username": "user1", "role": "standard"},
                {"username": "admin2", "role": "admin"},
            ],
        }
        json_file = Path(self.temp_dir) / "test_data.json"
        with Path(json_file).open("w") as f:
            json.dump(test_data, f)
        admin_accounts = self.data_manager.get_user_accounts("admin")
        assert_that(len(admin_accounts), equal_to(2))
        assert_that(all(acc["role"] == "admin" for acc in admin_accounts), is_(True))
        standard_accounts = self.data_manager.get_user_accounts("standard")
        assert_that(len(standard_accounts), equal_to(1))
        assert_that(standard_accounts[0]["username"], equal_to("user1"))
        """Test dynamic search data generation."""
        search_data = self.data_manager.generate_search_data(3)

        assert_that(len(search_data), equal_to(3))
        for scenario in search_data:
            assert_that(scenario, has_key("name"))
            assert_that(scenario, has_key("search_term"))
            assert_that(scenario, has_key("expected_results_count"))
            assert_that(scenario["generated"], is_(True))

    def test_validate_data_schema(self):
        """Test data schema validation."""
        # Valid search scenario
        valid_scenario = {"name": "test_search", "search_term": "python testing"}
        assert_that(
            self.data_manager.validate_data_schema(valid_scenario, "search_scenario"),
            is_(True),
        )

        # Invalid search scenario (missing required field)
        invalid_scenario = {"search_term": "python testing"}  # Missing 'name'
        assert_that(
            self.data_manager.validate_data_schema(invalid_scenario, "search_scenario"),
            is_(False),
        )

        # Unknown schema
        assert_that(
            self.data_manager.validate_data_schema(valid_scenario, "unknown_schema"),
            is_(False),
        )

    def test_cleanup_old_results(self):
        """Test cleanup of old result files."""
        # Create results directory and old files
        results_dir = Path(self.temp_dir) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Create old file (modify timestamp to be old)
        old_file = results_dir / "old_result.json"
        old_file.write_text('{"old": true}')

        # Modify file timestamp to be 35 days old
        old_time = datetime.now(timezone.utc) - timedelta(days=35)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

        # Create recent file
        recent_file = results_dir / "recent_result.json"
        recent_file.write_text('{"recent": true}')

        # Run cleanup (keep files from last 30 days)
        self.data_manager.cleanup_old_results(30)

        # Verify old file is gone, recent file remains
        assert_that(old_file.exists(), is_(False))
        assert_that(recent_file.exists(), is_(True))


class TestSmartErrorHandler:
    """Unit tests for SmartErrorHandler (simplified version)."""

    def setup_method(self):
        """Setup smart error handler with mocks."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = SmartErrorHandler(screenshots_dir=self.temp_dir)

    def test_init_creates_screenshots_dir(self):
        """Test that initialization creates screenshots directory."""
        assert_that(Path(self.temp_dir).exists(), is_(True))

    def test_handle_error_returns_false(self):
        """Test that simplified handler logs error and returns False."""
        mock_driver = Mock()
        mock_driver.save_screenshot.return_value = True

        error = Exception("TimeoutException: Element not found")
        result = self.error_handler.handle_error(error, mock_driver, "test_name")

        # Simplified handler always returns False (no automatic recovery)
        assert_that(result, is_(False))

    def test_handle_error_captures_screenshot(self):
        """Test that handle_error captures a screenshot."""
        mock_driver = Mock()

        def mock_save_screenshot(path):
            with Path(path).open("w") as f:
                f.write("fake image data")
            return True

        mock_driver.save_screenshot = mock_save_screenshot

        error = Exception("Test error")
        self.error_handler.handle_error(error, mock_driver, "test_screenshot")

        # Check screenshot was created
        screenshots = list(Path(self.temp_dir).glob("error_test_screenshot_*.png"))
        assert_that(len(screenshots), equal_to(1))

    def test_screenshot_service_capture_success(self):
        """Test successful screenshot capture via ScreenshotService."""
        mock_driver = Mock()

        def mock_save_screenshot(path):
            with Path(path).open("w") as f:
                f.write("fake image data")
            return True

        mock_driver.save_screenshot = mock_save_screenshot

        result = self.error_handler.screenshot_service.capture(mock_driver, "test_name")

        assert_that(result, is_(not_none()))
        assert_that(result, contains_string("error_test_name_"))
        assert_that(result, ends_with(".png"))

    def test_screenshot_service_capture_failure(self):
        """Test screenshot capture failure via ScreenshotService."""
        mock_driver = Mock()
        mock_driver.save_screenshot.side_effect = Exception("Screenshot failed")

        result = self.error_handler.screenshot_service.capture(mock_driver, "test_name")

        assert_that(result, is_(none()))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
