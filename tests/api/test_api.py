"""
Unified API testing module with conditional Allure reporting.
Controlled by settings.ENABLE_ALLURE flag.
"""

import json
import time

import allure
import pytest
import requests
from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    has_key,
    instance_of,
    is_,
    is_in,
    less_than,
)

from config.settings import settings
from utils.structured_logger import get_test_logger


@allure.epic("API Testing")
@allure.feature("REST API Validation")
class TestUnifiedAPI:
    """Unified API tests with conditional Allure reporting."""

    def setup_method(self, method):
        """Setup test method with optional structured logging."""
        if settings.ENABLE_ALLURE:
            self.test_logger = get_test_logger(method.__name__)
            self.test_logger.start_test(
                test_type="API",
                test_suite="REST API",
                framework="requests",
            )

        self.base_url = settings.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": "TestFramework/1.0",
            },
        )

    def teardown_method(self):
        """Cleanup after test."""
        if hasattr(self, "session"):
            self.session.close()
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_step("Session cleanup", "close_session")

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
            self.test_logger.end_test("COMPLETED")

    def _log_api_response(self, response: requests.Response, operation: str) -> None:
        """Log API response with optional Allure attachment."""
        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
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
                f"Response Time: "
                f"{response.elapsed.total_seconds() * 1000:.2f}ms\n"
                f"Headers: {dict(response.headers)}\n"
                f"Body: {response.text[:500]}"
                f"{'...' if len(response.text) > 500 else ''}",
                name=f"{operation} - API Response Details",
                attachment_type=allure.attachment_type.TEXT,
            )

    @pytest.mark.api
    @allure.story("GET Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify GET /posts endpoint functionality")
    @allure.description(
        """
        Test the GET /posts endpoint to ensure it returns a list of posts
        with proper structure and data validation.
        """,
    )
    @allure.tag("smoke", "api", "get")
    def test_get_posts(self):
        """Test GET /posts endpoint."""

        with allure.step("Send GET request to /posts endpoint"):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/posts")
            response_time = (time.time() - start_time) * 1000

            self._log_api_response(response, "GET Posts")
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.performance_metric(
                    "get_posts_response_time",
                    response_time,
                    "ms",
                )

        with allure.step("Verify response status code"):
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Status code is 200",
                    result=response.status_code == 200,
                    expected=200,
                    actual=response.status_code,
                )
            (
                assert_that(
                    response.status_code,
                    equal_to(200),
                ),
                f"Expected 200, got {response.status_code}",
            )

        with allure.step("Verify response content type"):
            content_type = response.headers.get("content-type", "")
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Content type is JSON",
                    result="application/json" in content_type,
                    expected="application/json",
                    actual=content_type,
                )
            (
                assert_that(
                    content_type,
                    contains_string("application/json"),
                ),
                f"Expected JSON content type, got {content_type}",
            )

        with allure.step("Parse and validate JSON response"):
            try:
                posts = response.json()
                if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                    self.test_logger.log_step("JSON parsing", "parse_response")
            except json.JSONDecodeError as e:
                if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                    self.test_logger.exception_caught(e, "JSON parsing failed")
                pytest.fail(f"Failed to parse JSON response: {e}")

        with allure.step("Verify posts structure and content"):
            # Verify it's a list
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Response is a list",
                    result=isinstance(posts, list),
                    expected="list",
                    actual=type(posts).__name__,
                )
            assert_that(posts, instance_of(list)), f"Expected list, got {type(posts)}"

            # Verify list is not empty
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Posts list not empty",
                    result=len(posts) > 0,
                    expected=">0 posts",
                    actual=len(posts),
                )
            assert_that(len(posts), greater_than(0)), "Posts list should not be empty"

            # Attach posts count to Allure
            if settings.ENABLE_ALLURE:
                allure.attach(
                    f"Total posts retrieved: {len(posts)}",
                    name="Posts Count",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("Validate individual post structure"):
            first_post = posts[0]
            required_fields = ["id", "title", "body", "userId"]

            for field in required_fields:
                if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                    self.test_logger.log_assertion(
                        assertion=f"Post has '{field}' field",
                        result=field in first_post,
                        expected=f"'{field}' field present",
                        actual=f"Fields: {list(first_post.keys())}",
                    )
                (
                    assert_that(
                        first_post,
                        has_key(field),
                    ),
                    f"Post missing required field: {field}",
                )

            # Attach first post sample to Allure
            if settings.ENABLE_ALLURE:
                allure.attach(
                    json.dumps(first_post, indent=2),
                    name="Sample Post Structure",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")

        print("✅ GET /posts test completed successfully")
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

        with allure.step(f"Send GET request to /posts/{post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{post_id}")
            self._log_api_response(response, f"GET Post {post_id}")

        with allure.step("Verify successful response"):
            (
                assert_that(
                    response.status_code,
                    equal_to(200),
                ),
                f"Expected 200, got {response.status_code}",
            )

            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Single post retrieval successful",
                    result=response.status_code == 200,
                    expected=200,
                    actual=response.status_code,
                )

        with allure.step("Validate post data"):
            post = response.json()

            # Verify ID matches
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Post ID matches request",
                    result=post["id"] == post_id,
                    expected=post_id,
                    actual=post["id"],
                )
            (
                assert_that(
                    post["id"],
                    equal_to(post_id),
                ),
                f"Expected post ID {post_id}, got {post['id']}",
            )

            # Verify data types
            assert_that(post["title"], instance_of(str)), "Title should be string"
            assert_that(post["body"], instance_of(str)), "Body should be string"
            assert_that(post["userId"], instance_of(int)), "UserId should be integer"

            if settings.ENABLE_ALLURE:
                allure.attach(
                    json.dumps(post, indent=2),
                    name=f"Post {post_id} Details",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
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

        with allure.step("Prepare POST request data"):
            if settings.ENABLE_ALLURE:
                allure.attach(
                    json.dumps(new_post_data, indent=2),
                    name="Request Payload",
                    attachment_type=allure.attachment_type.JSON,
                )
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_step("Request preparation", "create_payload")

        with allure.step("Send POST request to create new post"):
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/posts", json=new_post_data)
            response_time = time.time() - start_time
            self._log_api_response(response, "POST Create Post")

        with allure.step("Verify post creation response"):
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Post creation successful",
                    result=response.status_code == 201,
                    expected=201,
                    actual=response.status_code,
                )
            (
                assert_that(
                    response.status_code,
                    equal_to(201),
                ),
                f"Expected 201, got {response.status_code}",
            )

        with allure.step("Validate created post data"):
            created_post = response.json()

            # Verify the created post has an ID
            assert_that(created_post, has_key("id")), "Created post should have an ID"
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Created post has ID",
                    result="id" in created_post,
                    expected="ID field present",
                    actual=f"Fields: {list(created_post.keys())}",
                )

            # Verify the data matches what we sent
            for key, value in new_post_data.items():
                (
                    assert_that(
                        created_post[key],
                        equal_to(value),
                    ),
                    f"Expected {key}='{value}', got '{created_post[key]}'",
                )
                if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                    self.test_logger.log_assertion(
                        assertion=f"Created post {key} matches",
                        result=created_post[key] == value,
                        expected=value,
                        actual=created_post[key],
                    )

            if settings.ENABLE_ALLURE:
                allure.attach(
                    json.dumps(created_post, indent=2),
                    name="Created Post Response",
                    attachment_type=allure.attachment_type.JSON,
                )

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
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

        with allure.step(f"Request non-existent post ID {invalid_post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{invalid_post_id}")
            self._log_api_response(response, f"GET Invalid Post {invalid_post_id}")

        with allure.step("Verify 404 error response"):
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Returns 404 for invalid post",
                    result=response.status_code == 404,
                    expected=404,
                    actual=response.status_code,
                )
            (
                assert_that(
                    response.status_code,
                    equal_to(404),
                ),
                f"Expected 404, got {response.status_code}",
            )

        with allure.step("Verify error response structure"):
            # Some APIs return empty body for 404, others return error details
            if response.content:
                try:
                    error_data = response.json()
                    if settings.ENABLE_ALLURE:
                        allure.attach(
                            json.dumps(error_data, indent=2),
                            name="Error Response",
                            attachment_type=allure.attachment_type.JSON,
                        )
                except json.JSONDecodeError:
                    if settings.ENABLE_ALLURE:
                        allure.attach(
                            response.text,
                            name="Error Response (Text)",
                            attachment_type=allure.attachment_type.TEXT,
                        )

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")

        print("✅ 404 error handling works correctly")

        # Also test invalid data handling
        with allure.step("Test invalid data handling"):
            invalid_response = self.session.post(
                f"{self.base_url}/posts",
                json={"invalid": "data"},
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

        with allure.step(
            f"Execute {num_requests} API requests for performance measurement",
        ):
            for i in range(num_requests):
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/posts/{i + 1}")
                response_time = (time.time() - start_time) * 1000

                performance_data.append(
                    {
                        "request": i + 1,
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                    },
                )

                if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                    self.test_logger.performance_metric(
                        f"api_request_{i + 1}_response_time",
                        response_time,
                        "ms",
                    )

        with allure.step("Analyze performance metrics"):
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

            if settings.ENABLE_ALLURE:
                allure.attach(
                    json.dumps(performance_summary, indent=2),
                    name="Performance Summary",
                    attachment_type=allure.attachment_type.JSON,
                )

            # Log performance assertions
            if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
                self.test_logger.log_assertion(
                    assertion="Average response time acceptable",
                    result=avg_response_time < max_response_time,
                    expected=f"<{max_response_time}ms",
                    actual=f"{avg_response_time:.2f}ms",
                )

                self.test_logger.log_assertion(
                    assertion="All requests successful",
                    result=all(data["status_code"] == 200 for data in performance_data),
                    expected="All 200 status codes",
                    actual=(
                        f"Status codes: "
                        f"{[data['status_code'] for data in performance_data]}"
                    ),
                )

        with allure.step("Validate performance requirements"):
            (
                assert_that(
                    avg_response_time,
                    less_than(max_response_time),
                ),
                f"Average response time too slow: {avg_response_time:.2f}ms",
            )
            (
                assert_that(
                    all(data["status_code"] == 200 for data in performance_data),
                    is_(True),
                ),
                "Some requests failed",
            )

        if settings.ENABLE_ALLURE and hasattr(self, "test_logger"):
            self.test_logger.end_test("PASS")

        print("✅ Performance test completed")
        print(f"Average response time: {avg_response_time / 1000:.2f}s")
