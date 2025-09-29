"""
Unit tests for framework components with advanced capabilities.
Validates data management, reporting, and error handling functionality.
"""

import pytest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from utils.test_data_manager import TestDataManager, TestDataSet
from utils.test_reporter import AdvancedTestReporter, TestResult, TestSuite
from utils.error_handler import ErrorClassifier, RecoveryManager, SmartErrorHandler, ErrorContext


class TestTestDataManager:
    """Unit tests for TestDataManager."""

    def setup_method(self):
        """Setup test data manager with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = TestDataManager(self.temp_dir)

    def test_init_creates_directory(self):
        """Test that initialization creates data directory."""
        assert Path(self.temp_dir).exists()
        assert self.data_manager.data_dir == Path(self.temp_dir)

    def test_load_test_data_json(self):
        """Test loading JSON test data."""
        # Create test JSON file
        test_data = {"test_key": "test_value", "number": 42}
        json_file = Path(self.temp_dir) / "test_data.json"
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load and verify
        loaded_data = self.data_manager.load_test_data("test_data")
        assert loaded_data == test_data

    def test_load_test_data_caching(self):
        """Test that data is cached after first load."""
        # Create test file
        test_data = {"cached": True}
        json_file = Path(self.temp_dir) / "test_data.json"
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load twice
        data1 = self.data_manager.load_test_data("test_data")
        data2 = self.data_manager.load_test_data("test_data")
        
        assert data1 == data2
        assert "test_data_default" in self.data_manager._cache

    def test_get_search_scenarios(self):
        """Test getting search scenarios."""
        # Create test data with search scenarios
        test_data = {
            "search_scenarios": [
                {"name": "test1", "search_term": "python"},
                {"name": "test2", "search_term": "selenium"}
            ]
        }
        json_file = Path(self.temp_dir) / "test_data.json"
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        scenarios = self.data_manager.get_search_scenarios()
        assert len(scenarios) == 2
        assert scenarios[0]["name"] == "test1"
        assert scenarios[1]["search_term"] == "selenium"

    def test_get_user_accounts_filtered_by_role(self):
        """Test getting user accounts filtered by role."""
        test_data = {
            "user_accounts": [
                {"username": "admin1", "role": "admin"},
                {"username": "user1", "role": "standard"},
                {"username": "admin2", "role": "admin"}
            ]
        }
        json_file = Path(self.temp_dir) / "test_data.json"
        
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        admin_accounts = self.data_manager.get_user_accounts("admin")
        assert len(admin_accounts) == 2
        assert all(acc["role"] == "admin" for acc in admin_accounts)
        
        standard_accounts = self.data_manager.get_user_accounts("standard")
        assert len(standard_accounts) == 1
        assert standard_accounts[0]["username"] == "user1"

    def test_generate_test_user(self):
        """Test dynamic test user generation."""
        user = self.data_manager.generate_test_user("admin")
        
        assert user["role"] == "admin"
        assert "username" in user
        assert "password" in user
        assert "email" in user
        assert "permissions" in user
        assert "admin" in user["permissions"]
        assert user["active"] is True

    def test_generate_search_data(self):
        """Test dynamic search data generation."""
        search_data = self.data_manager.generate_search_data(3)
        
        assert len(search_data) == 3
        for scenario in search_data:
            assert "name" in scenario
            assert "search_term" in scenario
            assert "expected_results_count" in scenario
            assert scenario["generated"] is True

    def test_validate_data_schema(self):
        """Test data schema validation."""
        # Valid search scenario
        valid_scenario = {
            "name": "test_search",
            "search_term": "python testing"
        }
        assert self.data_manager.validate_data_schema(valid_scenario, "search_scenario")
        
        # Invalid search scenario (missing required field)
        invalid_scenario = {
            "search_term": "python testing"  # Missing 'name'
        }
        assert not self.data_manager.validate_data_schema(invalid_scenario, "search_scenario")
        
        # Unknown schema
        assert not self.data_manager.validate_data_schema(valid_scenario, "unknown_schema")

    def test_cleanup_old_results(self):
        """Test cleanup of old result files."""
        # Create results directory and old files
        results_dir = Path(self.temp_dir) / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create old file (modify timestamp to be old)
        old_file = results_dir / "old_result.json"
        old_file.write_text('{"old": true}')
        
        # Modify file timestamp to be 35 days old
        old_time = datetime.now() - timedelta(days=35)
        import os
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Create recent file
        recent_file = results_dir / "recent_result.json"
        recent_file.write_text('{"recent": true}')
        
        # Run cleanup (keep files from last 30 days)
        self.data_manager.cleanup_old_results(30)
        
        # Verify old file is gone, recent file remains
        assert not old_file.exists()
        assert recent_file.exists()


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
            assert (Path(self.temp_dir) / dir_name).exists()

    def test_start_test_suite(self):
        """Test starting a test suite."""
        self.reporter.start_test_suite("Test_Suite", "qa", "chrome")
        
        suite = self.reporter.current_suite
        assert suite is not None
        assert suite.suite_name == "Test_Suite"
        assert suite.environment == "qa"
        assert suite.browser == "chrome"
        assert suite.total_tests == 0

    def test_add_test_result(self):
        """Test adding test results to suite."""
        self.reporter.start_test_suite("Test_Suite", "local", "chrome")
        
        # Add passed test
        passed_result = TestResult(
            test_name="test_pass",
            status="PASSED",
            duration=2.5,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome"
        )
        self.reporter.add_test_result(passed_result)
        
        # Add failed test
        failed_result = TestResult(
            test_name="test_fail",
            status="FAILED",
            duration=1.8,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome",
            error_message="Test assertion failed"
        )
        self.reporter.add_test_result(failed_result)
        
        # Verify suite statistics
        suite = self.reporter.current_suite
        assert suite.total_tests == 2
        assert suite.passed == 1
        assert suite.failed == 1
        assert suite.total_duration == 4.3

    def test_generate_json_report(self):
        """Test JSON report generation."""
        self.reporter.start_test_suite("JSON_Test", "local", "chrome")
        
        # Add a test result
        result = TestResult(
            test_name="test_json",
            status="PASSED",
            duration=1.5,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome"
        )
        self.reporter.add_test_result(result)
        
        # Generate report
        report_path = self.reporter.generate_json_report("test_report.json")
        
        # Verify file exists and contains expected data
        assert Path(report_path).exists()
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        assert "suite_summary" in report_data
        assert "metrics" in report_data
        assert "test_results" in report_data
        assert report_data["suite_summary"]["suite_name"] == "JSON_Test"
        assert len(report_data["test_results"]) == 1

    def test_generate_html_report(self):
        """Test HTML report generation."""
        self.reporter.start_test_suite("HTML_Test", "local", "chrome")
        
        # Add test results
        result = TestResult(
            test_name="test_html",
            status="PASSED",
            duration=2.0,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome"
        )
        self.reporter.add_test_result(result)
        
        # Generate report
        report_path = self.reporter.generate_html_report("test_report.html")
        
        # Verify file exists and contains HTML content
        assert Path(report_path).exists()
        
        with open(report_path, 'r') as f:
            html_content = f.read()
        
        assert "<!DOCTYPE html>" in html_content
        assert "Test Execution Report" in html_content
        assert "HTML_Test" in html_content

    def test_get_failure_patterns(self):
        """Test failure pattern analysis."""
        self.reporter.start_test_suite("Failure_Test", "local", "chrome")
        
        # Add failed tests with different error patterns
        timeout_result = TestResult(
            test_name="test_timeout",
            status="FAILED",
            duration=30.0,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome",
            error_message="TimeoutException: Element not found within timeout"
        )
        
        element_result = TestResult(
            test_name="test_element",
            status="FAILED",
            duration=5.0,
            timestamp=datetime.now(),
            environment="local",
            browser="chrome",
            error_message="NoSuchElementException: Unable to locate element"
        )
        
        self.reporter.add_test_result(timeout_result)
        self.reporter.add_test_result(element_result)
        
        # Analyze failure patterns
        patterns = self.reporter.get_failure_patterns()
        
        assert patterns["total_failures"] == 2
        assert "error_patterns" in patterns
        assert "most_failing_tests" in patterns


class TestErrorClassifier:
    """Unit tests for ErrorClassifier."""

    def setup_method(self):
        """Setup error classifier."""
        self.classifier = ErrorClassifier()

    def test_classify_timeout_error(self):
        """Test classification of timeout errors."""
        from selenium.common.exceptions import TimeoutException
        
        error = TimeoutException("Element not found within timeout")
        context = ErrorContext(
            error_type="TimeoutException",
            error_message="Element not found within timeout",
            timestamp=datetime.now(),
            test_name="test_timeout",
            page_url="https://example.com"
        )
        
        classification = self.classifier.classify_error(error, context)
        
        assert classification["error_type"] == "TimeoutException"
        assert classification["classification"]["category"] == "timeout"
        assert classification["classification"]["severity"].value == "medium"

    def test_classify_element_not_found_error(self):
        """Test classification of element not found errors."""
        from selenium.common.exceptions import NoSuchElementException
        
        error = NoSuchElementException("Unable to locate element")
        context = ErrorContext(
            error_type="NoSuchElementException",
            error_message="Unable to locate element",
            timestamp=datetime.now(),
            test_name="test_element",
            page_url="https://example.com"
        )
        
        classification = self.classifier.classify_error(error, context)
        
        assert classification["error_type"] == "NoSuchElementException"
        assert classification["classification"]["category"] == "element_not_found"
        assert classification["classification"]["severity"].value == "high"

    def test_classify_unknown_error(self):
        """Test classification of unknown errors."""
        error = ValueError("Unknown error type")
        context = ErrorContext(
            error_type="ValueError",
            error_message="Unknown error type",
            timestamp=datetime.now(),
            test_name="test_unknown",
            page_url="https://example.com"
        )
        
        classification = self.classifier.classify_error(error, context)
        
        assert classification["error_type"] == "ValueError"
        assert classification["classification"]["category"] == "unknown"
        assert classification["confidence"] == 0.3


class TestRecoveryManager:
    """Unit tests for RecoveryManager."""

    def setup_method(self):
        """Setup recovery manager with mocks."""
        self.mock_driver_factory = Mock()
        self.recovery_manager = RecoveryManager(self.mock_driver_factory)

    def test_get_recovery_statistics_empty(self):
        """Test getting recovery statistics when no recoveries recorded."""
        stats = self.recovery_manager.get_recovery_statistics()
        assert stats["message"] == "No recovery attempts recorded"

    def test_retry_recovery_success(self):
        """Test successful retry recovery."""
        from utils.error_handler import RecoveryAction, RecoveryStrategy
        
        mock_driver = Mock()
        error_context = ErrorContext(
            error_type="TimeoutException",
            error_message="Timeout occurred",
            timestamp=datetime.now(),
            test_name="test_retry",
            page_url="https://example.com"
        )
        
        # Mock success validation
        success_validation = Mock(return_value=True)
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_attempts=2,
            wait_time=0.1,
            success_validation=success_validation
        )
        
        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver, error_context, recovery_action
        )
        
        assert result is True
        assert len(self.recovery_manager.recovery_history) == 1
        assert self.recovery_manager.recovery_history[0]["success"] is True

    def test_retry_recovery_failure(self):
        """Test failed retry recovery."""
        from utils.error_handler import RecoveryAction, RecoveryStrategy
        
        mock_driver = Mock()
        error_context = ErrorContext(
            error_type="TimeoutException",
            error_message="Timeout occurred",
            timestamp=datetime.now(),
            test_name="test_retry_fail",
            page_url="https://example.com"
        )
        
        # Mock failing validation
        success_validation = Mock(return_value=False)
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.RETRY,
            max_attempts=2,
            wait_time=0.1,
            success_validation=success_validation
        )
        
        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver, error_context, recovery_action
        )
        
        assert result is False
        assert len(self.recovery_manager.recovery_history) == 1
        assert self.recovery_manager.recovery_history[0]["success"] is False

    @patch('selenium.webdriver.support.ui.WebDriverWait')
    def test_refresh_recovery(self, mock_wait):
        """Test page refresh recovery."""
        from utils.error_handler import RecoveryAction, RecoveryStrategy
        
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
            timestamp=datetime.now(),
            test_name="test_refresh",
            page_url="https://example.com"
        )
        
        recovery_action = RecoveryAction(
            strategy=RecoveryStrategy.REFRESH,
            max_attempts=1,
            wait_time=1.0
        )
        
        # Execute recovery
        result = self.recovery_manager.execute_recovery(
            mock_driver, error_context, recovery_action
        )
        
        # Verify refresh was called
        mock_driver.refresh.assert_called_once()
        # Verify document ready state was checked
        mock_driver.execute_script.assert_called_with("return document.readyState")
        assert result is True

    def test_get_recovery_statistics_with_data(self):
        """Test getting recovery statistics with recorded data."""
        # Manually add recovery records
        self.recovery_manager.recovery_history = [
            {
                "strategy": "retry",
                "success": True,
                "duration": 1.5,
                "timestamp": datetime.now()
            },
            {
                "strategy": "retry",
                "success": False,
                "duration": 2.0,
                "timestamp": datetime.now()
            },
            {
                "strategy": "refresh",
                "success": True,
                "duration": 3.0,
                "timestamp": datetime.now()
            }
        ]
        
        stats = self.recovery_manager.get_recovery_statistics()
        
        assert stats["total_recovery_attempts"] == 3
        assert stats["successful_recoveries"] == 2
        assert stats["success_rate"] == 66.67
        assert stats["average_recovery_time"] == 2.17
        
        # Check strategy-specific stats
        strategy_stats = stats["strategy_performance"]
        assert strategy_stats["retry"]["total"] == 2
        assert strategy_stats["retry"]["successful"] == 1
        assert strategy_stats["refresh"]["total"] == 1
        assert strategy_stats["refresh"]["successful"] == 1


class TestSmartErrorHandler:
    """Unit tests for SmartErrorHandler."""

    def setup_method(self):
        """Setup smart error handler with mocks."""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = SmartErrorHandler(
            screenshots_dir=self.temp_dir
        )

    def test_init_creates_screenshots_dir(self):
        """Test that initialization creates screenshots directory."""
        assert Path(self.temp_dir).exists()

    @patch('utils.error_handler.SmartErrorHandler._capture_error_screenshot')
    def test_handle_error_with_recovery(self, mock_screenshot):
        """Test error handling with successful recovery."""
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.get_log.return_value = []
        mock_screenshot.return_value = "/path/to/screenshot.png"
        
        # Mock successful recovery
        with patch.object(self.error_handler.recovery_manager, 'execute_recovery') as mock_recovery:
            mock_recovery.return_value = True
            
            # Use a recognizable error type for the classifier
            error = Exception("TimeoutException: Element not found after timeout")
            result = self.error_handler.handle_error(error, mock_driver, "test_name")
            
            assert result is True
            mock_recovery.assert_called_once()

    @patch('utils.error_handler.SmartErrorHandler._capture_error_screenshot')
    def test_handle_error_with_failed_recovery(self, mock_screenshot):
        """Test error handling with failed recovery."""
        mock_driver = Mock()
        mock_driver.current_url = "https://example.com"
        mock_driver.get_log.return_value = []
        mock_screenshot.return_value = "/path/to/screenshot.png"
        
        # Mock failed recovery
        with patch.object(self.error_handler.recovery_manager, 'execute_recovery') as mock_recovery:
            mock_recovery.return_value = False
            
            # Use a recognizable error type for the classifier
            error = Exception("NoSuchElementException: Unable to locate element")
            result = self.error_handler.handle_error(error, mock_driver, "test_name")
            
            assert result is False
            mock_recovery.assert_called_once()

    def test_capture_error_screenshot_success(self):
        """Test successful screenshot capture."""
        mock_driver = Mock()
        
        # Setup mock to simulate successful screenshot
        screenshot_path = str(Path(self.temp_dir) / "test_screenshot.png")
        mock_driver.save_screenshot.return_value = True
        
        # Create a dummy image file to simulate screenshot
        with open(screenshot_path, 'w') as f:
            f.write("fake image data")
        
        # Mock the save_screenshot to create the file
        def mock_save_screenshot(path):
            with open(path, 'w') as f:
                f.write("fake image data")
            return True
        
        mock_driver.save_screenshot = mock_save_screenshot
        
        result = self.error_handler._capture_error_screenshot(mock_driver, "test_name")
        
        assert result is not None
        assert "error_test_name_" in result
        assert result.endswith(".png")

    def test_capture_error_screenshot_failure(self):
        """Test screenshot capture failure."""
        mock_driver = Mock()
        mock_driver.save_screenshot.side_effect = Exception("Screenshot failed")
        
        result = self.error_handler._capture_error_screenshot(mock_driver, "test_name")
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])