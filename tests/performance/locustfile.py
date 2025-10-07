"""
Locust load testing configuration for API and web performance testing.
"""

import random
import time

from locust import HttpUser, between, events, task
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from utils.structured_logger import get_logger
from utils.webdriver_factory import WebDriverFactory


class APILoadTestUser(HttpUser):
    """
    Load testing user for API endpoints.

    Simulates realistic user behavior with:
    - Random wait times between requests
    - Multiple API endpoints
    - Data validation
    - Performance monitoring
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize user session and logging."""
        self.logger = get_logger("LoadTest.API")
        self.user_data = {
            "user_id": f"load_test_user_{random.randint(1000, 9999)}",
            "session_start": time.time(),
        }
        self.logger.info("Load test user started", **self.user_data)

    def on_stop(self):
        """Cleanup and log session summary."""
        session_duration = time.time() - self.user_data["session_start"]
        self.logger.info(
            "Load test user stopped",
            user_id=self.user_data["user_id"],
            session_duration=session_duration,
        )

    @task(3)  # Weight 3 - most common operation
    def test_api_get_request(self):
        """Test GET request performance."""
        with self.client.get(
            "/api/test",
            headers={"User-Agent": f"LoadTest-{self.user_data['user_id']}"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                self.logger.debug("GET request successful", status_code=200)
            else:
                response.failure(
                    f"Unexpected status code: {
                        response.status_code}"
                )
                self.logger.warning(
                    "GET request failed", status_code=response.status_code
                )

    @task(2)  # Weight 2 - common operation
    def test_api_post_request(self):
        """Test POST request performance with data."""
        test_data = {
            "user_id": self.user_data["user_id"],
            "timestamp": time.time(),
            "data": f"test_data_{random.randint(1, 1000)}",
        }

        with self.client.post(
            "/api/data",
            json=test_data,
            headers={"Content-Type": "application/json"},
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
                self.logger.debug(
                    "POST request successful",
                    status_code=response.status_code,
                    data_size=len(str(test_data)),
                )
            else:
                response.failure(f"POST failed: {response.status_code}")
                self.logger.warning(
                    "POST request failed", status_code=response.status_code
                )

    @task(1)  # Weight 1 - less common operation
    def test_api_search(self):
        """Test search API performance."""
        search_terms = ["selenium", "python", "testing", "automation", "performance"]
        search_term = random.choice(search_terms)

        with self.client.get(
            f"/api/search?q={search_term}", catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and "results" in data:
                        response.success()
                        self.logger.debug(
                            "Search successful",
                            search_term=search_term,
                            results_count=len(data.get("results", [])),
                        )
                    else:
                        response.failure("Invalid response format")
                        self.logger.warning("Search response invalid format")
                except Exception as e:
                    response.failure(f"JSON parsing failed: {e}")
                    self.logger.error("Search JSON parsing failed", error=str(e))
            else:
                response.failure(f"Search failed: {response.status_code}")


class WebUILoadTestUser(HttpUser):
    """
    Load testing user for web UI using Selenium.

    Note: This is for demonstration. In production, use Locust's built-in
    HTTP client for better performance, or dedicated tools like Selenium Grid.
    """

    wait_time = between(2, 5)  # Longer wait times for UI interactions

    def on_start(self):
        """Initialize WebDriver and logging."""
        self.logger = get_logger("LoadTest.WebUI")
        self.user_id = f"ui_load_test_{random.randint(1000, 9999)}"

        # Initialize WebDriver (use headless for load testing)
        factory = WebDriverFactory()
        self.driver = factory.create_driver("chrome", headless=True)

        self.logger.info("Web UI load test user started", user_id=self.user_id)

    def on_stop(self):
        """Cleanup WebDriver."""
        if hasattr(self, "driver"):
            self.driver.quit()
        self.logger.info("Web UI load test user stopped", user_id=self.user_id)

    @task
    def test_google_search_flow(self):
        """Test complete Google search flow."""
        try:
            start_time = time.time()

            # Navigate to Google
            self.driver.get(settings.BASE_URL)

            # Find and interact with search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )

            search_term = f"selenium testing {random.randint(1, 100)}"
            search_box.clear()
            search_box.send_keys(search_term)
            search_box.submit()

            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )

            total_time = time.time() - start_time

            self.logger.info(
                "Google search flow completed",
                user_id=self.user_id,
                search_term=search_term,
                duration=total_time,
            )

        except Exception as e:
            self.logger.error(
                "Google search flow failed", user_id=self.user_id, error=str(e)
            )


# Locust event handlers for advanced monitoring
@events.request.add_listener
def request_handler(
    request_type, name, response_time, response_length, exception, context, **kwargs
):
    """Log all requests for detailed monitoring."""
    logger = get_logger("LoadTest.Events")

    if exception:
        logger.error(
            "Request failed",
            request_type=request_type,
            name=name,
            response_time=response_time,
            exception=str(exception),
        )
    else:
        logger.info(
            "Request completed",
            request_type=request_type,
            name=name,
            response_time=response_time,
            response_length=response_length,
        )


@events.user_error.add_listener
def user_error_handler(user_instance, exception, tb, **kwargs):
    """Handle and log user errors."""
    logger = get_logger("LoadTest.Errors")
    logger.error(
        "User error occurred",
        user_class=user_instance.__class__.__name__,
        exception=str(exception),
        traceback=tb,
    )


@events.test_start.add_listener
def test_start_handler(environment, **kwargs):
    """Log test start with configuration."""
    logger = get_logger("LoadTest.Lifecycle")
    logger.info(
        "Load test started",
        host=environment.host,
        user_count=environment.runner.user_count if environment.runner else 0,
        spawn_rate=environment.runner.spawn_rate if environment.runner else 0,
    )


@events.test_stop.add_listener
def test_stop_handler(environment, **kwargs):
    """Log test completion with summary statistics."""
    logger = get_logger("LoadTest.Lifecycle")

    if environment.runner and environment.runner.stats:
        stats = environment.runner.stats
        total_stats = stats.total

        logger.info(
            "Load test completed",
            total_requests=total_stats.num_requests,
            total_failures=total_stats.num_failures,
            average_response_time=total_stats.avg_response_time,
            min_response_time=total_stats.min_response_time,
            max_response_time=total_stats.max_response_time,
            requests_per_second=total_stats.total_rps,
            failure_rate=total_stats.fail_ratio,
        )


# Load test scenarios configuration
LOAD_TEST_SCENARIOS = {
    "smoke_test": {
        "users": 1,
        "spawn_rate": 1,
        "duration": "30s",
        "description": "Quick smoke test with single user",
    },
    "baseline_test": {
        "users": 10,
        "spawn_rate": 2,
        "duration": "5m",
        "description": "Baseline performance test",
    },
    "stress_test": {
        "users": 50,
        "spawn_rate": 5,
        "duration": "10m",
        "description": "Stress test with moderate load",
    },
    "spike_test": {
        "users": 100,
        "spawn_rate": 20,
        "duration": "5m",
        "description": "Spike test with rapid user ramp-up",
    },
    "endurance_test": {
        "users": 25,
        "spawn_rate": 1,
        "duration": "30m",
        "description": "Long-running endurance test",
    },
}
