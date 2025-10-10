"""
Enhanced structured logging utilities with JSON output for enterprise reporting.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import structlog


@dataclass(frozen=True)
class LoggerConfig:
    """
    Immutable configuration for structured logging.

    Attributes:
        default_name: Default logger name for framework components
        default_level: Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        framework_core_name: Name for the core framework logger instance
    """

    default_name: str = "TestFramework"
    default_level: str = "INFO"
    framework_core_name: str = "FrameworkCore"


# Global configuration instance
logger_config = LoggerConfig()


class StructuredLogger:
    """
    Enterprise-grade structured logging with JSON output and contextual information.

    Features:
    - JSON structured output for log aggregation systems
    - Automatic context injection (timestamp, level, module)
    - Performance-aware logging levels
    - Integration with existing Python logging
    """

    def __init__(
        self,
        name: str = logger_config.default_name,
        level: str = logger_config.default_level,
    ):
        """
        Initialize structured logger with configuration.

        Args:
            name (str): Logger name/component identifier
            level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level_upper = level.upper()
        if level_upper not in allowed_levels:
            message = (
                f"Invalid log level '{level}'. Allowed values are: "
                f"{', '.join(sorted(allowed_levels))}."
            )
            raise ValueError(message)
        self.level = getattr(logging, level_upper)

        # Configure structlog
        structlog.configure(
            processors=[
                # Add timestamp
                structlog.processors.TimeStamper(fmt="ISO"),
                # Add log level
                structlog.stdlib.add_log_level,
                # JSON output for structured logging
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(self.level),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Create logger instance with bound context
        self.logger = structlog.get_logger(name).bind(logger_name=name)

    def debug(self, message: str, *args: Any, **context: Any) -> None:
        """Log debug message with context."""
        if args:
            message = message % args
        self.logger.debug(message, **context)

    def info(self, message: str, *args: Any, **context: Any) -> None:
        """Log info message with context."""
        if args:
            message = message % args
        self.logger.info(message, **context)

    def warning(self, message: str, *args: Any, **context: Any) -> None:
        """Log warning message with context."""
        if args:
            message = message % args
        self.logger.warning(message, **context)

    def error(self, message: str, *args: Any, **context: Any) -> None:
        """Log error message with context."""
        if args:
            message = message % args
        self.logger.error(message, **context)

    def critical(self, message: str, *args: Any, **context: Any) -> None:
        """Log critical message with context."""
        if args:
            message = message % args
        self.logger.critical(message, **context)

    def test_start(
        self,
        test_name: str,
        test_class: str | None = None,
        **context: Any,
    ) -> None:
        """Log test start with structured context."""
        self.info(
            "Test started",
            event_type="test_start",
            test_name=test_name,
            test_class=test_class,
            **context,
        )

    def test_end(
        self,
        test_name: str,
        result: str,
        duration: float | None = None,
        **context: Any,
    ) -> None:
        """Log test completion with results."""
        self.info(
            "Test completed",
            event_type="test_end",
            test_name=test_name,
            result=result,
            duration_seconds=duration,
            **context,
        )

    def test_step(self, step_name: str, action: str, **context: Any) -> None:
        """Log individual test step for detailed tracing."""
        self.info(
            "Test step executed",
            event_type="test_step",
            step_name=step_name,
            action=action,
            **context,
        )

    def performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        **context: Any,
    ) -> None:
        """Log performance metrics for analysis."""
        self.info(
            "Performance metric recorded",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **context,
        )

    def browser_action(
        self,
        action: str,
        element: str | None = None,
        value: str | None = None,
        **context: Any,
    ) -> None:
        """Log browser interactions for debugging."""
        self.info(
            "Browser action performed",
            event_type="browser_action",
            action=action,
            element=element,
            value=value,
            **context,
        )

    def api_request(
        self,
        method: str,
        url: str,
        status_code: int | None = None,
        response_time: float | None = None,
        **context: Any,
    ) -> None:
        """Log API requests for tracking."""
        self.info(
            "API request executed",
            event_type="api_request",
            method=method,
            url=url,
            status_code=status_code,
            response_time_ms=response_time,
            **context,
        )

    def database_operation(
        self,
        operation: str,
        table: str | None = None,
        rows_affected: int | None = None,
        **context: Any,
    ) -> None:
        """Log database operations for auditing."""
        self.info(
            "Database operation executed",
            event_type="database_operation",
            operation=operation,
            table=table,
            rows_affected=rows_affected,
            **context,
        )

    def assertion_result(
        *,
        self,
        assertion: str,
        result: bool,
        expected: Any = None,
        actual: Any = None,
        **context: Any,
    ) -> None:
        """Log assertion results for detailed test analysis."""
        log_method = self.info if result else self.error
        log_method(
            "Assertion executed",
            event_type="assertion",
            assertion=assertion,
            result="PASS" if result else "FAIL",
            expected=expected,
            actual=actual,
            **context,
        )

    def environment_info(self, **environment_data: Any) -> None:
        """Log environment and configuration information."""
        self.info(
            "Environment information",
            event_type="environment_info",
            **environment_data,
        )

    def exception_caught(
        self,
        exception: Exception,
        context_info: str | None = None,
        **context: Any,
    ) -> None:
        """Log caught exceptions with full context."""
        self.error(
            "Exception caught during execution",
            event_type="exception",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context_info=context_info,
            **context,
        )


class ExecutionLogger:
    """
    Specialized logger for test execution lifecycle with timing and context.
    """

    def __init__(self, test_name: str):
        """Initialize test execution logger for specific test."""
        self.test_name = test_name
        self.logger = StructuredLogger(f"TestExecution.{test_name}")
        self.start_time = None
        self.step_count = 0

    def start_test(self, **context: Any) -> None:
        """Mark test start and begin timing."""
        self.start_time = datetime.now(UTC)
        self.step_count = 0
        self.logger.test_start(
            test_name=self.test_name,
            start_time=self.start_time.isoformat(),
            **context,
        )

    def end_test(self, result: str, **context: Any) -> None:
        """Mark test end with duration and results."""
        if self.start_time:
            duration = (datetime.now(UTC) - self.start_time).total_seconds()
        else:
            duration = None

        self.logger.test_end(
            test_name=self.test_name,
            result=result,
            duration=duration,
            total_steps=self.step_count,
            **context,
        )

    def log_step(self, step_name: str, action: str, **context: Any) -> None:
        """Log individual test step with automatic counting."""
        self.step_count += 1
        self.logger.test_step(
            step_name=step_name,
            action=action,
            step_number=self.step_count,
            **context,
        )

    def log_assertion(*, self, assertion: str, result: bool, **context: Any) -> None:
        """Log assertion with test context."""
        self.logger.assertion_result(
            assertion=assertion,
            result=result,
            test_name=self.test_name,
            step_number=self.step_count,
            **context,
        )

    def api_request(
        self,
        method: str,
        url: str,
        status_code: int | None = None,
        response_time: float | None = None,
        **context: Any,
    ) -> None:
        """Log API request with test context."""
        self.logger.api_request(
            method=method,
            url=url,
            status_code=status_code,
            response_time=response_time,
            test_name=self.test_name,
            **context,
        )

    def performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        **context: Any,
    ) -> None:
        """Log performance metric with test context."""
        self.logger.performance_metric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            test_name=self.test_name,
            **context,
        )

    def browser_action(self, action: str, **context: Any) -> None:
        """Log browser action with test context."""
        self.logger.info(
            "Browser action: %s",
            action,
            event_type="browser_action",
            action=action,
            test_name=self.test_name,
            **context,
        )

    def exception_caught(
        self,
        exception: Exception,
        context_description: str = "",
        **context: Any,
    ) -> None:
        """Log exception with test context."""
        self.logger.error(
            "Exception caught: %s",
            context_description,
            event_type="exception",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context_description=context_description,
            test_name=self.test_name,
            **context,
        )


# Global logger instance for framework-wide use
framework_logger = StructuredLogger(logger_config.framework_core_name)


def get_logger(
    name: str = logger_config.default_name,
    level: str = logger_config.default_level,
) -> StructuredLogger:
    """
    Factory function to create structured logger instances.

    Args:
        name (str): Logger name/component
        level (str): Logging level

    Returns:
        StructuredLogger: Configured logger instance
    """
    return StructuredLogger(name, level)


def get_test_logger(test_name: str) -> ExecutionLogger:
    """
    Factory function to create test execution logger.

    Args:
        test_name (str): Name of the test being executed

    Returns:
        ExecutionLogger: Test-specific logger
    """
    return ExecutionLogger(test_name)


# Backwards compatibility with existing logging
def log_info(message: str, **context: Any) -> None:
    """Legacy logging function for backwards compatibility."""
    framework_logger.info(message, **context)


def log_error(message: str, **context: Any) -> None:
    """Legacy logging function for backwards compatibility."""
    framework_logger.error(message, **context)


def log_warning(message: str, **context: Any) -> None:
    """Legacy logging function for backwards compatibility."""
    framework_logger.warning(message, **context)
