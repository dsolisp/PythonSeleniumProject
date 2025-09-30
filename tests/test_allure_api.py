"""
Enhanced API tests with Allure reporting and structured logging.
Demonstrates enterprise-grade API testing with detailed reporting.
"""

import allure
import pytest
import json
import time
import requests
from typing import Dict, Any

from utils.structured_logger import get_test_logger


@allure.epic("API Testing")
@allure.feature("REST API Validation")
class TestAllureAPI:
    """Enhanced API tests with Allure reporting and structured logging."""

    def setup_method(self, method):
        """Set up test environment with structured logging."""
        self.test_logger = get_test_logger(method.__name__)
        self.test_logger.start_test(
            test_type="API",
            test_suite="REST API Allure",
            framework="requests"
        )
        
        # Base configuration
        self.base_url = "https://jsonplaceholder.typicode.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "TestFramework-Allure/1.0"
        })

    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'session'):
            self.session.close()
            self.test_logger.log_step("Session cleanup", "close_session")
        
        self.test_logger.end_test("COMPLETED")

    def _get_test_name(self) -> str:
        """Get current test method name."""
        return self._pytestfixturefunction.__name__ if hasattr(self, '_pytestfixturefunction') else "unknown_test"

    def _log_api_response(self, response: requests.Response, operation: str) -> None:
        """Log API response details for debugging and reporting."""
        self.test_logger.api_request(
            method=response.request.method,
            url=response.url,
            status_code=response.status_code,
            response_time=response.elapsed.total_seconds() * 1000
        )
        
        # Attach response details to Allure
        allure.attach(
            f"Method: {response.request.method}\n"
            f"URL: {response.url}\n"
            f"Status Code: {response.status_code}\n"
            f"Response Time: {response.elapsed.total_seconds() * 1000:.2f}ms\n"
            f"Headers: {dict(response.headers)}\n"
            f"Body: {response.text[:500]}{'...' if len(response.text) > 500 else ''}",
            name=f"{operation} - API Response Details",
            attachment_type=allure.attachment_type.TEXT
        )

    @allure.story("GET Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify GET /posts endpoint functionality")
    @allure.description("""
    Test the GET /posts endpoint to ensure it returns a list of posts
    with proper structure and data validation.
    """)
    @allure.tag("smoke", "api", "get")
    def test_get_posts_with_allure(self):
        """Test GET /posts endpoint with enhanced reporting."""
        
        with allure.step("Send GET request to /posts endpoint"):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/posts")
            response_time = (time.time() - start_time) * 1000
            
            self._log_api_response(response, "GET Posts")
            self.test_logger.performance_metric("get_posts_response_time", response_time, "ms")

        with allure.step("Verify response status code"):
            self.test_logger.log_assertion(
                "Status code is 200",
                response.status_code == 200,
                expected=200,
                actual=response.status_code
            )
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Verify response content type"):
            content_type = response.headers.get('content-type', '')
            self.test_logger.log_assertion(
                "Content type is JSON",
                'application/json' in content_type,
                expected="application/json",
                actual=content_type
            )
            assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"

        with allure.step("Parse and validate JSON response"):
            try:
                posts = response.json()
                self.test_logger.log_step("JSON parsing", "parse_response")
            except json.JSONDecodeError as e:
                self.test_logger.exception_caught(e, "JSON parsing failed")
                raise AssertionError(f"Failed to parse JSON response: {e}")

        with allure.step("Verify posts structure and content"):
            # Verify it's a list
            self.test_logger.log_assertion(
                "Response is a list",
                isinstance(posts, list),
                expected="list",
                actual=type(posts).__name__
            )
            assert isinstance(posts, list), f"Expected list, got {type(posts)}"
            
            # Verify list is not empty
            self.test_logger.log_assertion(
                "Posts list not empty",
                len(posts) > 0,
                expected=">0 posts",
                actual=len(posts)
            )
            assert len(posts) > 0, "Posts list should not be empty"
            
            # Attach posts count to Allure
            allure.attach(
                f"Total posts retrieved: {len(posts)}",
                name="Posts Count",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Validate individual post structure"):
            first_post = posts[0]
            required_fields = ['id', 'title', 'body', 'userId']
            
            for field in required_fields:
                self.test_logger.log_assertion(
                    f"Post has '{field}' field",
                    field in first_post,
                    expected=f"'{field}' field present",
                    actual=f"Fields: {list(first_post.keys())}"
                )
                assert field in first_post, f"Post missing required field: {field}"
            
            # Attach first post sample to Allure
            allure.attach(
                json.dumps(first_post, indent=2),
                name="Sample Post Structure",
                attachment_type=allure.attachment_type.JSON
            )

        self.test_logger.end_test("PASS")

    @allure.story("GET Operations")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify GET /posts/{id} endpoint")
    @allure.description("Test retrieving a specific post by ID")
    @allure.tag("api", "get", "parametrized")
    def test_get_single_post_with_allure(self):
        """Test GET /posts/{id} endpoint."""
        
        post_id = 1
        
        with allure.step(f"Send GET request to /posts/{post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{post_id}")
            self._log_api_response(response, f"GET Post {post_id}")

        with allure.step("Verify successful response"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            self.test_logger.log_assertion(
                "Single post retrieval successful",
                response.status_code == 200,
                expected=200,
                actual=response.status_code
            )

        with allure.step("Validate post data"):
            post = response.json()
            
            # Verify ID matches
            self.test_logger.log_assertion(
                "Post ID matches request",
                post['id'] == post_id,
                expected=post_id,
                actual=post['id']
            )
            assert post['id'] == post_id, f"Expected post ID {post_id}, got {post['id']}"
            
            # Verify data types
            assert isinstance(post['title'], str), "Title should be string"
            assert isinstance(post['body'], str), "Body should be string"
            assert isinstance(post['userId'], int), "UserId should be integer"
            
            allure.attach(
                json.dumps(post, indent=2),
                name=f"Post {post_id} Details",
                attachment_type=allure.attachment_type.JSON
            )

        self.test_logger.end_test("PASS")

    @allure.story("POST Operations")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify POST /posts endpoint for creating new posts")
    @allure.description("Test creating a new post via POST request")
    @allure.tag("api", "post", "create")
    def test_create_post_with_allure(self):
        """Test POST /posts endpoint for creating new posts."""
        
        new_post_data = {
            "title": "Test Post via Allure",
            "body": "This is a test post created during API testing with Allure reporting",
            "userId": 1
        }
        
        with allure.step("Prepare POST request data"):
            allure.attach(
                json.dumps(new_post_data, indent=2),
                name="Request Payload",
                attachment_type=allure.attachment_type.JSON
            )
            self.test_logger.log_step("Request preparation", "create_payload")

        with allure.step("Send POST request to create new post"):
            response = self.session.post(
                f"{self.base_url}/posts",
                json=new_post_data
            )
            self._log_api_response(response, "POST Create Post")

        with allure.step("Verify post creation response"):
            self.test_logger.log_assertion(
                "Post creation successful",
                response.status_code == 201,
                expected=201,
                actual=response.status_code
            )
            assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        with allure.step("Validate created post data"):
            created_post = response.json()
            
            # Verify the created post has an ID
            assert 'id' in created_post, "Created post should have an ID"
            self.test_logger.log_assertion(
                "Created post has ID",
                'id' in created_post,
                expected="ID field present",
                actual=f"Fields: {list(created_post.keys())}"
            )
            
            # Verify the data matches what we sent
            for key, value in new_post_data.items():
                assert created_post[key] == value, f"Expected {key}='{value}', got '{created_post[key]}'"
                self.test_logger.log_assertion(
                    f"Created post {key} matches",
                    created_post[key] == value,
                    expected=value,
                    actual=created_post[key]
                )
            
            allure.attach(
                json.dumps(created_post, indent=2),
                name="Created Post Response",
                attachment_type=allure.attachment_type.JSON
            )

        self.test_logger.end_test("PASS")

    @allure.story("Error Handling")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify 404 error for non-existent post")
    @allure.description("Test API error handling for invalid post ID")
    @allure.tag("api", "error_handling", "404")
    def test_get_nonexistent_post_with_allure(self):
        """Test GET request for non-existent post."""
        
        invalid_post_id = 99999
        
        with allure.step(f"Request non-existent post ID {invalid_post_id}"):
            response = self.session.get(f"{self.base_url}/posts/{invalid_post_id}")
            self._log_api_response(response, f"GET Invalid Post {invalid_post_id}")

        with allure.step("Verify 404 error response"):
            self.test_logger.log_assertion(
                "Returns 404 for invalid post",
                response.status_code == 404,
                expected=404,
                actual=response.status_code
            )
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

        with allure.step("Verify error response structure"):
            # Some APIs return empty body for 404, others return error details
            if response.content:
                try:
                    error_data = response.json()
                    allure.attach(
                        json.dumps(error_data, indent=2),
                        name="Error Response",
                        attachment_type=allure.attachment_type.JSON
                    )
                except json.JSONDecodeError:
                    allure.attach(
                        response.text,
                        name="Error Response (Text)",
                        attachment_type=allure.attachment_type.TEXT
                    )

        self.test_logger.end_test("PASS")

    @allure.story("Performance Testing")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("API performance benchmarking")
    @allure.description("Measure and validate API response times")
    @allure.tag("performance", "benchmark")
    def test_api_performance_with_allure(self):
        """Test API performance and response times."""
        
        performance_data = []
        num_requests = 5
        max_response_time = 2000  # 2 seconds
        
        with allure.step(f"Execute {num_requests} API requests for performance measurement"):
            for i in range(num_requests):
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/posts/1")
                response_time = (time.time() - start_time) * 1000
                
                performance_data.append({
                    "request": i + 1,
                    "response_time_ms": response_time,
                    "status_code": response.status_code
                })
                
                self.test_logger.performance_metric(
                    f"api_request_{i+1}_response_time",
                    response_time,
                    "ms"
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
                "all_successful": all(data["status_code"] == 200 for data in performance_data)
            }
            
            allure.attach(
                json.dumps(performance_summary, indent=2),
                name="Performance Summary",
                attachment_type=allure.attachment_type.JSON
            )
            
            # Log performance assertions
            self.test_logger.log_assertion(
                "Average response time acceptable",
                avg_response_time < max_response_time,
                expected=f"<{max_response_time}ms",
                actual=f"{avg_response_time:.2f}ms"
            )
            
            self.test_logger.log_assertion(
                "All requests successful",
                all(data["status_code"] == 200 for data in performance_data),
                expected="All 200 status codes",
                actual=f"Status codes: {[data['status_code'] for data in performance_data]}"
            )

        with allure.step("Validate performance requirements"):
            assert avg_response_time < max_response_time, f"Average response time too slow: {avg_response_time:.2f}ms"
            assert all(data["status_code"] == 200 for data in performance_data), "Some requests failed"

        self.test_logger.end_test("PASS")