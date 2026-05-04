"""
SWAPI — Comprehensive API Tests
Equivalent to Cypress api.cy.ts.
Covers: positive, negative, schema validation, SLA, and pagination.
"""

import math
import time

import pytest
import requests  # type: ignore
import urllib3
from hamcrest import assert_that, equal_to, greater_than, has_key, is_not

from config.constants import URLS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = URLS.SWAPI


@pytest.mark.api
class TestSwapiAPI:
    def setup_method(self):
        self.session = requests.Session()
        self.session.verify = False

    def teardown_method(self):
        self.session.close()

    # ── Positive Tests ──────────────────────────────────────────────────
    def test_example_1_fetches_specific_person(self):
        """Example 1: Fetches a specific person (Luke Skywalker)"""
        res = self.session.get(f"{BASE_URL}/people/1")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body, has_key("name"))
        assert_that(body["name"], equal_to("Luke Skywalker"))
        assert_that(body["height"], equal_to("172"))

    def test_example_2_fetches_paginated_collection(self):
        """Example 2: Fetches a paginated collection of people"""
        res = self.session.get(f"{BASE_URL}/people")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body["count"], greater_than(0))
        assert_that(body["next"], is_not(None))
        assert_that(body["previous"], equal_to(None))
        assert_that(body["results"][0], has_key("name"))
        assert_that(body["results"][0], has_key("gender"))

    def test_example_3_fetches_person_search_query(self):
        """Example 3: Fetches a person using search query"""
        res = self.session.get(f"{BASE_URL}/people", params={"search": "Darth Vader"})
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body["count"], equal_to(1))
        assert_that(body["results"][0]["name"], equal_to("Darth Vader"))

    # ── Schema Validation ───────────────────────────────────────────────
    def test_example_4_validates_starship_schema(self):
        """Example 4: Validates starship resource schema"""
        res = self.session.get(f"{BASE_URL}/starships/9")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        expected_keys = [
            "name",
            "model",
            "manufacturer",
            "cost_in_credits",
            "length",
            "max_atmosphering_speed",
            "crew",
            "passengers",
            "cargo_capacity",
            "consumables",
            "hyperdrive_rating",
            "MGLT",
            "starship_class",
            "pilots",
            "films",
            "created",
            "edited",
            "url",
        ]
        for key in expected_keys:
            assert_that(body, has_key(key))

    # ── SLA / Performance ───────────────────────────────────────────────
    def test_example_5_verifies_response_time(self):
        """Example 5: Verifies response time is under 3000ms (external API)"""
        start = time.time()
        self.session.get(f"{BASE_URL}/planets/1")
        duration_ms = (time.time() - start) * 1000
        assert duration_ms < 3000, f"Expected < 3000ms, took {duration_ms}ms"

    # ── Negative Tests ──────────────────────────────────────────────────
    def test_example_6_verifies_404_non_existent_id(self):
        """Example 6: Verifies 404 for non-existent resource ID"""
        res = self.session.get(f"{BASE_URL}/people/99999")
        assert_that(res.status_code, equal_to(404))
        body = res.json()
        assert_that(body["detail"], equal_to("Not found"))

    def test_example_7_verifies_404_invalid_endpoint(self):
        """Example 7: Verifies 404 for invalid endpoint"""
        res = self.session.get(f"{BASE_URL}/invalid_endpoint")
        assert_that(res.status_code, equal_to(404))

    def test_example_8_handles_search_no_matches(self):
        """Example 8: Handles search with no matches"""
        res = self.session.get(f"{BASE_URL}/people", params={"search": "xyz_no_match"})
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body["count"], equal_to(0))
        assert_that(len(body["results"]), equal_to(0))

    # ── Pagination Boundary ─────────────────────────────────────────────
    def test_example_9_verifies_first_page_no_previous(self):
        """Example 9: Verifies first page has no previous link"""
        res = self.session.get(f"{BASE_URL}/people", params={"page": 1})
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body["previous"], equal_to(None))
        assert_that(body["next"], is_not(None))

    def test_example_10_verifies_last_page_no_next(self):
        """Example 10: Verifies last page has no next link"""
        res = self.session.get(f"{BASE_URL}/people")
        body = res.json()
        total_pages = math.ceil(body["count"] / len(body["results"]))

        last_page = self.session.get(f"{BASE_URL}/people", params={"page": total_pages})
        assert_that(last_page.status_code, equal_to(200))
        last_body = last_page.json()
        assert_that(last_body["next"], equal_to(None))
