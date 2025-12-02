"""
API Contract Testing Module.
Validates API responses against JSON schemas for contract compliance.
"""

import pytest
import requests
from jsonschema import Draft7Validator, ValidationError, validate

from config.settings import settings

# JSON Schemas for API contracts
POST_SCHEMA = {
    "type": "object",
    "required": ["id", "title", "body", "userId"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "body": {"type": "string"},
        "userId": {"type": "integer", "minimum": 1},
    },
    "additionalProperties": False,
}

USER_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "username", "email"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "name": {"type": "string", "minLength": 1},
        "username": {"type": "string", "minLength": 1},
        "email": {"type": "string", "format": "email"},
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "suite": {"type": "string"},
                "city": {"type": "string"},
                "zipcode": {"type": "string"},
                "geo": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "string"},
                        "lng": {"type": "string"},
                    },
                },
            },
        },
        "phone": {"type": "string"},
        "website": {"type": "string"},
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "catchPhrase": {"type": "string"},
                "bs": {"type": "string"},
            },
        },
    },
}

COMMENT_SCHEMA = {
    "type": "object",
    "required": ["id", "postId", "name", "email", "body"],
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "postId": {"type": "integer", "minimum": 1},
        "name": {"type": "string"},
        "email": {"type": "string"},
        "body": {"type": "string"},
    },
}

POSTS_LIST_SCHEMA = {"type": "array", "items": POST_SCHEMA}


@pytest.mark.api
@pytest.mark.contract
class TestAPIContracts:
    """API Contract validation tests using JSON Schema."""

    def setup_method(self):
        """Setup test session."""
        self.base_url = settings.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def teardown_method(self):
        """Cleanup session."""
        if hasattr(self, "session"):
            self.session.close()

    def test_posts_response_matches_schema(self):
        """Verify GET /posts response matches the posts list schema."""
        response = self.session.get(f"{self.base_url}/posts")
        assert response.status_code == 200

        posts = response.json()
        validate(instance=posts, schema=POSTS_LIST_SCHEMA)
        print(f"✅ Posts list ({len(posts)} items) matches schema")

    def test_single_post_matches_schema(self):
        """Verify GET /posts/1 response matches the post schema."""
        response = self.session.get(f"{self.base_url}/posts/1")
        assert response.status_code == 200

        post = response.json()
        validate(instance=post, schema=POST_SCHEMA)
        print(f"✅ Single post matches schema: {post['title'][:30]}...")

    def test_user_response_matches_schema(self):
        """Verify GET /users/1 response matches the user schema."""
        response = self.session.get(f"{self.base_url}/users/1")
        assert response.status_code == 200

        user = response.json()
        validate(instance=user, schema=USER_SCHEMA)
        print(f"✅ User matches schema: {user['name']}")

    def test_comment_response_matches_schema(self):
        """Verify GET /comments/1 response matches the comment schema."""
        response = self.session.get(f"{self.base_url}/comments/1")
        assert response.status_code == 200

        comment = response.json()
        validate(instance=comment, schema=COMMENT_SCHEMA)
        print(f"✅ Comment matches schema: {comment['name'][:30]}...")

    def test_created_post_matches_schema(self):
        """Verify POST /posts response matches schema with required fields."""
        new_post = {
            "title": "Contract Test Post",
            "body": "Testing API contract validation",
            "userId": 1,
        }
        response = self.session.post(f"{self.base_url}/posts", json=new_post)
        assert response.status_code == 201

        created = response.json()
        validate(instance=created, schema=POST_SCHEMA)
        print(f"✅ Created post matches schema with ID: {created['id']}")

    def test_schema_validation_catches_invalid_response(self):
        """Verify schema validation correctly rejects invalid data."""
        invalid_post = {
            "id": "not-an-integer",  # Should be integer
            "title": "",  # Should have minLength 1
            "userId": -1,  # Should be minimum 1
        }

        with pytest.raises(ValidationError):
            validate(instance=invalid_post, schema=POST_SCHEMA)
        print("✅ Schema validation correctly rejects invalid data")

    def test_all_posts_conform_to_schema(self):
        """Verify all posts in the collection conform to schema."""
        response = self.session.get(f"{self.base_url}/posts")
        posts = response.json()

        validator = Draft7Validator(POST_SCHEMA)
        errors = []

        for i, post in enumerate(posts[:10]):  # Check first 10
            post_errors = list(validator.iter_errors(post))
            if post_errors:
                errors.append(f"Post {i}: {[e.message for e in post_errors]}")

        assert not errors, f"Schema violations found: {errors}"
        print(f"✅ All {min(10, len(posts))} posts conform to schema")

    def test_nested_address_schema_in_user(self):
        """Verify nested address object in user response."""
        response = self.session.get(f"{self.base_url}/users/1")
        user = response.json()

        assert "address" in user, "User should have address"
        assert "street" in user["address"], "Address should have street"
        assert "geo" in user["address"], "Address should have geo"
        assert "lat" in user["address"]["geo"], "Geo should have lat"
        print(f"✅ Nested address structure valid for user: {user['name']}")
