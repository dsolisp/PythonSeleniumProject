"""
Performance monitoring utilities with benchmarking and load testing capabilities.
"""

import time
import statistics
import psutil
from typing import Dict, List, Callable, Any
from functools import wraps
from dataclasses import dataclass
from datetime import datetime

from utils.structured_logger import get_logger


@dataclass
class PerformanceMetric:
    """Data class for performance metric storage."""

    name: str
    value: float
    unit: str
    timestamp: datetime
    context: Dict[str, Any] = None


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
        self.metrics: List[PerformanceMetric] = []
        self.thresholds: Dict[str, float] = {}

    def set_threshold(
        self, metric_name: str, threshold_value: float, unit: str = "ms"
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
        self, name: str, value: float, unit: str = "ms", **context
    ) -> None:
        """Record a performance metric with context."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
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

    def timer(self, name: str = None, unit: str = "ms", **context):
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
                    duration = (end_time - start_time) * 1000  # Convert to milliseconds

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

    def measure_memory_usage(self, name: str = "memory_usage") -> Dict[str, float]:
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
        self, interval: float = 0.1, name: str = "cpu_usage"
    ) -> float:
        """Measure CPU usage and record as metric."""
        cpu_percent = psutil.cpu_percent(interval=interval)
        self.record_metric(name, cpu_percent, "%")
        return cpu_percent

    def benchmark_function(
        self, func: Callable, iterations: int = 100, *args, **kwargs
    ) -> Dict[str, float]:
        """Benchmark a function with multiple iterations and statistical analysis."""
        execution_times = []

        for i in range(iterations):
            start_time = time.perf_counter()
            func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_times.append((end_time - start_time) * 1000)  # Convert to ms

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

    def get_metrics_summary(self) -> Dict[str, Any]:
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


class WebDriverPerformanceMonitor(PerformanceMonitor):
    """Specialized performance monitor for WebDriver operations."""

    def __init__(self):
        super().__init__("WebDriver")

        # Set default thresholds for web operations
        self.set_threshold("page_load_time", 5000, "ms")  # 5 seconds
        self.set_threshold("element_find_time", 1000, "ms")  # 1 second
        self.set_threshold("click_operation_time", 500, "ms")  # 500ms
        self.set_threshold("form_fill_time", 2000, "ms")  # 2 seconds

    def monitor_page_load(self, driver, url: str) -> float:
        """Monitor page load performance."""
        start_time = time.perf_counter()
        driver.get(url)
        end_time = time.perf_counter()

        load_time = (end_time - start_time) * 1000
        self.record_metric("page_load_time", load_time, "ms", url=url)

        return load_time

    def monitor_element_find(self, driver, by, value: str) -> float:
        """Monitor element finding performance."""
        start_time = time.perf_counter()
        driver.find_element(by, value)
        end_time = time.perf_counter()

        find_time = (end_time - start_time) * 1000
        locator_str = f"{by}={value}" if isinstance(by, str) else f"{by.name}={value}"
        self.record_metric("element_find_time", find_time, "ms", locator=locator_str)

        return find_time


class APIPerformanceMonitor(PerformanceMonitor):
    """Specialized performance monitor for API operations."""

    def __init__(self):
        super().__init__("API")

        # Set default thresholds for API operations
        self.set_threshold("api_response_time", 2000, "ms")  # 2 seconds
        self.set_threshold("api_first_byte_time", 500, "ms")  # 500ms
        self.set_threshold("api_total_time", 3000, "ms")  # 3 seconds

    def monitor_api_request(
        self, session, method: str, url: str, **kwargs
    ) -> Dict[str, float]:
        """Monitor API request performance with detailed timing."""
        start_time = time.perf_counter()
        response = getattr(session, method.lower())(url, **kwargs)
        end_time = time.perf_counter()

        total_time = (end_time - start_time) * 1000

        # Extract response timing if available
        response_time = response.elapsed.total_seconds() * 1000

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


def benchmark_decorator(iterations: int = 100, name: str = None):
    """Pytest benchmark decorator for performance testing."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if running under pytest-benchmark
            if hasattr(kwargs.get("benchmark"), "__call__"):
                # Use pytest-benchmark if available in kwargs
                benchmark = kwargs.pop("benchmark")
                return benchmark(func, *args, **kwargs)
            else:
                # Fallback to manual benchmarking
                monitor = PerformanceMonitor(name or func.__name__)
                return monitor.benchmark_function(func, iterations, *args, **kwargs)

        return wrapper

    return decorator


def performance_test(threshold_ms: float = None, name: str = None):
    """Decorator for performance testing with threshold validation."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor(name or func.__name__)

            if threshold_ms:
                monitor.set_threshold(f"{func.__name__}_execution", threshold_ms, "ms")

            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()

            execution_time = (end_time - start_time) * 1000
            monitor.record_metric(f"{func.__name__}_execution", execution_time, "ms")

            if threshold_ms and execution_time > threshold_ms:
                raise AssertionError(
                    f"Performance threshold exceeded: {
                        execution_time:.2f}ms > {threshold_ms}ms"
                )

            return result

        return wrapper

    return decorator


# Global performance monitor instances
web_performance = WebDriverPerformanceMonitor()
api_performance = APIPerformanceMonitor()
general_performance = PerformanceMonitor("General")
