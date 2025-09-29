"""
Unit tests for logging utility module.
Tests logging functionality, formatting, and file operations.
"""

import logging
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.logger import TestLogger, logger


class TestTestLogger:
    """Test cases for TestLogger class."""

    def test_logger_initialization(self):
        """Test that logger initializes with correct configuration."""
        test_logger = TestLogger()
        
        assert test_logger.logger.name == "TestFramework"
        assert test_logger.logger.level == logging.DEBUG
        assert len(test_logger.logger.handlers) >= 1  # At least console handler

    def test_console_handler_setup(self):
        """Test console handler configuration."""
        test_logger = TestLogger()
        
        # Find console handler
        console_handler = None
        for handler in test_logger.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break
        
        assert console_handler is not None
        assert console_handler.level == logging.INFO

    @patch('config.settings.settings')
    def test_file_handler_setup(self, mock_settings):
        """Test file handler configuration."""
        # Mock settings to provide logs directory
        mock_logs_dir = Path("/tmp/test_logs")
        mock_settings.LOGS_DIR = mock_logs_dir
        mock_settings.LOG_LEVEL = "DEBUG"
        
        with patch('pathlib.Path.mkdir'):
            test_logger = TestLogger()
            
            # Should have both console and file handlers
            assert len(test_logger.logger.handlers) >= 1

    def test_info_logging(self):
        """Test info level logging."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.info("Test info message")
            mock_info.assert_called_once_with("Test info message")

    def test_debug_logging(self):
        """Test debug level logging."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'debug') as mock_debug:
            test_logger.debug("Test debug message")
            mock_debug.assert_called_once_with("Test debug message")

    def test_warning_logging(self):
        """Test warning level logging."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'warning') as mock_warning:
            test_logger.warning("Test warning message")
            mock_warning.assert_called_once_with("Test warning message")

    def test_error_logging(self):
        """Test error level logging."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'error') as mock_error:
            test_logger.error("Test error message")
            mock_error.assert_called_once_with("Test error message")

    def test_test_start_logging(self):
        """Test test start logging with proper formatting."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.test_start("test_example")
            mock_info.assert_called_once_with("🚀 STARTING TEST: test_example")

    def test_test_end_logging(self):
        """Test test end logging with duration and status."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.test_end("test_example", "PASSED", 2.5)
            expected_message = "✅ TEST COMPLETED: test_example | Status: PASSED | Duration: 2.50s"
            mock_info.assert_called_once_with(expected_message)

    def test_test_end_failed_status(self):
        """Test test end logging with failed status."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.test_end("test_example", "FAILED", 1.2)
            expected_message = "❌ TEST COMPLETED: test_example | Status: FAILED | Duration: 1.20s"
            mock_info.assert_called_once_with(expected_message)

    def test_step_logging(self):
        """Test step logging functionality."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.step("Click login button")
            mock_info.assert_called_once_with("  📋 STEP: Click login button")

    def test_screenshot_logging(self):
        """Test screenshot logging."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.screenshot("/path/to/screenshot.png")
            mock_info.assert_called_once_with("Screenshot saved: /path/to/screenshot.png")

    def test_separator_logging(self):
        """Test separator logging for test organization."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            test_logger.separator()
            mock_info.assert_called_once_with("=" * 80)

    def test_exception_logging(self):
        """Test exception logging with traceback."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'error') as mock_error:
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                test_logger.exception("Error occurred", e)
                
            # Should log the error message and exception
            assert mock_error.call_count == 1
            call_args = mock_error.call_args[0][0]
            assert "Error occurred" in call_args
            assert "Test exception" in call_args


class TestLoggerModule:
    """Test cases for module-level logger functions."""

    def test_module_logger_instance(self):
        """Test that module provides a logger instance."""
        assert logger is not None
        assert isinstance(logger, TestLogger)

    def test_module_function_info(self):
        """Test module-level info function."""
        with patch.object(logger, 'info') as mock_info:
            from utils.logger import info
            info("Test message")
            mock_info.assert_called_once_with("Test message")

    def test_module_function_debug(self):
        """Test module-level debug function."""
        with patch.object(logger, 'debug') as mock_debug:
            from utils.logger import debug
            debug("Debug message")
            mock_debug.assert_called_once_with("Debug message")

    def test_module_function_warning(self):
        """Test module-level warning function."""
        with patch.object(logger, 'warning') as mock_warning:
            from utils.logger import warning
            warning("Warning message")
            mock_warning.assert_called_once_with("Warning message")

    def test_module_function_error(self):
        """Test module-level error function."""
        with patch.object(logger, 'error') as mock_error:
            from utils.logger import error
            error("Error message")
            mock_error.assert_called_once_with("Error message")

    def test_module_function_test_start(self):
        """Test module-level test_start function."""
        with patch.object(logger, 'test_start') as mock_test_start:
            from utils.logger import test_start
            test_start("test_name")
            mock_test_start.assert_called_once_with("test_name")

    def test_module_function_test_end(self):
        """Test module-level test_end function."""
        with patch.object(logger, 'test_end') as mock_test_end:
            from utils.logger import test_end
            test_end("test_name", "PASSED", 1.5)
            mock_test_end.assert_called_once_with("test_name", "PASSED", 1.5)

    def test_module_function_step(self):
        """Test module-level step function."""
        with patch.object(logger, 'step') as mock_step:
            from utils.logger import step
            step("Test step")
            mock_step.assert_called_once_with("Test step")

    def test_module_function_screenshot(self):
        """Test module-level screenshot function."""
        with patch.object(logger, 'screenshot') as mock_screenshot:
            from utils.logger import screenshot
            screenshot("/path/to/image.png")
            mock_screenshot.assert_called_once_with("/path/to/image.png")

    def test_module_function_separator(self):
        """Test module-level separator function."""
        with patch.object(logger, 'separator') as mock_separator:
            from utils.logger import separator
            separator()
            mock_separator.assert_called_once()


class TestLoggerFormatting:
    """Test cases for logger formatting and output."""

    def test_log_format_contains_timestamp(self):
        """Test that log format includes timestamp."""
        test_logger = TestLogger()
        
        # Create a string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        test_logger.logger.addHandler(handler)
        
        test_logger.info("Test message")
        
        log_output = log_stream.getvalue()
        # Should contain timestamp pattern (YYYY-MM-DD HH:MM:SS)
        import re
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        assert re.search(timestamp_pattern, log_output)

    def test_duration_formatting(self):
        """Test that duration is formatted correctly."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            # Test different duration formats
            test_logger.test_end("test", "PASSED", 1.0)
            args = mock_info.call_args[0][0]
            assert "Duration: 1.00s" in args
            
            mock_info.reset_mock()
            test_logger.test_end("test", "PASSED", 0.123)
            args = mock_info.call_args[0][0]
            assert "Duration: 0.12s" in args

    def test_status_emoji_formatting(self):
        """Test that status gets correct emoji."""
        test_logger = TestLogger()
        
        with patch.object(test_logger.logger, 'info') as mock_info:
            # Test PASSED status
            test_logger.test_end("test", "PASSED", 1.0)
            args = mock_info.call_args[0][0]
            assert "✅" in args
            
            mock_info.reset_mock()
            
            # Test FAILED status
            test_logger.test_end("test", "FAILED", 1.0)
            args = mock_info.call_args[0][0]
            assert "❌" in args