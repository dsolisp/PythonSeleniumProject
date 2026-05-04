"""
API Contract Testing Module.
Equivalent to Cypress contract.cy.ts.
Validates API schemas and contract stability for SWAPI.
"""

import pytest
import requests  # type: ignore[import-untyped]
import urllib3
from hamcrest import assert_that, equal_to, has_key, instance_of

from config.constants import URLS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = URLS.SWAPI


@pytest.mark.api
@pytest.mark.contract
class TestAPIContracts:
    def setup_method(self):
        self.session = requests.Session()
        self.session.verify = False

    def teardown_method(self):
        self.session.close()

    def test_schema_for_people_endpoint(self):
        """should match expected schema for /people endpoint"""
        res = self.session.get(f"{BASE_URL}/people/1/")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        keys = [
            "name",
            "height",
            "mass",
            "hair_color",
            "skin_color",
            "eye_color",
            "birth_year",
            "gender",
            "homeworld",
            "films",
            "species",
            "vehicles",
            "starships",
            "created",
            "edited",
            "url",
        ]
        for k in keys:
            assert_that(body, has_key(k))

    def test_validate_films_endpoint_contract(self):
        """should validate films endpoint contract"""
        res = self.session.get(f"{BASE_URL}/films/1/")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        keys = [
            "title",
            "episode_id",
            "opening_crawl",
            "director",
            "producer",
            "release_date",
            "created",
            "edited",
            "url",
        ]
        for k in keys:
            assert_that(body, has_key(k))
        assert_that(body["characters"], instance_of(list))
        assert_that(body["planets"], instance_of(list))
        assert_that(body["starships"], instance_of(list))
        assert_that(body["vehicles"], instance_of(list))
        assert_that(body["species"], instance_of(list))

    def test_validate_planets_endpoint_contract(self):
        """should validate planets endpoint contract"""
        res = self.session.get(f"{BASE_URL}/planets/1/")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        keys = [
            "name",
            "rotation_period",
            "orbital_period",
            "diameter",
            "climate",
            "gravity",
            "terrain",
            "surface_water",
            "population",
        ]
        for k in keys:
            assert_that(body, has_key(k))
        assert_that(body["residents"], instance_of(list))
        assert_that(body["films"], instance_of(list))

    def test_ensure_contract_stability_no_unexpected_fields_removed(self):
        """should ensure contract stability — no unexpected fields removed"""
        res = self.session.get(f"{BASE_URL}/people/1/")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        required_fields = [
            "name",
            "height",
            "mass",
            "hair_color",
            "skin_color",
            "eye_color",
            "birth_year",
            "gender",
        ]
        for field in required_fields:
            assert_that(body, has_key(field))

    def test_validate_array_response_structure_for_list_endpoints(self):
        """should validate array response structure for list endpoints"""
        res = self.session.get(f"{BASE_URL}/people/")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body, has_key("count"))
        assert_that(body["count"], instance_of(int))
        assert_that(body, has_key("next"))
        assert_that(body, has_key("previous"))
        assert_that(body["results"], instance_of(list))
        assert_that(body["results"][0], has_key("name"))
        assert_that(body["results"][0], has_key("height"))
