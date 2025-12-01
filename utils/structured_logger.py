"""
Structured logging with JSON output using structlog.
Provides consistent logging format for test automation framework.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import structlog


class StructuredLogger:
    """JSON structured logger with contextual information."""

    def __init__(self, name: str = "TestFramework", level: str = "INFO"):
        self.name = name
        level_value = getattr(logging, level.upper(), logging.INFO)

        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="ISO"),
                structlog.stdlib.add_log_level,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level_value),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        self.logger = structlog.get_logger(name).bind(logger_name=name)
        self.level = level_value

    def _log(self, level: str, msg: str, *args, **ctx):
        if args:
            msg = msg % args
        getattr(self.logger, level)(msg, **ctx)

    def debug(self, msg: str, *args, **ctx):
        """Log a debug message."""
        self._log("debug", msg, *args, **ctx)

    def info(self, msg: str, *args, **ctx):
        """Log an info message."""
        self._log("info", msg, *args, **ctx)

    def warning(self, msg: str, *args, **ctx):
        """Log a warning message."""
        self._log("warning", msg, *args, **ctx)

    def error(self, msg: str, *args, **ctx):
        """Log an error message."""
        self._log("error", msg, *args, **ctx)

    def critical(self, msg: str, *args, **ctx):
        """Log a critical message."""
        self._log("critical", msg, *args, **ctx)

    # Domain-specific log methods

    def test_start(self, test_name: str, test_class: Optional[str] = None, **ctx):
        """Log test start event."""
        self.info(
            "Test started",
            event_type="test_start",
            test_name=test_name,
            test_class=test_class,
            **ctx,
        )

    def test_end(
        self, test_name: str, result: str, duration: Optional[float] = None, **ctx
    ):
        """Log test end event."""
        self.info(
            "Test completed",
            event_type="test_end",
            test_name=test_name,
            result=result,
            duration_seconds=duration,
            **ctx,
        )

    def test_step(self, step_name: str, action: str, **ctx):
        """Log a test step execution."""
        self.info(
            "Test step executed",
            event_type="test_step",
            step_name=step_name,
            action=action,
            **ctx,
        )

    def assertion_result(
        self,
        *,
        assertion: str,
        result: bool,
        expected: Any = None,
        actual: Any = None,
        **ctx,
    ):
        """Log assertion result (pass or fail)."""
        log = self.info if result else self.error
        log(
            "Assertion executed",
            event_type="assertion",
            assertion=assertion,
            result="PASS" if result else "FAIL",
            expected=expected,
            actual=actual,
            **ctx,
        )

    def exception_caught(
        self, exception: Exception, context_info: Optional[str] = None, **ctx
    ):
        """Log caught exception details."""
        self.error(
            "Exception caught during execution",
            event_type="exception",
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            context_info=context_info,
            **ctx,
        )

    def performance_metric(
        self, metric_name: str, value: float, unit: str = "ms", **ctx
    ):
        self.info(
            "Performance metric recorded",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **ctx,
        )

    def browser_action(self, action: str, element: Optional[str] = None, **ctx):
        self.info(
            "Browser action",
            event_type="browser_action",
            action=action,
            element=element,
            **ctx,
        )

    def api_request(
        self,
        method: str,
        url: str,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        **ctx,
    ):
        self.info(
            "API request",
            event_type="api_request",
            method=method,
            url=url,
            status_code=status_code,
            response_time_ms=response_time,
            **ctx,
        )


class ExecutionLogger:
    """Test execution logger with timing and step counting."""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.logger = StructuredLogger(f"Test.{test_name}")
        self.start_time: Optional[datetime] = None
        self.step_count = 0

    def start_test(self, **ctx):
        self.start_time = datetime.now(timezone.utc)
        self.step_count = 0
        self.logger.test_start(
            self.test_name, start_time=self.start_time.isoformat(), **ctx
        )

    def end_test(self, result: str, **ctx):
        duration = (
            (datetime.now(timezone.utc) - self.start_time).total_seconds()
            if self.start_time
            else None
        )
        self.logger.test_end(
            self.test_name, result, duration, total_steps=self.step_count, **ctx
        )

    def log_step(self, step_name: str, action: str, **ctx):
        self.step_count += 1
        self.logger.test_step(step_name, action, step_number=self.step_count, **ctx)

    def log_assertion(self, *, assertion: str, result: bool, **ctx):
        self.logger.assertion_result(
            assertion=assertion, result=result, test_name=self.test_name, **ctx
        )

    def api_request(
        self,
        *,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        **ctx,
    ):
        """Log an API request with response details."""
        self.logger.info(
            "API request completed",
            event_type="api_request",
            method=method,
            url=url,
            status_code=status_code,
            response_time_ms=response_time,
            **ctx,
        )

    def performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        **ctx,
    ):
        """Log a performance metric."""
        self.logger.info(
            "Performance metric recorded",
            event_type="performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **ctx,
        )

    def browser_action(self, action: str, **ctx):
        """Log a browser action (navigate, click, type, etc.)."""
        self.logger.info(
            "Browser action performed",
            event_type="browser_action",
            action=action,
            **ctx,
        )


# Factory functions
def get_logger(name: str = "TestFramework", level: str = "INFO") -> StructuredLogger:
    return StructuredLogger(name, level)


def get_test_logger(test_name: str) -> ExecutionLogger:
    return ExecutionLogger(test_name)


# Global instance + legacy compatibility
framework_logger = StructuredLogger("FrameworkCore")
log_info = framework_logger.info
log_error = framework_logger.error
log_warning = framework_logger.warning

# Backward compatibility alias for utils/logger.py migration
# TestLogger was in utils/logger.py - now consolidated here
TestLogger = StructuredLogger
