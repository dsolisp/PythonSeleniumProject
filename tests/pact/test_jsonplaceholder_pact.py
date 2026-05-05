"""Pact consumer contract against JSONPlaceholder (mock provider)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import requests
from pact import Pact, match

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def pact() -> Generator[Pact, None, None]:
    out = Path(__file__).resolve().parent.parent.parent / "pacts"
    out.mkdir(parents=True, exist_ok=True)
    pact = Pact("PythonSeleniumProject", "JSONPlaceholder").with_specification("V4")
    yield pact
    pact.write_file(out)


@pytest.mark.pact
def test_get_post_1(pact: Pact) -> None:
    response = {
        "userId": match.int(1),
        "id": match.int(1),
        "title": match.str("hello"),
        "body": match.str("world"),
    }
    (
        pact.upon_receiving("a request for post 1")
        .given("a post with id 1 exists")
        .with_request("GET", "/posts/1")
        .will_respond_with(200)
        .with_header("Content-Type", "application/json; charset=utf-8")
        .with_body(response, content_type="application/json")
    )

    with pact.serve() as srv:
        res = requests.get(f"{srv.url}/posts/1", timeout=10)
        res.raise_for_status()
        body = res.json()
        assert body["id"] == 1
