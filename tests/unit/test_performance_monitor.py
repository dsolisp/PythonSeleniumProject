from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    greater_than_or_equal_to,
    has_item,
    has_key,
    instance_of,
    is_,
    none,
    not_none,
)

"""
Unit tests for performance monitoring utilities.
"""

import threading
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from utils.performance_monitor import (
    APIPerformanceMonitor,
    PerformanceMetric,
    PerformanceMonitor,
    WebDriverPerformanceMonitor,
    benchmark_decorator,
    performance_test,
)


class TestPerformanceMetric:
    """Test PerformanceMetric data class."""

    def test_performance_metric_creation(self):
        """Test creating performance metric with all fields."""
        timestamp = datetime.now()
        context = {"test": "data"}

        metric = PerformanceMetric(
            name="test_metric",
            value=123.45,
            unit="ms",
            timestamp=timestamp,
            context=context,
        )

        assert_that(metric.name, equal_to("test_metric"))
        assert_that(metric.value, equal_to(123.45))
        assert_that(metric.unit, equal_to("ms"))
        assert_that(metric.timestamp, equal_to(timestamp))
        assert_that(metric.context, equal_to(context))

    def test_performance_metric_without_context(self):
        """Test creating performance metric without context."""
        metric = PerformanceMetric(
            name="simple_metric", value=100.0, unit="s", timestamp=datetime.now()
        )

        assert_that(metric.name, equal_to("simple_metric"))
        assert_that(metric.value, equal_to(100.0))
        assert_that(metric.unit, equal_to("s"))
        assert_that(metric.context, is_(none()))


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""

    def setup_method(self):
        """Setup for each test method."""
        self.monitor = PerformanceMonitor("TestMonitor")

    def test_performance_monitor_initialization(self):
        """Test performance monitor initialization."""
        assert_that(self.monitor.name, equal_to("TestMonitor"))
        assert_that(self.monitor.metrics, equal_to([]))
        assert_that(self.monitor.thresholds, equal_to({}))
        assert_that(self.monitor.logger, is_(not_none()))

    def test_set_threshold(self):
        """Test setting performance thresholds."""
        self.monitor.set_threshold("test_metric", 500.0, "ms")

        assert_that(self.monitor.thresholds, has_key("test_metric"))
        assert_that(self.monitor.thresholds["test_metric"], equal_to(500.0))

    def test_record_metric(self):
        """Test recording performance metrics."""
        self.monitor.record_metric("test_timing", 123.45, "ms", operation="test")

        assert_that(len(self.monitor.metrics), equal_to(1))
        metric = self.monitor.metrics[0]
        assert_that(metric.name, equal_to("test_timing"))
        assert_that(metric.value, equal_to(123.45))
        assert_that(metric.unit, equal_to("ms"))
        assert_that(metric.context["operation"], equal_to("test"))

    def test_record_metric_with_threshold_exceeded(self):
        """Test recording metric that exceeds threshold."""
        self.monitor.set_threshold("slow_operation", 100.0, "ms")

        # This should trigger threshold warning in logs
        self.monitor.record_metric("slow_operation", 200.0, "ms")

        assert_that(len(self.monitor.metrics), equal_to(1))
        assert_that(self.monitor.metrics[0].value, equal_to(200.0))

    def test_record_metric_within_threshold(self):
        """Test recording metric within threshold."""
        self.monitor.set_threshold("fast_operation", 100.0, "ms")

        self.monitor.record_metric("fast_operation", 50.0, "ms")

        assert_that(len(self.monitor.metrics), equal_to(1))
        assert_that(self.monitor.metrics[0].value, equal_to(50.0))

    def test_timer_decorator_success(self):
        """Test timer decorator with successful function."""

        @self.monitor.timer(name="test_function")
        def test_function():
            time.sleep(0.01)  # 10ms
            return "success"

        result = test_function()

        assert_that(result, equal_to("success"))
        assert_that(len(self.monitor.metrics), equal_to(1))

        metric = self.monitor.metrics[0]
        assert_that(metric.name, equal_to("test_function"))
        # Should be at least 10ms
        assert_that(metric.value, greater_than_or_equal_to(10))
        assert_that(metric.context["function"], equal_to("test_function"))
        assert_that(metric.context["success"], is_(True))
        assert_that(metric.context["error"], is_(none()))

    def test_timer_decorator_with_exception(self):
        """Test timer decorator with function that raises exception."""

        @self.monitor.timer(name="failing_function")
        def failing_function():
            time.sleep(0.01)
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

        assert_that(len(self.monitor.metrics), equal_to(1))

        metric = self.monitor.metrics[0]
        assert_that(metric.name, equal_to("failing_function"))
        assert_that(metric.value, greater_than_or_equal_to(10))
        assert_that(metric.context["success"], is_(False))
        assert_that(metric.context["error"], contains_string("Test error"))

    def test_timer_decorator_default_name(self):
        """Test timer decorator with default name."""

        @self.monitor.timer()
        def sample_function():
            return "done"

        result = sample_function()

        assert_that(result, equal_to("done"))
        assert_that(len(self.monitor.metrics), equal_to(1))
        assert_that(
            self.monitor.metrics[0].name, equal_to("sample_function_execution_time")
        )

    @patch("psutil.Process")
    def test_measure_memory_usage(self, mock_process_class):
        """Test memory usage measurement."""
        # Mock memory info
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_memory_info.vms = 200 * 1024 * 1024  # 200MB

        mock_process = Mock()
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.memory_percent.return_value = 15.5
        mock_process_class.return_value = mock_process

        metrics = self.monitor.measure_memory_usage("test_memory")

        assert_that(metrics["rss_mb"], equal_to(100.0))
        assert_that(metrics["vms_mb"], equal_to(200.0))
        assert_that(metrics["percent"], equal_to(15.5))

        # Should record 3 metrics
        assert_that(len(self.monitor.metrics), equal_to(3))
        metric_names = [m.name for m in self.monitor.metrics]
        assert_that(metric_names, has_item("test_memory_rss_mb"))
        assert_that(metric_names, has_item("test_memory_vms_mb"))
        assert_that(metric_names, has_item("test_memory_percent"))

    @patch("psutil.cpu_percent")
    def test_measure_cpu_usage(self, mock_cpu_percent):
        """Test CPU usage measurement."""
        mock_cpu_percent.return_value = 25.5

        cpu_usage = self.monitor.measure_cpu_usage(interval=0.1, name="test_cpu")

        assert_that(cpu_usage, equal_to(25.5))
        mock_cpu_percent.assert_called_once_with(interval=0.1)

        assert_that(len(self.monitor.metrics), equal_to(1))
        assert_that(self.monitor.metrics[0].name, equal_to("test_cpu"))
        assert_that(self.monitor.metrics[0].value, equal_to(25.5))
        assert_that(self.monitor.metrics[0].unit, equal_to("%"))

    def test_benchmark_function(self):
        """Test function benchmarking."""

        def test_func(delay):
            time.sleep(delay)
            return "completed"

        stats = self.monitor.benchmark_function(test_func, iterations=3, delay=0.01)

        assert_that(stats, has_key("mean"))
        assert_that(stats, has_key("median"))
        assert_that(stats, has_key("min"))
        assert_that(stats, has_key("max"))
        assert_that(stats, has_key("stddev"))
        assert_that(stats, has_key("iterations"))
        assert_that(stats["iterations"], equal_to(3))
        # Should be at least 10ms
        assert_that(stats["mean"], greater_than_or_equal_to(10))

        # Should record benchmark metrics
        recorded_metrics = len(self.monitor.metrics)
        # mean
        assert_that(recorded_metrics, equal_to(5))

    def test_get_metrics_summary_empty(self):
        """Test metrics summary with no metrics."""
        summary = self.monitor.get_metrics_summary()

        assert_that(summary["total_metrics"], equal_to(0))

    def test_get_metrics_summary_single_metric(self):
        """Test metrics summary with single metric."""
        self.monitor.record_metric("single_test", 100.0, "ms")

        summary = self.monitor.get_metrics_summary()

        assert_that(summary["total_metrics"], equal_to(1))
        assert_that(summary["unique_metric_names"], equal_to(1))
        assert_that(summary["metrics"], has_key("single_test"))

        metric_info = summary["metrics"]["single_test"]
        assert_that(metric_info["count"], equal_to(1))
        assert_that(metric_info["value"], equal_to(100.0))
        assert_that(metric_info["unit"], equal_to("ms"))

    def test_get_metrics_summary_multiple_metrics(self):
        """Test metrics summary with multiple metrics of same name."""
        # Record multiple metrics with same name
        self.monitor.record_metric("repeated_test", 100.0, "ms")
        self.monitor.record_metric("repeated_test", 200.0, "ms")
        self.monitor.record_metric("repeated_test", 150.0, "ms")

        summary = self.monitor.get_metrics_summary()

        assert_that(summary["total_metrics"], equal_to(3))
        assert_that(summary["unique_metric_names"], equal_to(1))

        metric_info = summary["metrics"]["repeated_test"]
        assert_that(metric_info["count"], equal_to(3))
        assert_that(metric_info["mean"], equal_to(150.0))
        assert_that(metric_info["min"], equal_to(100.0))
        assert_that(metric_info["max"], equal_to(200.0))
        assert_that(metric_info["unit"], equal_to("ms"))


class TestWebDriverPerformanceMonitor:
    """Test WebDriverPerformanceMonitor class."""

    def setup_method(self):
        """Setup for each test method."""
        self.web_monitor = WebDriverPerformanceMonitor()

    def test_webdriver_monitor_initialization(self):
        """Test WebDriver monitor initialization with default thresholds."""
        assert_that(self.web_monitor.name, equal_to("WebDriver"))
        assert_that(self.web_monitor.thresholds, has_key("page_load_time"))
        assert_that(self.web_monitor.thresholds, has_key("element_find_time"))
        assert_that(self.web_monitor.thresholds, has_key("click_operation_time"))
        assert_that(self.web_monitor.thresholds, has_key("form_fill_time"))

    def test_monitor_page_load(self):
        """Test page load monitoring."""
        # Mock driver
        mock_driver = Mock()

        load_time = self.web_monitor.monitor_page_load(mock_driver, "https://test.com")

        mock_driver.get.assert_called_once_with("https://test.com")
        assert_that(load_time, greater_than(0))
        assert_that(len(self.web_monitor.metrics), equal_to(1))

        metric = self.web_monitor.metrics[0]
        assert_that(metric.name, equal_to("page_load_time"))
        assert_that(metric.context["url"], equal_to("https://test.com"))

    def test_monitor_element_find(self):
        """Test element finding monitoring."""
        # Mock driver and element
        mock_element = Mock()
        mock_driver = Mock()
        mock_driver.find_element.return_value = mock_element

        from selenium.webdriver.common.by import By

        find_time = self.web_monitor.monitor_element_find(mock_driver, By.ID, "test-id")

        mock_driver.find_element.assert_called_once_with(By.ID, "test-id")
        assert_that(find_time, greater_than(0))
        assert_that(len(self.web_monitor.metrics), equal_to(1))

        metric = self.web_monitor.metrics[0]
        assert_that(metric.name, equal_to("element_find_time"))
        assert_that(metric.context["locator"], contains_string("id=test-id"))


class TestAPIPerformanceMonitor:
    """Test APIPerformanceMonitor class."""

    def setup_method(self):
        """Setup for each test method."""
        self.api_monitor = APIPerformanceMonitor()

    def test_api_monitor_initialization(self):
        """Test API monitor initialization with default thresholds."""
        assert_that(self.api_monitor.name, equal_to("API"))
        assert_that(self.api_monitor.thresholds, has_key("api_response_time"))
        assert_that(self.api_monitor.thresholds, has_key("api_first_byte_time"))
        assert_that(self.api_monitor.thresholds, has_key("api_total_time"))

    def test_monitor_api_request(self):
        """Test API request monitoring."""
        # Mock session and response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5  # 500ms

        mock_session = Mock()
        mock_session.get.return_value = mock_response

        timing_data = self.api_monitor.monitor_api_request(
            mock_session, "GET", "https://api.test.com/data"
        )

        mock_session.get.assert_called_once_with("https://api.test.com/data")

        assert_that(timing_data["response_time"], equal_to(500.0))
        assert_that(timing_data["status_code"], equal_to(200))
        assert_that(timing_data, has_key("total_time"))

        # Should record 2 metrics
        assert_that(len(self.api_monitor.metrics), equal_to(2))
        metric_names = [m.name for m in self.api_monitor.metrics]
        assert_that(metric_names, has_item("api_response_time"))
        assert_that(metric_names, has_item("api_total_time"))


class TestDecorators:
    """Test performance testing decorators."""

    def test_benchmark_decorator_with_pytest_benchmark(self):
        """Test benchmark decorator when pytest.benchmark is available."""
        # Mock benchmark function
        mock_benchmark = Mock(return_value="benchmark_result")

        @benchmark_decorator(iterations=5, name="test_benchmark")
        def test_function():
            return "test_result"

        result = test_function(benchmark=mock_benchmark)

        assert_that(result, equal_to("benchmark_result"))
        mock_benchmark.assert_called_once()

    def test_benchmark_decorator_fallback(self):
        """Test benchmark decorator fallback when pytest.benchmark not available."""

        @benchmark_decorator(iterations=3, name="fallback_test")
        def test_function():
            time.sleep(0.001)  # 1ms
            return "completed"

        result = test_function()

        # Should return benchmark statistics
        assert_that(result, instance_of(dict))
        assert_that(result, has_key("mean"))
        assert_that(result, has_key("iterations"))
        assert_that(result["iterations"], equal_to(3))

    def test_performance_test_decorator_within_threshold(self):
        """Test performance test decorator with execution within threshold."""

        @performance_test(threshold_ms=100, name="fast_test")
        def fast_function():
            time.sleep(0.01)  # 10ms - well within threshold
            return "completed"

        result = fast_function()
        assert_that(result, equal_to("completed"))

    def test_performance_test_decorator_exceeds_threshold(self):
        """Test performance test decorator with execution exceeding threshold."""

        @performance_test(threshold_ms=10, name="slow_test")
        def slow_function():
            time.sleep(0.05)  # 50ms - exceeds 10ms threshold
            return "completed"

        with pytest.raises(AssertionError, match="Performance threshold exceeded"):
            slow_function()

    def test_performance_test_decorator_without_threshold(self):
        """Test performance test decorator without threshold."""

        @performance_test(name="no_threshold_test")
        def normal_function():
            time.sleep(0.01)
            return "done"

        result = normal_function()
        assert_that(result, equal_to("done"))


class TestThreadSafety:
    """Test thread safety of performance monitoring."""

    def test_concurrent_metric_recording(self):
        """Test concurrent metric recording from multiple threads."""
        monitor = PerformanceMonitor("ThreadSafetyTest")
        results = []

        def record_metrics(thread_id):
            for i in range(10):
                monitor.record_metric(
                    f"thread_{thread_id}_metric_{i}", float(i), "units"
                )
                time.sleep(0.001)  # Small delay
            results.append(f"thread_{thread_id}_completed")

        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=record_metrics, args=(thread_id,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All threads should complete
        assert_that(len(results), equal_to(3))

        # All metrics should be recorded
        # 3 threads × 10 metrics
        assert_that(len(monitor.metrics), equal_to(30))

        # Verify metric names are unique
        metric_names = [m.name for m in monitor.metrics]
        # All names should be unique
        assert_that(len(set(metric_names)), equal_to(30))


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_function_name_in_timer(self):
        """Test timer decorator with function having empty name."""
        monitor = PerformanceMonitor("EdgeCaseTest")

        # Create function with empty name (edge case)
        def test_func():
            return "result"

        test_func.__name__ = ""

        decorated_func = monitor.timer()(test_func)
        result = decorated_func()

        assert_that(result, equal_to("result"))
        assert_that(len(monitor.metrics), equal_to(1))
        assert_that(monitor.metrics[0].name, equal_to("_execution_time"))

    def test_very_large_metric_values(self):
        """Test handling of very large metric values."""
        monitor = PerformanceMonitor("LargeValueTest")

        large_value = float(10**10)  # 10 billion
        monitor.record_metric("large_metric", large_value, "units")

        assert_that(len(monitor.metrics), equal_to(1))
        assert_that(monitor.metrics[0].value, equal_to(large_value))

    def test_zero_and_negative_metric_values(self):
        """Test handling of zero and negative metric values."""
        monitor = PerformanceMonitor("ZeroNegativeTest")

        monitor.record_metric("zero_metric", 0.0, "units")
        monitor.record_metric("negative_metric", -100.0, "units")

        assert_that(len(monitor.metrics), equal_to(2))
        assert_that(monitor.metrics[0].value, equal_to(0.0))
        assert_that(monitor.metrics[1].value, equal_to(-100.0))
