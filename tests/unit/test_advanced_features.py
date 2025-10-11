import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

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
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from utils.error_handler import (
    ErrorClassifier,
    ErrorContext,
    RecoveryAction,
    RecoveryManager,
    RecoveryStrategy,
    SmartErrorHandler,
)
from utils.test_data_manager import DataManager
from utils.test_reporter import AdvancedTestReporter, Result

"""
Unit tests for framework components with advanced capabilities.
Validates data management, reporting, and error handling functionality.
"""


class TestTestDataManager:
    """Unit tests for TestDataManager."""

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


class TestAdvancedTestReporter:
    """Unit tests for AdvancedTestReporter."""

    def setup_method(self):
        """Setup test reporter with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.reporter = AdvancedTestReporter(self.temp_dir)

    def test_init_creates_directories(self):
        """Test that initialization creates report directories."""
        expected_dirs = ["json", "html", "trends", "analytics"]
        for dir_name in expected_dirs:
            assert_that((Path(self.temp_dir) / dir_name).exists(), is_(True))

    # ...existing code...
    """Test starting a test suite."""
    # ...existing code...
    def test_add_test_result(self):
        """Test adding test results to suite."""
        self.reporter.start_test_suite("Test_Suite", "local", "chrome")

        # Add passed test
        passed_result = Result(
            test_name="test_pass",
            status="PASSED",
            duration=2.5,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
        )
        self.reporter.add_test_result(passed_result)

        # Add passed test
        passed_result = Result(
            test_name="test_pass",
            status="PASSED",
            duration=2.5,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
        )
        self.reporter.add_test_result(passed_result)

        # Add failed test
        failed_result = Result(
            test_name="test_fail",
            status="FAILED",
            duration=1.8,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
            error_message="Test assertion failed",
        )
        self.reporter.add_test_result(failed_result)

        # Verify suite statistics
        suite = self.reporter.current_suite
        assert_that(suite.total_tests, equal_to(3))
        assert_that(suite.passed, equal_to(2))
        assert_that(suite.failed, equal_to(1))
        assert_that(suite.total_duration, equal_to(6.8))

        # Add a test result
        result = Result(
            test_name="test_json",
            status="PASSED",
            duration=1.5,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
        )
        self.reporter.add_test_result(result)

        # Generate report
        report_path = self.reporter.generate_json_report("test_report.json")

        # Verify file exists and contains expected data
        assert_that(Path(report_path).exists(), is_(True))

        with Path(report_path).open() as f:
            report_data = json.load(f)

        assert_that(report_data, has_key("suite_summary"))
        assert_that(report_data, has_key("metrics"))
        assert_that(report_data, has_key("test_results"))
        assert_that(report_data["suite_summary"]["suite_name"], equal_to("Test_Suite"))
        assert_that(len(report_data["test_results"]), equal_to(4))

    def test_generate_html_report(self):
        """Test HTML report generation."""
        self.reporter.start_test_suite("HTML_Test", "local", "chrome")

    # ...existing code...
        result = Result(
            test_name="test_html",
            status="PASSED",
            duration=2.0,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
        )
        self.reporter.add_test_result(result)

        # Generate report
        report_path = self.reporter.generate_html_report("test_report.html")

        # Verify file exists and contains HTML content
        assert_that(Path(report_path).exists(), is_(True))

        with Path(report_path).open() as f:
            html_content = f.read()

        assert_that(html_content, contains_string("<!DOCTYPE html>"))
        assert_that(html_content, contains_string("Test Execution Report"))
        assert_that(html_content, contains_string("HTML_Test"))
    def test_get_failure_patterns(self):
        """Test failure pattern analysis."""
        self.reporter.start_test_suite("Failure_Test", "local", "chrome")

        # Add failed tests with different error patterns
        timeout_result = Result(
            test_name="test_timeout",
            status="FAILED",
            duration=30.0,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
            error_message="TimeoutException: Element not found within timeout",
        )

        element_result = Result(
            test_name="test_element",
            status="FAILED",
            duration=5.0,
            timestamp=datetime.now(timezone.utc),
            environment="local",
            browser="chrome",
            error_message="NoSuchElementException: Unable to locate element",
        )

        self.reporter.add_test_result(timeout_result)
        self.reporter.add_test_result(element_result)

        # Analyze failure patterns
        patterns = self.reporter.get_failure_patterns()

        assert_that(patterns["total_failures"], equal_to(2))
        assert_that(patterns, has_key("error_patterns"))
        assert_that(patterns, has_key("most_failing_tests"))


class TestErrorClassifier:
    """Unit tests for ErrorClassifier."""

    def setup_method(self):
        """Setup error classifier."""
        self.classifier = ErrorClassifier()

    def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        error = TimeoutException("Element not found within timeout")
        context = ErrorContext(
            error_type="TimeoutException",
            error_message="Element not found within timeout",
            timestamp=datetime.now(timezone.utc),
            test_name="test_timeout",
            page_url="https://example.com",
        )

        classification = self.classifier.classify_error(error, context)

        assert_that(classification["error_type"], equal_to("TimeoutException"))
        assert_that(classification["classification"]["category"], equal_to("timeout"))
        assert_that(
            classification["classification"]["severity"].value,
            equal_to("medium"),
        )

    def test_classify_element_not_found_error(self):
        """Test classification of element not found errors."""
        error = NoSuchElementException("Unable to locate element")
        context = ErrorContext(
            error_type="NoSuchElementException",
            error_message="Unable to locate element",
            timestamp=datetime.now(timezone.utc),
            test_name="test_element",
            page_url="https://example.com",
        )

        classification = self.classifier.classify_error(error, context)

        assert_that(classification["error_type"], equal_to("NoSuchElementException"))
        assert_that(
            classification["classification"]["category"],
            equal_to("element_not_found"),
        )
        assert_that(
            classification["classification"]["severity"].value,
            equal_to("high"),
        )

    def test_classify_unknown_error(self):
        """Test classification of unknown errors."""
        error = ValueError("Unknown error type")
        context = ErrorContext(
            error_type="ValueError",
            error_message="Unknown error type",
            timestamp=datetime.now(timezone.utc),
            test_name="test_unknown",
            page_url="https://example.com",
        )

        classification = self.classifier.classify_error(error, context)

        assert_that(classification["error_type"], equal_to("ValueError"))
        assert_that(classification["classification"]["category"], equal_to("unknown"))
        assert_that(classification["confidence"], equal_to(0.3))


class TestRecoveryManager:
    """Unit tests for RecoveryManager."""

    def setup_method(self):
        """Setup recovery manager with mocks."""
        self.mock_driver_factory = Mock()
        self.recovery_manager = RecoveryManager(self.mock_driver_factory)

    def test_get_recovery_statistics_empty(self):
        """Test getting recovery statistics when no recoveries recorded."""
        stats = self.recovery_manager.get_recovery_statistics()
        assert_that(stats["message"], equal_to("No recovery attempts recorded"))

    def test_retry_recovery_success(self):
        """Test successful retry recovery."""
        mock_driver = Mock()
        error_context = ErrorContext(
            error_type="TimeoutException",
            error_message="Timeout occurred",
            timestamp=datetime.now(timezone.utc),
            test_name="test_retry",
            page_url="https://example.com",
        )

        # Mock success validation
        success_validation = Mock(return_value=True)
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_attempts=2,
            wait_time=0.1,
            success_validation=success_validation,
        )

        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver,
            error_context,
            recovery_action,
        )

        assert_that(result, is_(True))
        assert_that(len(self.recovery_manager.recovery_history), equal_to(1))
        assert_that(self.recovery_manager.recovery_history[0]["success"], is_(True))

    def test_retry_recovery_failure(self):
        """Test failed retry recovery."""
        mock_driver = Mock()
        error_context = ErrorContext(
            error_type="TimeoutException",
            error_message="Timeout occurred",
            timestamp=datetime.now(timezone.utc),
            test_name="test_retry_fail",
            page_url="https://example.com",
        )

        # Mock failing validation
        success_validation = Mock(return_value=False)
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_attempts=2,
            wait_time=0.1,
            success_validation=success_validation,
        )

        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver,
            error_context,
            recovery_action,
        )

        assert_that(result, is_(False))
        assert_that(len(self.recovery_manager.recovery_history), equal_to(1))
        assert_that(self.recovery_manager.recovery_history[0]["success"], is_(False))

    @patch("selenium.webdriver.support.ui.WebDriverWait")
    def test_refresh_recovery(self, mock_wait):
        """Test page refresh recovery."""
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.execute_script.return_value = "complete"  # Mock document.readyState

        # Setup WebDriverWait mock
        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = True
        mock_wait.return_value = mock_wait_instance

        error_context = ErrorContext(
            error_type="StaleElementReferenceException",
            error_message="Element is stale",
            timestamp=datetime.now(timezone.utc),
            test_name="test_refresh",
            page_url="https://example.com",
        )

        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.REFRESH,
            max_attempts=1,
            wait_time=1.0,
        )

        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver,
            error_context,
            recovery_action,
        )

        # Verify refresh was called
        mock_driver.refresh.assert_called_once()
        # Verify document ready state was checked
        mock_driver.execute_script.assert_called_with("return document.readyState")
        assert_that(result, is_(True))

    def test_get_recovery_statistics_with_data(self):
        """Test getting recovery statistics with recorded data."""
        # Manually add recovery records
        self.recovery_manager.recovery_history = [
            {
                "strategy": "retry",
                "success": True,
                "duration": 1.5,
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "strategy": "retry",
                "success": False,
                "duration": 2.0,
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "strategy": "refresh",
                "success": True,
                "duration": 3.0,
                "timestamp": datetime.now(timezone.utc),
            },
        ]

        stats = self.recovery_manager.get_recovery_statistics()

        assert_that(stats["total_recovery_attempts"], equal_to(3))
        assert_that(stats["successful_recoveries"], equal_to(2))
        assert_that(stats["success_rate"], equal_to(66.67))
        assert_that(stats["average_recovery_time"], equal_to(2.17))

        # Check strategy-specific stats
        strategy_stats = stats["strategy_performance"]
        assert_that(strategy_stats["retry"]["total"], equal_to(2))
        assert_that(strategy_stats["retry"]["successful"], equal_to(1))
        assert_that(strategy_stats["refresh"]["total"], equal_to(1))
        assert_that(strategy_stats["refresh"]["successful"], equal_to(1))


class TestSmartErrorHandler:
    """Unit tests for SmartErrorHandler."""

    def setup_method(self):
        """Setup smart error handler with mocks."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = SmartErrorHandler(screenshots_dir=self.temp_dir)

    def test_init_creates_screenshots_dir(self):
        """Test that initialization creates screenshots directory."""
        assert_that(Path(self.temp_dir).exists(), is_(True))

    @patch("utils.error_handler.SmartErrorHandler._capture_error_screenshot")
    def test_handle_error_with_recovery(self, mock_screenshot):
        """Test error handling with successful recovery."""
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.get_log.return_value = []
        mock_screenshot.return_value = "/path/to/screenshot.png"

        # Mock successful recovery
        with patch.object(
            self.error_handler.recovery_manager,
            "execute_recovery",
        ) as mock_recovery:
            mock_recovery.return_value = True

            # Use a recognizable error type for the classifier
            error = Exception("TimeoutException: Element not found after timeout")
            result = self.error_handler.handle_error(error, mock_driver, "test_name")

            assert_that(result, is_(True))
            mock_recovery.assert_called_once()

    @patch("utils.error_handler.SmartErrorHandler._capture_error_screenshot")
    def test_handle_error_with_failed_recovery(self, mock_screenshot):
        """Test error handling with failed recovery."""
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.get_log.return_value = []
        mock_screenshot.return_value = "/path/to/screenshot.png"

        # Mock failed recovery
        with patch.object(
            self.error_handler.recovery_manager,
            "execute_recovery",
        ) as mock_recovery:
            mock_recovery.return_value = False

            # Use a recognizable error type for the classifier
            error = Exception("NoSuchElementException: Unable to locate element")
            result = self.error_handler.handle_error(error, mock_driver, "test_name")

            assert_that(result, is_(False))
            mock_recovery.assert_called_once()

    def test_capture_error_screenshot_success(self):
        """Test successful screenshot capture."""
        mock_driver = Mock()

        # Setup mock to simulate successful screenshot
        screenshot_path = str(Path(self.temp_dir) / "test_screenshot.png")
        mock_driver.save_screenshot.return_value = True

        # Create a dummy image file to simulate screenshot
        with Path(screenshot_path).open("w") as f:
            f.write("fake image data")

        # Mock the save_screenshot to create the file
        def mock_save_screenshot(path):
            with Path(path).open("w") as f:
                f.write("fake image data")
            return True

        mock_driver.save_screenshot = mock_save_screenshot

        result = self.error_handler._capture_error_screenshot(mock_driver, "test_name")  # noqa: SLF001

        assert_that(result, is_(not_none()))
        assert_that(result, contains_string("error_test_name_"))
        assert_that(result, ends_with(".png"))

    def test_capture_error_screenshot_failure(self):
        """Test screenshot capture failure."""
        mock_driver = Mock()
        mock_driver.save_screenshot.side_effect = Exception("Screenshot failed")

        result = self.error_handler._capture_error_screenshot(mock_driver, "test_name")  # noqa: SLF001

        assert_that(result, is_(none()))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
