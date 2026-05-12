"""
Pytest configuration and fixtures for test automation.
"""

import contextlib
import json
import os
import time
from collections.abc import Generator
from pathlib import Path

import allure
import pytest
from selenium import webdriver

from config.settings import settings
from utils.otel import configure_tracing, current_trace_id, get_tracer
from utils.webdriver_factory import cleanup_driver_and_database, get_driver

# ── Auth state cache (ADR-009) ────────────────────────────────────────────────
_AUTH_FILE = Path(".auth/sauce.json")
_SAUCE_URL = "https://www.saucedemo.com/"
_SAUCE_USERNAME = "standard_user"
_SAUCE_PASSWORD = "secret_sauce"


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--selenium-browser",
        action="store",
        default="chrome",
        help="Browser to use for Selenium tests",
    )
    parser.addoption("--headless", action="store_true", help="Run in headless mode")
    parser.addoption(
        "--no-cache-auth",
        action="store_true",
        default=False,
        help="Skip auth state cache and perform a fresh login every session",
    )


@pytest.fixture(scope="session")
def test_config(request):
    """Test configuration from command line and environment."""
    headless_cli = request.config.getoption("--headless")
    headless_env = os.getenv("HEADLESS", "false").lower() == "true"
    return {
        "browser": request.config.getoption("--selenium-browser"),
        "headless": headless_cli or headless_env,
        "no_cache_auth": request.config.getoption("--no-cache-auth"),
    }


# ── Clean Selenium driver fixture (replaces the old tuple pattern) ────────────


@pytest.fixture
def selenium_driver(
    request,
    test_config,
) -> Generator[webdriver.Chrome]:
    """Function-scoped Selenium WebDriver — returns the driver directly (no tuple)."""
    test_name = request.node.name
    start_time = time.time()

    drv, db = get_driver(
        browser=test_config["browser"],
        headless=test_config["headless"],
    )

    try:
        yield drv
    finally:
        duration = time.time() - start_time
        print(f"\nTest '{test_name}' completed in {duration:.2f}s")

        if (
            hasattr(request.node, "rep_call")
            and request.node.rep_call.failed
            and settings.SCREENSHOT_ON_FAILURE
        ):
            with contextlib.suppress(OSError):
                screenshot_path = settings.SCREENSHOTS_DIR / f"{test_name}_failure.png"
                drv.save_screenshot(str(screenshot_path))
                print(f"Failure screenshot: {screenshot_path}")

        cleanup_driver_and_database(drv, db)


# ── Session-scoped authenticated driver (ADR-009 — auth state reuse) ─────────


@pytest.fixture(scope="session")
def authenticated_driver(test_config) -> Generator[webdriver.Chrome]:
    """Session-scoped driver pre-authenticated as standard_user.

    On first use it logs in and writes cookies to `.auth/sauce.json`.
    Subsequent tests in the same session reuse the cached state so
    the login page is only hit once per session (--no-cache-auth bypasses this).
    """
    drv, db = get_driver(
        browser=test_config["browser"],
        headless=test_config["headless"],
    )

    _auth_file = _AUTH_FILE
    use_cache = not test_config["no_cache_auth"]

    if use_cache and _auth_file.exists():
        # Restore cookies from cache — navigate first so domain matches
        drv.get(_SAUCE_URL)
        state = json.loads(_auth_file.read_text())
        for cookie in state.get("cookies", []):
            with contextlib.suppress(Exception):
                drv.add_cookie(cookie)
        drv.get(_SAUCE_URL)
    else:
        # Fresh login
        drv.get(_SAUCE_URL)
        from pages.sauce.login_page import LoginPage  # noqa: PLC0415

        login = LoginPage(drv)
        login.login(_SAUCE_USERNAME, _SAUCE_PASSWORD)

        # Ensure we're authenticated before continuing (inventory should be visible).
        drv.get(f"{_SAUCE_URL}inventory.html")
        from selenium.webdriver.support import (  # noqa: PLC0415
            expected_conditions as EC,
        )
        from selenium.webdriver.support.ui import WebDriverWait  # noqa: PLC0415

        from locators.sauce.inventory_locators import (  # noqa: PLC0415
            InventoryLocators,
        )

        WebDriverWait(drv, 10).until(
            EC.visibility_of_element_located(InventoryLocators.INVENTORY_LIST)
        )

        # Persist auth state
        if use_cache:
            _auth_file.parent.mkdir(parents=True, exist_ok=True)
            state = {"cookies": drv.get_cookies()}
            _auth_file.write_text(json.dumps(state, indent=2))

    try:
        yield drv
    finally:
        cleanup_driver_and_database(drv, db)


# ── Legacy driver fixture (backward-compat — returns (driver, db) tuple) ──────


@pytest.fixture
def driver(
    request,
    test_config,
) -> Generator[tuple[webdriver.Chrome, object]]:
    """Legacy fixture returning (WebDriver, db) tuple. Prefer selenium_driver."""
    test_name = request.node.name
    start_time = time.time()

    drv, db = get_driver(
        browser=test_config["browser"],
        headless=test_config["headless"],
    )

    try:
        yield drv, db
    finally:
        duration = time.time() - start_time
        print(f"\nTest '{test_name}' completed in {duration:.2f}s")

        if (
            hasattr(request.node, "rep_call")
            and request.node.rep_call.failed
            and settings.SCREENSHOT_ON_FAILURE
        ):
            with contextlib.suppress(OSError):
                screenshot_path = settings.SCREENSHOTS_DIR / f"{test_name}_failure.png"
                drv.save_screenshot(str(screenshot_path))

        cleanup_driver_and_database(drv, db)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    """Capture test results for failure screenshots."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# ── Markers ───────────────────────────────────────────────────────────────────


def pytest_configure(config):
    """Register test markers."""
    configure_tracing(service_name="PythonSeleniumProject")
    markers = [
        "ui: UI automation tests (tests/ui/)",
        "web: Legacy alias for ui tests",
        "api: API tests (tests/backend/test_api.py)",
        "database: Database tests (tests/backend/test_database.py)",
        "framework: Framework functionality tests",
        "visual: Visual regression tests (tests/ui/visual/)",
        "playwright: Playwright-based tests",
        "sauce: SauceDemo E2E tests (tests/ui/sauce/)",
        "practice: QA Practice App tests (tests/ui/practice/)",
        "smoke: Smoke / fast-feedback tests",
        "selectors: Selector strategy showcase tests",
        "accessibility: Accessibility tests (tests/accessibility/)",
        "performance: Performance / benchmarking tests (tests/performance/)",
        "integration: Integration tests (tests/integration/)",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    tracer = get_tracer("pytest")
    test_name = item.nodeid
    with tracer.start_as_current_span(
        "test",
        attributes={
            "test.name": item.name,
            "test.nodeid": test_name,
            "test.file": str(getattr(item, "path", "")),
        },
    ):
        yield

    trace_id = current_trace_id()
    if not trace_id:
        return

    # Best-effort: if allure is installed and enabled, attach the trace id for drill-down.
    if getattr(settings, "ENABLE_ALLURE", False):
        try:
            jaeger_ui = os.getenv("JAEGER_UI_URL")  # e.g. http://localhost:16686
            if jaeger_ui:
                allure.dynamic.link(
                    f"{jaeger_ui.rstrip('/')}/trace/{trace_id}", name="Jaeger trace"
                )
            allure.attach(
                trace_id,
                name="otel.trace_id",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:
            # Allure is optional in this repo; ignore if not installed/configured.
            pass


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
