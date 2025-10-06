"""
Unified API testing module with conditional Allure reporting.
Controlled by settings.ENABLE_ALLURE flag.
"""

import json
import time
from typing import Optional

import pytest
import requests
from hamcrest import (
    assert_that,
    is_,
    equal_to,
    greater_than,
    less_than,
    instance_of,
    has_key,
    contains_string,
    has_item,
    not_none,
    has_length,
    is_in,
)

from config.settings import settings
from utils.structured_logger import get_test_logger

# Conditional Allure import
try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False
    # Create dummy decorators if Allure is not available
    class allure:
        @staticmethod
        def epic(name): return lambda f: f
        @staticmethod
        def feature(name): return lambda f: f
        @staticmethod
        def story(name): return lambda f: f
        @staticmethod
        def severity(level): return lambda f: f
        @staticmethod
        def title(name): return lambda f: f
        @staticmethod
        def description(text): return lambda f: f
        @staticmethod
        def tag(*tags): return lambda f: f
        @staticmethod
        def step(name): 
            from contextlib import contextmanager
            @contextmanager
            def _step():
                yield
            return _step()
        @staticmethod
        def attach(body, name, attachment_type): pass
        
        class severity_level:
            CRITICAL = "critical"
            NORMAL = "normal"
            MINOR = "minor"
        
        class attachment_type:
            TEXT = "text"
            JSON = "json"


def conditional_allure_class_decorator(cls):
    """Conditionally apply Allure class decorators."""
    if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
        cls = allure.epic("API Testing")(cls)
        cls = allure.feature("REST API Validation")(cls)
    return cls


def conditional_allure_method(*decorators):
    """Conditionally apply Allure method decorators."""
    def decorator(func):
        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
            for dec in reversed(decorators):
                func = dec(func)
        return func
    return decorator


@conditional_allure_class_decorator
class TestUnifiedAPI:
    """Unified API tests with conditional Allure reporting."""

    def setup_method(self, method):
        """Setup test method with optional structured logging."""
        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
            self.test_logger = get_test_logger(method.__name__)
            self.test_logger.start_test(
                test_type="API", test_suite="REST API", framework="requests"
            )

        self.base_url = settings.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "TestFramework/1.0",
            }
        )

    def teardown_method(self):
        """Cleanup after test."""
        if hasattr(self, "session"):
            self.session.close()
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_step("Session cleanup", "close_session")

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("COMPLETED")

    def _log_api_response(self, response: requests.Response, operation: str) -> None:
        """Log API response with optional Allure attachment."""
        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.api_request(
                method=response.request.method,
                url=response.url,
                status_code=response.status_code,
                response_time=response.elapsed.total_seconds() * 1000,
            )

            allure.attach(
                f"Method: {response.request.method}\n"
                f"URL: {response.url}\n"
                f"Status Code: {response.status_code}\n"
                f"Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms\n"
                f"Headers: {dict(response.headers)}\n"
                f"Body: {response.text[:500]}{'...' if len(response.text) > 500 else ''}",
                name=f"{operation} - API Response Details",
                attachment_type=allure.attachment_type.TEXT,
            )

    def _step(self, description: str):
        """Conditional step context manager."""
        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
            return allure.step(description)
        else:
            from contextlib import contextmanager
            @contextmanager
            def _noop_step():
                yield
            return _noop_step()

    @pytest.mark.api
    @allure.story("GET Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify GET /posts endpoint functionality")
    @allure.description(
        """
        Test the GET /posts endpoint to ensure it returns a list of posts
        with proper structure and data validation.
        """
    )
    @allure.tag("smoke", "api", "get")
    def test_get_posts(self):
        """Test GET /posts endpoint."""
        
        with self._step("Send GET request to /posts endpoint"):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/posts")
            response_time = (time.time() - start_time) * 1000

            self._log_api_response(response, "GET Posts")
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.performance_metric(
                    "get_posts_response_time", response_time, "ms"
                )

        with self._step("Verify response status code"):
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Status code is 200",
                    response.status_code == 200,
                    expected=200,
                    actual=response.status_code,
                )
            assert_that(
                response.status_code, equal_to(200)
            ), f"Expected 200, got {response.status_code}"

        with self._step("Verify response content type"):
            content_type = response.headers.get("content-type", "")
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Content type is JSON",
                    "application/json" in content_type,
                    expected="application/json",
                    actual=content_type,
                )
            assert_that(
                content_type, contains_string("application/json")
            ), f"Expected JSON content type, got {content_type}"

        with self._step("Parse and validate JSON response"):
            try:
                posts = response.json()
                if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                    self.test_logger.log_step("JSON parsing", "parse_response")
            except json.JSONDecodeError as e:
                if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                    self.test_logger.exception_caught(e, "JSON parsing failed")
                pytest.fail(f"Failed to parse JSON response: {e}")

        with self._step("Verify posts structure and content"):
            # Verify it's a list
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Response is a list",
                    isinstance(posts, list),
                    expected="list",
                    actual=type(posts).__name__,
                )
            assert_that(posts, instance_of(list)), f"Expected list, got {type(posts)}"

            # Verify list is not empty
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Posts list not empty",
                    len(posts) > 0,
                    expected=">0 posts",
                    actual=len(posts),
                )
            assert_that(len(posts), greater_than(0)), "Posts list should not be empty"

            # Attach posts count to Allure
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    f"Total posts retrieved: {len(posts)}",
                    name="Posts Count",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with self._step("Validate individual post structure"):
            first_post = posts[0]
            required_fields = ["id", "title", "body", "userId"]

            for field in required_fields:
                if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                    self.test_logger.log_assertion(
                        f"Post has '{field}' field",
                        field in first_post,
                        expected=f"'{field}' field present",
                        actual=f"Fields: {list(first_post.keys())}",
                    )
                assert_that(
                    first_post, has_key(field)
                ), f"Post missing required field: {field}"

            # Attach first post sample to Allure
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    json.dumps(first_post, indent=2),
                    name="Sample Post Structure",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")
        
        print(f"✅ GET /posts test completed successfully")
        print(f"Retrieved {len(posts)} posts")

    @pytest.mark.api
    @allure.story("GET Operations")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify GET /posts/{id} endpoint")
    @allure.description("Test retrieving a specific post by ID")
    @allure.tag("api", "get", "parametrized")
    def test_get_single_post(self):
        """Test GET /posts/{id} endpoint."""
        
        post_id = 1

        with self._step(f"Send GET request to /posts/{post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{post_id}")
            self._log_api_response(response, f"GET Post {post_id}")

        with self._step("Verify successful response"):
            assert_that(
                response.status_code, equal_to(200)
            ), f"Expected 200, got {response.status_code}"

            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Single post retrieval successful",
                    response.status_code == 200,
                    expected=200,
                    actual=response.status_code,
                )

        with self._step("Validate post data"):
            post = response.json()

            # Verify ID matches
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Post ID matches request",
                    post["id"] == post_id,
                    expected=post_id,
                    actual=post["id"],
                )
            assert_that(
                post["id"], equal_to(post_id)
            ), f"Expected post ID {post_id}, got {post['id']}"

            # Verify data types
            assert_that(post["title"], instance_of(str)), "Title should be string"
            assert_that(post["body"], instance_of(str)), "Body should be string"
            assert_that(post["userId"], instance_of(int)), "UserId should be integer"

            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    json.dumps(post, indent=2),
                    name=f"Post {post_id} Details",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")
        
        print(f"✅ GET /posts/{post_id} test completed successfully")
        print(f"Retrieved post: {post['title'][:50]}...")

    @pytest.mark.api
    @allure.story("POST Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify POST /posts endpoint for creating new posts")
    @allure.description("Test creating a new post via POST request")
    @allure.tag("api", "post", "create")
    def test_create_post(self):
        """Test POST /posts endpoint for creating new posts."""
        
        new_post_data = {
            "title": "Python Test Post",
            "body": "This is a test post created by Python automation testing",
            "userId": 1,
        }

        with self._step("Prepare POST request data"):
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    json.dumps(new_post_data, indent=2),
                    name="Request Payload",
                    attachment_type=allure.attachment_type.JSON,
                )
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_step("Request preparation", "create_payload")

        with self._step("Send POST request to create new post"):
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/posts", json=new_post_data)
            response_time = time.time() - start_time
            self._log_api_response(response, "POST Create Post")

        with self._step("Verify post creation response"):
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Post creation successful",
                    response.status_code == 201,
                    expected=201,
                    actual=response.status_code,
                )
            assert_that(
                response.status_code, equal_to(201)
            ), f"Expected 201, got {response.status_code}"

        with self._step("Validate created post data"):
            created_post = response.json()

            # Verify the created post has an ID
            assert_that(created_post, has_key("id")), "Created post should have an ID"
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Created post has ID",
                    "id" in created_post,
                    expected="ID field present",
                    actual=f"Fields: {list(created_post.keys())}",
                )

            # Verify the data matches what we sent
            for key, value in new_post_data.items():
                assert_that(
                    created_post[key], equal_to(value)
                ), f"Expected {key}='{value}', got '{created_post[key]}'"
                if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                    self.test_logger.log_assertion(
                        f"Created post {key} matches",
                        created_post[key] == value,
                        expected=value,
                        actual=created_post[key],
                    )

            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    json.dumps(created_post, indent=2),
                    name="Created Post Response",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")
        
        print(f"✅ Created post with ID: {created_post['id']}")
        print(f"✅ API test completed successfully in {response_time:.2f}s")

    @pytest.mark.api
    @allure.story("Error Handling")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify 404 error for non-existent post")
    @allure.description("Test API error handling for invalid post ID")
    @allure.tag("api", "error_handling", "404")
    def test_get_nonexistent_post(self):
        """Test GET request for non-existent post."""
        
        invalid_post_id = 99999

        with self._step(f"Request non-existent post ID {invalid_post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{invalid_post_id}")
            self._log_api_response(response, f"GET Invalid Post {invalid_post_id}")

        with self._step("Verify 404 error response"):
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Returns 404 for invalid post",
                    response.status_code == 404,
                    expected=404,
                    actual=response.status_code,
                )
            assert_that(
                response.status_code, equal_to(404)
            ), f"Expected 404, got {response.status_code}"

        with self._step("Verify error response structure"):
            # Some APIs return empty body for 404, others return error details
            if response.content:
                try:
                    error_data = response.json()
                    if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                        allure.attach(
                            json.dumps(error_data, indent=2),
                            name="Error Response",
                            attachment_type=allure.attachment_type.JSON,
                        )
                except json.JSONDecodeError:
                    if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                        allure.attach(
                            response.text,
                            name="Error Response (Text)",
                            attachment_type=allure.attachment_type.TEXT,
                        )

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")
        
        print("✅ 404 error handling works correctly")
        
        # Also test invalid data handling
        with self._step("Test invalid data handling"):
            invalid_response = self.session.post(
                f"{self.base_url}/posts", json={"invalid": "data"}
            )
            assert_that(
                invalid_response.status_code,
                is_in([201, 400, 422]),
                "Should handle invalid data appropriately",
            )
            print("✅ Invalid data handling works correctly")

    @pytest.mark.api
    @allure.story("Performance Testing")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("API performance benchmarking")
    @allure.description("Measure and validate API response times")
    @allure.tag("performance", "benchmark")
    def test_api_performance(self):
        """Test API performance and response times."""
        
        performance_data = []
        num_requests = 5
        max_response_time = 2000  # 2 seconds in ms

        with self._step(
            f"Execute {num_requests} API requests for performance measurement"
        ):
            for i in range(num_requests):
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/posts/{i+1}")
                response_time = (time.time() - start_time) * 1000

                performance_data.append(
                    {
                        "request": i + 1,
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                    }
                )

                if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                    self.test_logger.performance_metric(
                        f"api_request_{i+1}_response_time", response_time, "ms"
                    )

        with self._step("Analyze performance metrics"):
            response_times = [data["response_time_ms"] for data in performance_data]
            avg_response_time = sum(response_times) / len(response_times)
            max_recorded_time = max(response_times)
            min_recorded_time = min(response_times)

            performance_summary = {
                "total_requests": num_requests,
                "average_response_time_ms": avg_response_time,
                "max_response_time_ms": max_recorded_time,
                "min_response_time_ms": min_recorded_time,
                "all_successful": all(
                    data["status_code"] == 200 for data in performance_data
                ),
            }

            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE:
                allure.attach(
                    json.dumps(performance_summary, indent=2),
                    name="Performance Summary",
                    attachment_type=allure.attachment_type.JSON,
                )

            # Log performance assertions
            if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    "Average response time acceptable",
                    avg_response_time < max_response_time,
                    expected=f"<{max_response_time}ms",
                    actual=f"{avg_response_time:.2f}ms",
                )

                self.test_logger.log_assertion(
                    "All requests successful",
                    all(data["status_code"] == 200 for data in performance_data),
                    expected="All 200 status codes",
                    actual=(
                        f"Status codes: "
                        f"{[data['status_code'] for data in performance_data]}"
                    ),
                )

        with self._step("Validate performance requirements"):
            assert_that(
                avg_response_time, less_than(max_response_time)
            ), f"Average response time too slow: {avg_response_time:.2f}ms"
            assert_that(
                all(data["status_code"] == 200 for data in performance_data), is_(True)
            ), "Some requests failed"

        if settings.ENABLE_ALLURE and ALLURE_AVAILABLE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")
        
        print(f"✅ Performance test completed")
        print(f"Average response time: {avg_response_time/1000:.2f}s")
