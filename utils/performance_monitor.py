"""
Performance monitoring utilities with benchmarking and load testing capabilities.
"""

import os
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Optional

import psutil

from utils.structured_logger import get_logger

# Constants
SECONDS_TO_MILLISECONDS = 1000

# Default Performance Thresholds (in milliseconds)
# These represent acceptable maximums for various operations
DEFAULT_PAGE_LOAD_THRESHOLD_MS = 5000  # 5 seconds
DEFAULT_ELEMENT_FIND_THRESHOLD_MS = 1000  # 1 second
DEFAULT_CLICK_OPERATION_THRESHOLD_MS = 500  # 500ms
DEFAULT_FORM_FILL_THRESHOLD_MS = 2000  # 2 seconds
DEFAULT_API_RESPONSE_THRESHOLD_MS = 2000  # 2 seconds
DEFAULT_API_FIRST_BYTE_THRESHOLD_MS = 500  # 500ms
DEFAULT_API_TOTAL_TIME_THRESHOLD_MS = 3000  # 3 seconds


def _format_locator(by: Any, value: str) -> str:
    """
    Format a Selenium locator for logging.

    Args:
        by: Selenium By locator type (string or By enum)
        value: Locator value

    Returns:
        str: Formatted locator string (e.g., "id=username" or "xpath=//div")
    """
    if isinstance(by, str):
        return f"{by}={value}"
    if by is not None and hasattr(by, "name"):
        return f"{by.name}={value}"
    return f"{by!s}={value}"


@dataclass
class PerformanceMetric:
    """Data class for performance metric storage."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Optional[dict[str, Any]] = None


class PerformanceMonitor:
    """
    Advanced performance monitoring with benchmarking capabilities.

    Features:
    - Function execution timing with decorators
    - Memory usage tracking and analysis
    - CPU utilization monitoring
    - Performance threshold validation
    - Statistical analysis of performance data
    - Integration with structured logging
    """

    def __init__(self, name: str = "PerformanceMonitor"):
        """Initialize performance monitor with logging."""
        self.name = name
        self.logger = get_logger(f"Performance.{name}")
        self.metrics: list[PerformanceMetric] = []
        self.thresholds: dict[str, float] = {}

    def set_threshold(
        self,
        metric_name: str,
        threshold_value: float,
        unit: str = "ms",
    ) -> None:
        """Set performance threshold for monitoring."""
        self.thresholds[metric_name] = threshold_value
        self.logger.info(
            "Performance threshold set",
            metric=metric_name,
            threshold=threshold_value,
            unit=unit,
        )

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "ms",
        **context,
    ) -> None:
        """Record a performance metric with context."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(timezone.utc),
            context=context,
        )
        self.metrics.append(metric)

        # Log the metric
        self.logger.performance_metric(name, value, unit, **context)

        # Check threshold if set
        if name in self.thresholds:
            threshold = self.thresholds[name]
            if value > threshold:
                self.logger.warning(
                    "Performance threshold exceeded",
                    metric=name,
                    value=value,
                    threshold=threshold,
                    unit=unit,
                    exceeded_by=value - threshold,
                )

    def timer(self, name: Optional[str] = None, unit: str = "ms", **context):
        """Decorator for timing function execution."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                metric_name = name or f"{func.__name__}_execution_time"

                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.perf_counter()
                    duration = (end_time - start_time) * SECONDS_TO_MILLISECONDS

                    self.record_metric(
                        metric_name,
                        duration,
                        unit,
                        function=func.__name__,
                        success=success,
                        error=error,
                        **context,
                    )

                return result

            return wrapper

        return decorator

    def measure_memory_usage(self, name: str = "memory_usage") -> dict[str, float]:
        """Measure current memory usage and record as metric."""
        process = psutil.Process()
        memory_info = process.memory_info()

        metrics = {
            "rss_mb": memory_info.rss / (1024 * 1024),
            "vms_mb": memory_info.vms / (1024 * 1024),
            "percent": process.memory_percent(),
        }

        # Record each metric
        for key, value in metrics.items():
            self.record_metric(f"{name}_{key}", value, "MB" if "mb" in key else "%")

        return metrics

    def measure_cpu_usage(
        self,
        interval: float = 0.1,
        name: str = "cpu_usage",
    ) -> float:
        """Measure CPU usage and record as metric."""
        cpu_percent = psutil.cpu_percent(interval=interval)
        self.record_metric(name, cpu_percent, "%")
        return cpu_percent

    def benchmark_function(
        self,
        func: Callable,
        iterations: int = 100,
        *args,
        **kwargs,
    ) -> dict[str, float]:
        """Benchmark a function with multiple iterations and statistical analysis."""
        execution_times = []

        for _i in range(iterations):
            start_time = time.perf_counter()
            func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_times.append((end_time - start_time) * SECONDS_TO_MILLISECONDS)

        # Statistical analysis
        stats = {
            "mean": statistics.mean(execution_times),
            "median": statistics.median(execution_times),
            "min": min(execution_times),
            "max": max(execution_times),
            "stddev": (
                statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            ),
            "iterations": iterations,
        }

        # Record summary metrics
        function_name = func.__name__
        for stat_name, value in stats.items():
            if stat_name != "iterations":
                self.record_metric(
                    f"{function_name}_benchmark_{stat_name}",
                    value,
                    "ms",
                    iterations=iterations,
                    benchmark_type=stat_name,
                )

        self.logger.info(
            "Function benchmark completed",
            function=function_name,
            benchmark_iterations=iterations,
            **stats,
        )

        return stats

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of all recorded metrics."""
        if not self.metrics:
            return {"total_metrics": 0}

        # Group metrics by name
        grouped_metrics = {}
        for metric in self.metrics:
            if metric.name not in grouped_metrics:
                grouped_metrics[metric.name] = []
            grouped_metrics[metric.name].append(metric.value)

        # Calculate statistics for each metric
        summary = {
            "total_metrics": len(self.metrics),
            "unique_metric_names": len(grouped_metrics),
            "metrics": {},
        }

        for name, values in grouped_metrics.items():
            if len(values) == 1:
                summary["metrics"][name] = {
                    "count": 1,
                    "value": values[0],
                    "unit": next(m.unit for m in self.metrics if m.name == name),
                }
            else:
                summary["metrics"][name] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "min": min(values),
                    "max": max(values),
                    "stddev": statistics.stdev(values),
                    "unit": next(m.unit for m in self.metrics if m.name == name),
                }

        return summary

    def get_performance_report(self) -> dict[str, Any]:
        """Get performance report with average values - alias for compatibility.

        Returns:
            Dictionary with total_metrics and average_value keys.
        """
        summary = self.get_metrics_summary()
        all_values = [m.value for m in self.metrics]
        summary["average_value"] = statistics.mean(all_values) if all_values else 0
        return summary


class WebDriverPerformanceMonitor(PerformanceMonitor):
    """Specialized performance monitor for WebDriver operations."""

    def __init__(self):
        super().__init__("WebDriver")

        # Set default thresholds for web operations using named constants
        self.set_threshold("page_load_time", DEFAULT_PAGE_LOAD_THRESHOLD_MS, "ms")
        self.set_threshold("element_find_time", DEFAULT_ELEMENT_FIND_THRESHOLD_MS, "ms")
        self.set_threshold(
            "click_operation_time", DEFAULT_CLICK_OPERATION_THRESHOLD_MS, "ms"
        )
        self.set_threshold("form_fill_time", DEFAULT_FORM_FILL_THRESHOLD_MS, "ms")

    def monitor_page_load(self, driver, url: str) -> float:
        """Monitor page load performance."""
        start_time = time.perf_counter()
        driver.get(url)
        end_time = time.perf_counter()

        load_time = (end_time - start_time) * SECONDS_TO_MILLISECONDS
        self.record_metric("page_load_time", load_time, "ms", url=url)

        return load_time

    def monitor_element_find(self, driver, by, value: str) -> float:
        """Monitor element finding performance."""
        start_time = time.perf_counter()
        driver.find_element(by, value)
        end_time = time.perf_counter()

        find_time = (end_time - start_time) * SECONDS_TO_MILLISECONDS
        locator_str = _format_locator(by, value)
        self.record_metric("element_find_time", find_time, "ms", locator=locator_str)

        return find_time


class APIPerformanceMonitor(PerformanceMonitor):
    """Specialized performance monitor for API operations."""

    def __init__(self):
        super().__init__("API")

        # Set default thresholds for API operations using named constants
        self.set_threshold("api_response_time", DEFAULT_API_RESPONSE_THRESHOLD_MS, "ms")
        self.set_threshold(
            "api_first_byte_time", DEFAULT_API_FIRST_BYTE_THRESHOLD_MS, "ms"
        )
        self.set_threshold("api_total_time", DEFAULT_API_TOTAL_TIME_THRESHOLD_MS, "ms")

    def monitor_api_request(
        self,
        session,
        method: str,
        url: str,
        **kwargs,
    ) -> dict[str, float]:
        """Monitor API request performance with detailed timing."""
        start_time = time.perf_counter()
        response = getattr(session, method.lower())(url, **kwargs)
        end_time = time.perf_counter()

        total_time = (end_time - start_time) * SECONDS_TO_MILLISECONDS

        # Extract response timing if available
        response_time = response.elapsed.total_seconds() * SECONDS_TO_MILLISECONDS

        # Record metrics
        self.record_metric(
            "api_response_time",
            response_time,
            "ms",
            method=method,
            url=url,
            status_code=response.status_code,
        )
        self.record_metric(
            "api_total_time",
            total_time,
            "ms",
            method=method,
            url=url,
            status_code=response.status_code,
        )

        return {
            "response_time": response_time,
            "total_time": total_time,
            "status_code": response.status_code,
        }


def performance_test(threshold_ms: Optional[float] = None, name: Optional[str] = None):
    """Decorator for performance testing with threshold validation."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor(name or func.__name__)

            if threshold_ms:
                monitor.set_threshold(f"{func.__name__}_execution", threshold_ms, "ms")
            effective_threshold = threshold_ms
            # Global override (milliseconds)
            try:
                env_global = os.getenv("PERFORMANCE_THRESHOLD_MS")
                if env_global:
                    effective_threshold = float(env_global)
            except (ValueError, OSError, TypeError):
                # Ignore invalid env var
                pass

            # Specific override for this test name
            try:
                specific_key = f"PERF_THRESHOLD_{(name or func.__name__).upper()}"
                env_specific = os.getenv(specific_key)
                if env_specific:
                    effective_threshold = float(env_specific)
            except (ValueError, OSError, TypeError):
                pass

            if effective_threshold:
                monitor.set_threshold(
                    f"{func.__name__}_execution",
                    effective_threshold,
                    "ms",
                )

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            execution_time = (end_time - start_time) * SECONDS_TO_MILLISECONDS
            monitor.record_metric(f"{func.__name__}_execution", execution_time, "ms")

            # Use effective_threshold for evaluation (may be overridden by env)
            if effective_threshold and execution_time > effective_threshold:
                msg = (
                    f"Performance threshold exceeded: "
                    f"{execution_time:.2f}ms > {effective_threshold}ms"
                )
                # Allow strict failure to be opt-in via environment variable.
                fail_on_threshold = (
                    os.getenv(
                        "PERFORMANCE_FAIL_ON_THRESHOLD",
                        "false",
                    ).lower()
                    == "true"
                )
                if fail_on_threshold:
                    raise AssertionError(msg)
                # Default to warning to reduce test flakiness on slower runners.
                monitor.logger.warning(msg)

            return result

        return wrapper

    return decorator


# Pre-configured monitor instances for common use cases
web_performance = WebDriverPerformanceMonitor()
api_performance = APIPerformanceMonitor()
