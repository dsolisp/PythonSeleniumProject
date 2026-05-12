"""Minimal Playwright check using the shared factory (no pytest-playwright plugin)."""

import pytest
from hamcrest import assert_that, equal_to

from config.constants import URLS
from utils.playwright_factory import create_playwright_session


@pytest.mark.ui
@pytest.mark.playwright
def test_playwright_opens_sauce_demo() -> None:
    """Navigate to SauceDemo and assert title — validates browsers + factory wiring."""
    factory = None
    try:
        factory, page = create_playwright_session()
        page.navigate_to(URLS.SAUCE_DEMO)
        assert_that(page.get_title(), equal_to("Swag Labs"))
    finally:
        if factory is not None:
            factory.safe_cleanup()
