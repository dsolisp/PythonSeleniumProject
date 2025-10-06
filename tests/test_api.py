"""
API testing module using requests library.
"""

import time

import pytest
import requests
from hamcrest import (
    assert_that,
    equal_to,
    greater_than,
    less_than,
    has_key,
    instance_of,
    is_in,
    not_none,
    has_length,
)

from config.settings import settings

base_url = settings.API_BASE_URL


@pytest.mark.api
def test_create_and_retrieve_post():
    start_time = time.time()

    post_data = {
        "title": "Python Test Post",
        "body": "This is a test post created by Python",
        "userId": 1,
    }

    try:
        post_response = requests.post(f"{base_url}/posts", json=post_data, timeout=10)

        assert_that(post_response.status_code, equal_to(201))
        assert_that(
            post_response.headers.get("content-type"),
            not_none(),
            "Response should have content-type header",
        )

        post_json = post_response.json()
        assert_that(post_json, has_key("id"), "Response should contain 'id' field")
        assert_that(post_json["title"], equal_to(post_data["title"]))
        assert_that(post_json["body"], equal_to(post_data["body"]))

        post_id = post_json["id"]
        print(f"✅ Created post with ID: {post_id}")

        get_response = requests.get(f"{base_url}/posts/1", timeout=10)

        assert_that(get_response.status_code, equal_to(200))
        assert_that(
            get_response.headers.get("content-type"),
            not_none(),
            "Response should have content-type header",
        )

        get_json = get_response.json()

        required_fields = ["id", "title", "body", "userId"]
        for field in required_fields:
            assert_that(
                get_json, has_key(field), f"Response should contain '{field}' field"
            )

        assert_that(get_json["id"], instance_of(int), "ID should be an integer")
        assert_that(get_json["title"], instance_of(str), "Title should be a string")
        assert_that(get_json["body"], instance_of(str), "Body should be a string")
        assert_that(get_json["userId"], instance_of(int), "UserID should be an integer")

        assert_that(get_json["id"], equal_to(1))
        assert_that(get_json["userId"], greater_than(0))
        assert_that(
            get_json["title"], has_length(greater_than(0)), "Title should not be empty"
        )
        assert_that(
            get_json["body"], has_length(greater_than(0)), "Body should not be empty"
        )

        response_time = time.time() - start_time
        assert_that(
            response_time,
            less_than(5.0),
            f"API response too slow: {response_time:.2f}s",
        )

        print(f"✅ API test completed successfully in {response_time:.2f}s")
        print(f"Retrieved post: {get_json['title'][:50]}...")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Network error during API test: {e}")
    except ValueError as e:
        pytest.fail(f"JSON parsing error: {e}")
    except AssertionError as e:
        pytest.fail(f"API validation failed: {e}")


@pytest.mark.api
def test_api_error_handling():
    try:
        response = requests.get(f"{base_url}/posts/99999", timeout=10)
        assert_that(response.status_code, equal_to(404))
        print("✅ 404 error handling works correctly")

        invalid_response = requests.post(
            f"{base_url}/posts", json={"invalid": "data"}, timeout=10
        )
        assert_that(
            invalid_response.status_code,
            is_in([201, 400, 422]),
            "Should handle invalid data appropriately",
        )
        print("✅ Invalid data handling works correctly")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Network error during error handling test: {e}")


@pytest.mark.api
def test_api_performance():
    start_time = time.time()

    try:
        response_times = []
        for i in range(3):
            req_start = time.time()
            response = requests.get(f"{base_url}/posts/{i+1}", timeout=10)
            req_end = time.time()

            assert_that(response.status_code, equal_to(200))
            response_times.append(req_end - req_start)

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        assert_that(
            avg_response_time,
            less_than(2.0),
            f"Average response time too slow: {avg_response_time:.2f}s",
        )
        assert_that(
            max_response_time,
            less_than(3.0),
            f"Max response time too slow: {max_response_time:.2f}s",
        )

        total_time = time.time() - start_time
        print(f"✅ Performance test completed in {total_time:.2f}s")
        print(f"Average response time: {avg_response_time:.2f}s")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Network error during performance test: {e}")
