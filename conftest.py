"""
Pytest configuration and fixtures for test automation.
"""

import contextlib
import os
import time
from collections.abc import Generator
from typing import Any

import pytest
from selenium import webdriver

from config.settings import settings
from utils.webdriver_factory import cleanup_driver_and_database, get_driver


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--selenium-browser",
        action="store",
        default="chrome",
        help="Browser to use for Selenium tests",
    )
    parser.addoption("--headless", action="store_true", help="Run in headless mode")


@pytest.fixture(scope="session")
def test_config(request) -> dict[str, Any]:
    """Test configuration from command line and environment."""
    # Check both command line flag and environment variable for headless mode
    headless_cli = request.config.getoption("--headless")
    headless_env = os.getenv("HEADLESS", "false").lower() == "true"

    return {
        "browser": request.config.getoption("--selenium-browser"),
        "headless": headless_cli or headless_env,  # Use headless if either is True
    }


@pytest.fixture
def driver(
    request,
    test_config,
) -> Generator[
    tuple[webdriver.Chrome, object],
    None,
    None,
]:
    """
    Main driver fixture providing WebDriver and database connection.
    """
    test_name = request.node.name
    start_time = time.time()

    # Setup phase
    driver, db = get_driver(
        browser=test_config["browser"],
        headless=test_config["headless"],
    )

    try:
        yield driver, db
    finally:
        # Cleanup phase
        duration = time.time() - start_time
        print(f"Test {test_name} completed in {duration:.2f}s")

        # Screenshot on failure
        if (
            hasattr(request.node, "rep_call")
            and request.node.rep_call.failed
            and settings.SCREENSHOT_ON_FAILURE
        ):
            try:
                screenshot_path = settings.SCREENSHOTS_DIR / f"{test_name}_failure.png"
                driver.save_screenshot(str(screenshot_path))
                print(f"Failure screenshot: {screenshot_path}")
            except OSError as e:
                print(f"Screenshot failed: {e}")

        # Centralized cleanup
        cleanup_driver_and_database(driver, db)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """Capture test results for failure screenshots."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# Test markers
def pytest_configure(config):
    """Configure test markers."""
    markers = [
        "ui: UI automation tests",
        "api: API tests",
        "database: Database tests",
        "framework: Framework functionality tests",
        "visual: Visual regression tests",
        "playwright: Playwright-based tests",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


# === PLAYWRIGHT CONFIGURATION ===

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure Playwright browser context for visual testing."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "device_scale_factor": 1,
        "ignore_https_errors": True,
        "record_video_dir": (
            str(settings.SCREENSHOTS_DIR / "videos")
            if hasattr(settings, "RECORD_VIDEOS") and settings.RECORD_VIDEOS
            else None
        ),
    }


@pytest.fixture
def page_with_visual_setup(page):
    """
    Enhanced page fixture with visual testing setup.
    Sets up the page for visual regression testing.
    """
    # Set default timeout for visual operations
    page.set_default_timeout(30000)  # 30 seconds

    # Ensure consistent viewport for visual testing
    page.set_viewport_size({"width": 1280, "height": 720})

    yield page

    # Cleanup after test
    with contextlib.suppress(Exception):
        # Close any modal dialogs that might be open
        page.evaluate("() => { try { window.close(); } catch(e) {} }")
