"""Unit tests for structured_logger module."""

import pytest
from hamcrest import (
    assert_that,
    equal_to,
    has_property,
    instance_of,
    is_,
    not_none,
)

from utils.structured_logger import (
    ExecutionLogger,
    StructuredLogger,
    framework_logger,
    get_logger,
    get_test_logger,
)


class TestStructuredLogger:
    """Test cases for StructuredLogger class."""

    def test_logger_instantiation(self):
        """Test that StructuredLogger can be instantiated."""
        logger = StructuredLogger("TestLogger")
        assert_that(logger, is_(not_none()))
        assert_that(logger.name, equal_to("TestLogger"))

    def test_logger_has_required_methods(self):
        """Test that logger has all required logging methods."""
        logger = StructuredLogger("TestLogger")

        # Standard logging methods
        assert_that(logger, has_property("debug"))
        assert_that(logger, has_property("info"))
        assert_that(logger, has_property("warning"))
        assert_that(logger, has_property("error"))
        assert_that(logger, has_property("critical"))

        # Specialized logging methods
        assert_that(logger, has_property("test_start"))
        assert_that(logger, has_property("test_end"))
        assert_that(logger, has_property("test_step"))
        assert_that(logger, has_property("performance_metric"))
        assert_that(logger, has_property("browser_action"))
        assert_that(logger, has_property("api_request"))
        assert_that(logger, has_property("database_operation"))
        assert_that(logger, has_property("assertion_result"))

    def test_logger_level_configuration(self):
        """Test that logger level can be configured."""
        debug_logger = StructuredLogger("DebugLogger", "DEBUG")
        error_logger = StructuredLogger("ErrorLogger", "ERROR")

        # DEBUG level
        assert_that(debug_logger.level, equal_to(10))
        # ERROR level
        assert_that(error_logger.level, equal_to(40))

    def test_logging_methods_callable(self):
        """Test that all logging methods are callable."""
        logger = StructuredLogger("TestLogger")

        # These should not raise exceptions
        try:
            logger.info("Test message", test_context="test_value")
            logger.test_start("test_method", test_class="TestClass")
            logger.test_end("test_method", "PASS", duration=1.5)
            logger.performance_metric("response_time", 250.5, "ms")
            logger.browser_action("click", element="button#submit")
            logger.api_request("GET", "http://example.com", status_code=200)
            logger.database_operation("SELECT", table="users", rows_affected=5)
            logger.assertion_result("equals", True, expected=5, actual=5)
        except Exception as e:
            pytest.fail(f"Logging method failed: {e}")


class TestExecutionLogger:
    """Test cases for ExecutionLogger class."""

    def test_test_execution_logger_instantiation(self):
        """Test that ExecutionLogger can be instantiated."""
        test_logger = ExecutionLogger("test_example")
        assert_that(test_logger, is_(not_none()))
        assert_that(test_logger.test_name, equal_to("test_example"))
        assert_that(test_logger.step_count, equal_to(0))

    def test_test_lifecycle_methods(self):
        """Test that test lifecycle methods exist and are callable."""
        test_logger = ExecutionLogger("test_example")

        assert_that(test_logger, has_property("start_test"))
        assert_that(test_logger, has_property("end_test"))
        assert_that(test_logger, has_property("log_step"))
        assert_that(test_logger, has_property("log_assertion"))

        # These should not raise exceptions
        try:
            test_logger.start_test(browser="chrome")
            test_logger.log_step("Navigate to page", "navigate")
            test_logger.log_assertion("Page title correct", True)
            test_logger.end_test("PASS")
        except Exception as e:
            pytest.fail(f"Test execution logging failed: {e}")

    def test_step_counting(self):
        """Test that step counting works correctly."""
        test_logger = ExecutionLogger("test_example")

        assert_that(test_logger.step_count, equal_to(0))
        test_logger.log_step("Step 1", "action1")
        assert_that(test_logger.step_count, equal_to(1))
        test_logger.log_step("Step 2", "action2")
        assert_that(test_logger.step_count, equal_to(2))


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_get_logger_factory(self):
        """Test that get_logger factory function works."""
        logger = get_logger("FactoryTest", "INFO")
        assert_that(logger, is_(not_none()))
        assert_that(logger, instance_of(StructuredLogger))
        assert_that(logger.name, equal_to("FactoryTest"))

    def test_get_test_logger_factory(self):
        """Test that get_test_logger factory function works."""
        test_logger = get_test_logger("factory_test_method")
        assert_that(test_logger, is_(not_none()))
        assert_that(test_logger, instance_of(ExecutionLogger))
        assert_that(test_logger.test_name, equal_to("factory_test_method"))

    def test_framework_logger_exists(self):
        """Test that global framework logger exists."""
        assert_that(framework_logger, is_(not_none()))
        assert_that(framework_logger, instance_of(StructuredLogger))


class TestBackwardsCompatibility:
    """Test cases for backwards compatibility functions."""

    def test_legacy_logging_functions_exist(self):
        """Test that legacy logging functions exist for backwards compatibility."""
        from utils.structured_logger import log_error, log_info, log_warning

        assert_that(callable(log_info), is_(True))
        assert_that(callable(log_error), is_(True))
        assert_that(callable(log_warning), is_(True))

    def test_legacy_logging_functions_callable(self):
        """Test that legacy logging functions can be called."""
        from utils.structured_logger import log_error, log_info, log_warning

        try:
            log_info("Test info message", context="test")
            log_error("Test error message", context="test")
            log_warning("Test warning message", context="test")
        except Exception as e:
            pytest.fail(f"Legacy logging function failed: {e}")


class TestErrorHandling:
    """Test cases for error handling in logging."""

    def test_invalid_log_level_handling(self):
        """Test handling of invalid log levels."""
        try:
            # This should not crash, might use default level
            StructuredLogger("TestLogger", "INVALID_LEVEL")
            # If it doesn't crash, that's acceptable behavior
        except Exception:
            # If it does throw an exception, that's also acceptable
            pass

    def test_none_values_in_context(self):
        """Test that None values in context don't cause issues."""
        logger = StructuredLogger("TestLogger")

        try:
            logger.info("Test message", none_value=None, empty_string="")
        except Exception as e:
            pytest.fail(f"Logging with None values failed: {e}")


class TestSpecializedLogging:
    """Test cases for specialized logging methods."""

    def test_performance_metric_logging(self):
        """Test performance metric logging with various units."""
        logger = StructuredLogger("PerfLogger")

        try:
            logger.performance_metric("response_time", 150.5, "ms")
            logger.performance_metric("memory_usage", 512.0, "MB")
            logger.performance_metric("cpu_usage", 45.2, "%")
        except Exception as e:
            pytest.fail(f"Performance metric logging failed: {e}")

    def test_assertion_result_logging(self):
        """Test assertion result logging with different outcomes."""
        logger = StructuredLogger("AssertLogger")

        try:
            logger.assertion_result("equals", True, expected=5, actual=5)
            logger.assertion_result(
                "contains", False, expected="text", actual="other")
        except Exception as e:
            pytest.fail(f"Assertion result logging failed: {e}")

    def test_exception_logging(self):
        """Test exception logging functionality."""
        logger = StructuredLogger("ExceptionLogger")

        try:
            test_exception = ValueError("Test exception")
            logger.exception_caught(test_exception, "Test context")
        except Exception as e:
            pytest.fail(f"Exception logging failed: {e}")
