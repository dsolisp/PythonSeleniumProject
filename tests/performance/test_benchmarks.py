from hamcrest import (
    assert_that, is_, equal_to, not_none, none, greater_than, less_than, 
    greater_than_or_equal_to, less_than_or_equal_to, has_length, instance_of, 
    has_key, contains_string, has_property, is_in, is_not
)
"""
Performance benchmark tests using pytest-benchmark.
"""

import pytest
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.performance_monitor import (
    PerformanceMonitor, 
    web_performance, 
    api_performance,
    benchmark_decorator,
    performance_test
)
from utils.webdriver_factory import WebDriverFactory
from utils.structured_logger import get_logger
from config.settings import settings


class TestPerformanceBenchmarks:
    """Performance benchmark test suite using pytest-benchmark."""
    
    @classmethod
    def setup_class(cls):
        """Setup class-level resources."""
        cls.logger = get_logger("PerformanceBenchmarks")
        cls.monitor = PerformanceMonitor("BenchmarkTests")
        cls.logger.info("Performance benchmark test suite started")
    
    @classmethod
    def teardown_class(cls):
        """Cleanup and log performance summary."""
        summary = cls.monitor.get_metrics_summary()
        cls.logger.info("Performance benchmark suite completed", **summary)
    
    def test_webdriver_creation_benchmark(self, benchmark):
        """Benchmark WebDriver creation performance."""
        factory = WebDriverFactory()
        
        def create_and_quit_driver():
            driver = factory.create_driver("chrome", headless=True)
            driver.quit()
            return True
        
        # Benchmark with pytest-benchmark
        result = benchmark.pedantic(
            create_and_quit_driver,
            iterations=5,
            rounds=3,
            warmup_rounds=1
        )
        
        assert_that(result, is_(True))
        
        # Log benchmark results
        self.logger.info(
            "WebDriver creation benchmark completed",
            mean_time=benchmark.stats['mean'],
            min_time=benchmark.stats['min'],
            max_time=benchmark.stats['max'],
            stddev=benchmark.stats['stddev']
        )
    
    def test_google_search_performance_benchmark(self, benchmark):
        """Benchmark Google search operation."""
        factory = WebDriverFactory()
        driver = factory.create_driver("chrome", headless=True)
        
        def perform_google_search():
            try:
                driver.get(settings.BASE_URL)
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys("selenium testing performance")
                search_box.submit()
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "search"))
                )
                return True
            except Exception as e:
                self.logger.error("Google search failed", error=str(e))
                return False
        
        try:
            # Benchmark the search operation
            result = benchmark.pedantic(
                perform_google_search,
                iterations=3,
                rounds=2,
                warmup_rounds=1
            )
            
            assert_that(result, is_(True))
            
            self.logger.info(
                "Google search benchmark completed",
                mean_time=benchmark.stats['mean'],
                iterations=benchmark.stats['iterations']
            )
            
        finally:
            driver.quit()
    
    @benchmark_decorator(iterations=10, name="element_finding")
    def test_element_finding_benchmark(self, benchmark):
        """Benchmark element finding operations."""
        factory = WebDriverFactory()
        driver = factory.create_driver("chrome", headless=True)
        
        def find_elements_on_google():
            driver.get(settings.BASE_URL)
            
            # Find multiple elements
            elements_found = 0
            try:
                driver.find_element(By.NAME, "q")
                elements_found += 1
                driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                elements_found += 1
                driver.find_elements(By.TAG_NAME, "a")
                elements_found += 1
            except Exception as e:
                self.logger.warning("Element finding partial failure", error=str(e))
            
            return elements_found
        
        try:
            result = benchmark(find_elements_on_google)
            # At least one element should be found
            assert_that(result, greater_than_or_equal_to(1))
            
        finally:
            driver.quit()
    
    def test_api_request_benchmark(self, benchmark):
        """Benchmark API request performance."""
        # Using httpbin.org for reliable API testing
        test_url = settings.TEST_API_URL
        
        def make_api_request():
            try:
                response = requests.get(test_url, timeout=10)
                return response.status_code == 200 and response.json() is not None
            except Exception as e:
                self.logger.error("API request failed", error=str(e))
                return False
        
        result = benchmark.pedantic(
            make_api_request,
            iterations=10,
            rounds=3,
            warmup_rounds=1
        )
        
        assert_that(result, is_(True))
        
        self.logger.info(
            "API request benchmark completed",
            url=test_url,
            mean_time=benchmark.stats['mean']
        )
    
    def test_database_operation_benchmark(self, benchmark):
        """Benchmark database operations."""
        from utils.sql_connection import DatabaseConnection
        
        def database_operations():
            try:
                db = DatabaseConnection()
                connection = db.get_connection()
                cursor = connection.cursor()
                
                # Simple query operation
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                result = cursor.fetchone()
                
                cursor.close()
                connection.close()
                
                return result is not None
            except Exception as e:
                self.logger.error("Database operation failed", error=str(e))
                return False
        
        result = benchmark.pedantic(
            database_operations,
            iterations=20,
            rounds=3,
            warmup_rounds=2
        )
        
        assert_that(result, is_(True))
    
    @performance_test(threshold_ms=5000, name="page_load_threshold")
    def test_page_load_with_threshold(self):
        """Test page load with performance threshold validation."""
        factory = WebDriverFactory()
        driver = factory.create_driver("chrome", headless=True)
        
        try:
            start_time = time.perf_counter()
            driver.get(settings.BASE_URL)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            end_time = time.perf_counter()
            
            load_time = (end_time - start_time) * 1000
            self.logger.info("Page load test completed", load_time_ms=load_time)
            
            # Performance threshold is enforced by decorator
            # Should be less than 5 seconds
            assert_that(load_time, less_than(5000))
            
        finally:
            driver.quit()
    
    def test_memory_usage_benchmark(self, benchmark):
        """Benchmark memory usage during operations."""
        import psutil
        
        def memory_intensive_operation():
            # Simulate memory-intensive operation
            large_list = [i for i in range(10000)]
            large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
            
            process = psutil.Process()
            memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Cleanup
            del large_list, large_dict
            
            return memory_usage
        
        memory_usage = benchmark(memory_intensive_operation)
        
        self.logger.info(
            "Memory usage benchmark completed",
            peak_memory_mb=memory_usage,
            benchmark_time=benchmark.stats['mean']
        )
        
        # Assert reasonable memory usage (less than 500MB for this test)
        assert_that(memory_usage, less_than(500))
    
    def test_concurrent_operations_benchmark(self, benchmark):
        """Benchmark concurrent operations simulation."""
        import threading
        import queue
        
        def concurrent_operations():
            results = queue.Queue()
            threads = []
            
            def worker_task(task_id):
                # Simulate work
                time.sleep(0.01)  # 10ms of work
                results.put(f"task_{task_id}_completed")
            
            # Create and start threads
            for i in range(5):
                thread = threading.Thread(target=worker_task, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            completed_tasks = []
            while not results.empty():
                completed_tasks.append(results.get())
            
            return len(completed_tasks)
        
        result = benchmark.pedantic(
            concurrent_operations,
            iterations=5,
            rounds=2
        )
        
        # All 5 tasks should complete
        assert_that(result, equal_to(5))
        
        self.logger.info(
            "Concurrent operations benchmark completed",
            tasks_completed=result,
            mean_time=benchmark.stats['mean']
        )


class TestPerformanceMonitoringIntegration:
    """Test performance monitoring utilities integration."""
    
    def test_performance_monitor_timer_decorator(self):
        """Test performance monitor timer decorator."""
        monitor = PerformanceMonitor("TestMonitor")
        
        @monitor.timer(name="test_function_timing")
        def slow_function():
            time.sleep(0.1)  # 100ms delay
            return "completed"
        
        result = slow_function()
        assert_that(result, equal_to("completed"))
        
        # Check if metric was recorded
        metrics = monitor.get_metrics_summary()
        assert_that(metrics["total_metrics"], greater_than(0))
        assert_that(metrics["metrics"], contains_string("test_function_timing"))
        
        timing_metric = metrics["metrics"]["test_function_timing"]
        # Should be at least 100ms
        assert_that(timing_metric["value"], greater_than_or_equal_to(100))
    
    def test_web_performance_monitor(self):
        """Test WebDriver performance monitoring."""
        factory = WebDriverFactory()
        driver = factory.create_driver("chrome", headless=True)
        
        try:
            # Monitor page load
            load_time = web_performance.monitor_page_load(driver, settings.BASE_URL)
            assert_that(load_time, greater_than(0))
            
            # Monitor element finding
            find_time = web_performance.monitor_element_find(driver, By.NAME, "q")
            assert_that(find_time, greater_than(0))
            
            # Check metrics were recorded
            summary = web_performance.get_metrics_summary()
            assert_that(summary["total_metrics"], greater_than_or_equal_to(2))
            
        finally:
            driver.quit()
    
    def test_api_performance_monitor(self):
        """Test API performance monitoring."""
        import requests
        
        session = requests.Session()
        
        # Monitor API request
        timing_data = api_performance.monitor_api_request(
            session, "GET", settings.TEST_API_URL
        )
        
        assert_that(timing_data, contains_string("response_time"))
        assert_that(timing_data, contains_string("total_time"))
        assert_that(timing_data, contains_string("status_code"))
        assert_that(timing_data["status_code"], equal_to(200))
        
        # Check metrics were recorded
        summary = api_performance.get_metrics_summary()
        assert_that(summary["total_metrics"], greater_than_or_equal_to(2))