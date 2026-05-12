"""
Minimal Locust scenario for local load experiments.

Run from the project root (same layout as docs/README):

    locust -f tests/performance/locustfile.py

Uses JSONPlaceholder — keep user count low when pointing at shared public APIs.
"""

from locust import HttpUser, between, task

from config.constants import URLS


class JsonPlaceholderUser(HttpUser):
    """Lightweight read-heavy traffic against JSONPlaceholder."""

    host = URLS.JSON_PLACEHOLDER
    wait_time = between(0.5, 2.0)

    @task(3)
    def list_posts(self) -> None:
        self.client.get("/posts", name="/posts")

    @task(2)
    def get_post(self) -> None:
        self.client.get("/posts/1", name="/posts/[id]")

    @task(1)
    def list_users(self) -> None:
        self.client.get("/users", name="/users")
