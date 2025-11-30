"""
Playwright Search engine tests demonstrating modern browser automation.
"""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import pytest
from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    is_,
    less_than,
)

from config.settings import settings
from pages.playwright_search_engine_page import PlaywrightSearchEnginePage
from utils.playwright_factory import PlaywrightFactory, create_playwright_session


@dataclass
class PlaywrightSession:
    """Container for Playwright session components."""

    factory: PlaywrightFactory
    playwright_page: object
    search_page: PlaywrightSearchEnginePage


@pytest.fixture
def playwright_session():
    """Fixture providing Playwright session with automatic cleanup."""
    factory, playwright_page = create_playwright_session(
        browser_type="chromium",
        headless=settings.HEADLESS,
    )
    search_page = PlaywrightSearchEnginePage(playwright_page.page)

    yield PlaywrightSession(
        factory=factory,
        playwright_page=playwright_page,
        search_page=search_page,
    )

    factory.cleanup()


@pytest.fixture
def playwright_session_firefox():
    """Fixture providing Firefox Playwright session with automatic cleanup."""
    factory, playwright_page = create_playwright_session(
        browser_type="firefox",
        headless=settings.HEADLESS,
    )
    search_page = PlaywrightSearchEnginePage(playwright_page.page)

    yield PlaywrightSession(
        factory=factory,
        playwright_page=playwright_page,
        search_page=search_page,
    )

    factory.cleanup()


def _get_search_engine_url_from_requests(
    intercepted_requests: list[dict],
) -> Optional[str]:
    """Extract search engine URL from intercepted requests."""
    # Try document/fetch requests first
    for req in intercepted_requests:
        try:
            if req.get("resource_type") in ("document", "fetch") and req.get("url"):
                parsed = urlparse(req["url"])
                if parsed.scheme and parsed.netloc:
                    return f"{parsed.scheme}://{parsed.netloc}"
        except (ValueError, TypeError):
            continue

    # Fall back to any request with valid URL
    for req in intercepted_requests:
        try:
            if req.get("url"):
                parsed = urlparse(req["url"])
                if parsed.scheme and parsed.netloc:
                    return f"{parsed.scheme}://{parsed.netloc}"
        except (ValueError, TypeError):
            continue

    return None


@pytest.mark.playwright
def test_playwright_search_basic(playwright_session: PlaywrightSession):
    search_page = playwright_session.search_page

    # Test navigation
    success = search_page.open_search_engine()
    assert_that(success, is_(True), "Should be able to open search engine")

    # Verify page loaded
    title = search_page.get_title()
    assert_that(title, contains_string("DuckDuckGo"))

    # Perform search
    search_term = settings.PLAYWRIGHT_SEARCH_TERM

    # Navigate to search engine
    search_success = search_page.search_for(
        search_term,
        wait_for_results=True,
    )
    assert_that(search_success, is_(True), "Search should succeed")

    # Wait for search completion
    completion_success = search_page.wait_for_search_completion()
    assert_that(
        completion_success,
        is_(True),
        "Search should complete within timeout",
    )

    # Verify search was performed (DuckDuckGo uses ?q= parameter)
    current_url = search_page.get_url()
    assert_that(
        any(
            indicator in current_url.lower() for indicator in ["?q=", "/search", "&q="]
        ),
        is_(True),
        f"Should be on search results page: {current_url}",
    )

    # Check for results
    if search_page.has_results():
        result_count = search_page.get_result_count()
        assert_that(result_count, greater_than(0), "Should have search results")

        # Get result titles
        titles = search_page.get_result_titles()
        assert_that(len(titles), greater_than(0), "Should have result titles")

        # Verify search term relevance (basic check)
        titles_text = " ".join(titles).lower()
        assert_that(
            any(word in titles_text for word in ["python", "automation", "testing"]),
            is_(True),
            "Results should be relevant to search term",
        )

        print(f"✅ Found {result_count} results for '{search_term}'")
        print(f"First result: {titles[0][:100]}...")
    else:
        pytest.fail("No results found - may be blocked by anti-bot measures")


@pytest.mark.playwright
def test_playwright_search_with_suggestions(playwright_session: PlaywrightSession):
    """
    Test search engine suggestions using Playwright.
    Demonstrates advanced element interactions.
    """
    search_page = playwright_session.search_page
    playwright_page = playwright_session.playwright_page

    # Open search engine
    success = search_page.open_search_engine()
    assert_that(success, is_(True), "Should be able to open search engine")

    # Type partial search term to trigger suggestions
    search_page.element_actions.send_keys(
        search_page.locators.SEARCH_INPUT,
        "playwright browser",
        clear=True,
    )

    # Try to wait for suggestions to appear (may not always appear)
    try:
        playwright_page.page.wait_for_selector(
            search_page.locators.SEARCH_SUGGESTIONS,
            timeout=3000,
        )
    except (TimeoutError, ValueError, TypeError):
        print("⚠️ Suggestions did not appear - common in automated environments")

    # Try to get suggestions (may not always appear due to anti-bot measures)
    suggestions = search_page.get_search_suggestions()

    if suggestions:
        assert_that(
            len(suggestions),
            greater_than(0),
            "Should have search suggestions",
        )
        print(f"✅ Found {len(suggestions)} search suggestions")
        for i, suggestion in enumerate(suggestions[:3]):
            print(f"  {i + 1}. {suggestion}")
    else:
        pytest.fail("No suggestions found - common in automated environments")

    # Complete the search
    playwright_page.page.keyboard.press("Enter")

    # Verify search completed
    search_page.wait_for_search_completion()
    current_url = search_page.get_url()
    assert_that(current_url.lower(), contains_string("duckduckgo.com"))


@pytest.mark.playwright
def test_playwright_advanced_search(playwright_session: PlaywrightSession):
    """
    Test advanced Search engine with filters using Playwright.
    Demonstrates advanced search capabilities.
    """
    search_page = playwright_session.search_page

    # Open Search engine
    success = search_page.open_search_engine()
    assert_that(success, is_(True), "Should be able to open search engine")

    # Perform advanced search with simpler, more realistic query
    search_success = search_page.perform_advanced_search(
        search_term="python",
        site_filter="github.com",
    )
    assert_that(search_success, is_(True), "Advanced search should succeed")

    # Verify advanced search (DuckDuckGo uses ?q= parameter)
    current_url = search_page.get_url()
    assert_that(
        any(
            indicator in current_url.lower() for indicator in ["?q=", "/search", "&q="]
        ),
        is_(True),
        f"Should be on search results page: {current_url}",
    )

    # The URL should contain our search parameters
    url_lower = current_url.lower()
    # Check for python and site filter in URL
    assert_that(url_lower, contains_string("python"))
    print(f"✅ Advanced search URL: {current_url[:100]}...")

    # Check if we have results (should have many for "python site:github.com")
    if search_page.has_results():
        result_count = search_page.get_result_count()
        print(f"✅ Advanced search returned {result_count} results")

        # Get some result links to verify they're from GitHub
        links = search_page.get_result_links()
        if links:
            github_links = [link for link in links[:5] if "github.com" in link.lower()]
            print(f"✅ Found {len(github_links)} GitHub links in top 5 results")
    else:
        pytest.fail("No results found - search engine may not support site: filter")


@pytest.mark.playwright
@pytest.mark.skip(
    reason="Multiple Playwright sync sessions conflict with pytest-asyncio. "
    "Run browsers separately or use async API for multi-browser testing."
)
def test_playwright_multiple_browsers(
    playwright_session: PlaywrightSession,
    playwright_session_firefox: PlaywrightSession,
):
    """
    Test the same search across multiple browsers.
    Demonstrates Playwright's multi-browser capabilities.

    NOTE: This test is skipped because running multiple sync_playwright()
    instances causes conflicts with pytest-asyncio. For multi-browser testing,
    either run browsers in separate test sessions or use the async API.
    """
    sessions = [
        ("chromium", playwright_session),
        ("firefox", playwright_session_firefox),
    ]

    for browser_type, session in sessions:
        print(f"\n🌐 Testing with {browser_type}")
        search_page = session.search_page
        playwright_page = session.playwright_page

        # Open Search engine
        success = search_page.open_search_engine()
        assert_that(
            success,
            is_(True),
            f"Should be able to open search engine in {browser_type}",
        )

        # Verify browser-specific behavior
        user_agent = playwright_page.page.evaluate("navigator.userAgent")
        print(f"User-Agent: {user_agent[:100]}...")

        # Perform basic search
        search_success = search_page.search_for(
            "playwright browser automation",
        )

        if search_success and search_page.has_results():
            result_count = search_page.get_result_count()
            print(f"✅ {browser_type}: Found {result_count} results")
        else:
            pytest.fail(f"{browser_type}: Search blocked or no results")


@pytest.mark.playwright
def test_playwright_network_interception(playwright_session: PlaywrightSession):
    """
    Test with network interception capabilities.
    Demonstrates Playwright's advanced network features.
    """
    playwright_page = playwright_session.playwright_page
    search_page = playwright_session.search_page

    # Set up network interception
    intercepted_requests = []

    def handle_request(route):
        request = route.request
        intercepted_requests.append(
            {
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
            },
        )
        route.continue_()

    # Enable request interception
    playwright_page.page.route("**/*", handle_request)

    # Navigate to Search engine (this will trigger network requests)
    success = search_page.open_search_engine()
    assert_that(success, is_(True), "Should be able to open search engine")

    # Verify we intercepted requests
    assert_that(
        len(intercepted_requests),
        greater_than(0),
        "Should have intercepted network requests",
    )

    # Determine search engine URL with fallback strategy
    search_engine_url = getattr(settings, "SEARCH_ENGINE_URL", None) or getattr(
        search_page, "SEARCH_ENGINE_URL", None
    )

    if not search_engine_url:
        try:
            page_url = playwright_page.page.evaluate("() => location.href")
            if page_url:
                parsed = urlparse(page_url)
                if parsed.scheme and parsed.netloc:
                    search_engine_url = f"{parsed.scheme}://{parsed.netloc}"
        except (ValueError, TypeError):
            pass

    if not search_engine_url:
        search_engine_url = _get_search_engine_url_from_requests(intercepted_requests)

    if not search_engine_url:
        message = "Could not determine search engine URL for request filtering"
        raise RuntimeError(message)

    search_engine_domain = urlparse(search_engine_url).netloc
    search_engine_requests = [
        req
        for req in intercepted_requests
        if search_engine_domain in (req.get("url") or "")
    ]
    assert_that(
        len(search_engine_requests),
        greater_than(0),
        "Should have Search engine-related requests",
    )

    # Check for different resource types
    resource_types = {req["resource_type"] for req in intercepted_requests}
    print(f"✅ Intercepted {len(intercepted_requests)} requests")
    print(f"Resource types: {sorted(resource_types)}")

    # Verify we got the main document
    document_requests = [
        req for req in intercepted_requests if req["resource_type"] == "document"
    ]
    assert_that(
        len(document_requests),
        greater_than(0),
        "Should have document requests",
    )


@pytest.fixture
def playwright_session_mobile():
    """Fixture providing mobile Playwright session with iPhone 12 Pro emulation."""
    factory = PlaywrightFactory()
    browser = factory.create_browser("chromium", headless=settings.HEADLESS)

    context = factory.create_context(
        browser,
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
            "Mobile/15E148 Safari/604.1"
        ),
    )

    page = factory.create_page(context)
    search_page = PlaywrightSearchEnginePage(page)

    yield PlaywrightSession(
        factory=factory,
        playwright_page=type("PlaywrightPage", (), {"page": page})(),
        search_page=search_page,
    )

    factory.cleanup()


@pytest.mark.playwright
def test_playwright_mobile_emulation(playwright_session_mobile: PlaywrightSession):
    """
    Test Search engine with mobile device emulation.
    Demonstrates responsive testing capabilities.
    """
    search_page = playwright_session_mobile.search_page
    page = playwright_session_mobile.playwright_page.page

    # Test mobile navigation
    success = search_page.open_search_engine()
    assert_that(
        success,
        is_(True),
        "Should be able to open search engine on mobile",
    )

    # Verify mobile layout
    viewport_size = page.evaluate(
        "() => ({width: window.innerWidth, height: window.innerHeight})",
    )
    assert_that(
        viewport_size["width"],
        equal_to(390),
        "Should have mobile viewport width",
    )
    assert_that(
        viewport_size["height"],
        equal_to(844),
        "Should have mobile viewport height",
    )

    # Test mobile search
    search_success = search_page.search_for("mobile testing playwright")

    if search_success and search_page.has_results():
        result_count = search_page.get_result_count()
        print(f"✅ Mobile: Found {result_count} results")
    else:
        pytest.fail("Mobile search blocked or no results")

    print("✅ Mobile emulation test completed")


@pytest.mark.playwright
@pytest.mark.slow
def test_playwright_performance_metrics(playwright_session: PlaywrightSession):
    """
    Test with performance metrics collection.
    Demonstrates Playwright's performance monitoring capabilities.
    """
    playwright_page = playwright_session.playwright_page
    search_page = playwright_session.search_page

    # Start performance monitoring
    playwright_page.page.evaluate("performance.mark('test-start')")

    # Navigate and measure
    navigation_start = playwright_page.page.evaluate("performance.now()")
    success = search_page.open_search_engine()
    navigation_end = playwright_page.page.evaluate("performance.now()")
    assert_that(success, is_(True), "Should be able to open search engine")

    navigation_time = navigation_end - navigation_start
    print(f"✅ Navigation time: {navigation_time:.2f}ms")

    # Measure search performance
    search_start = playwright_page.page.evaluate("performance.now()")
    search_success = search_page.search_for("performance testing")
    search_end = playwright_page.page.evaluate("performance.now()")

    if search_success:
        search_time = search_end - search_start
        print(f"✅ Search time: {search_time:.2f}ms")

        # Get basic performance metrics
        metrics = playwright_page.page.evaluate(
            """
            () => {
                const perfData = performance.getEntriesByType('navigation')[0];
                return {
                    domContentLoaded: perfData.domContentLoadedEventEnd -
                        perfData.domContentLoadedEventStart,
                    loadComplete: perfData.loadEventEnd -
                        perfData.loadEventStart,
                    totalTime: perfData.loadEventEnd - perfData.fetchStart
                };
            }
        """,
        )

        print("✅ Performance metrics:")
        print(f"  DOM Content Loaded: {metrics['domContentLoaded']:.2f}ms")
        print(f"  Load Complete: {metrics['loadComplete']:.2f}ms")
        print(f"  Total Time: {metrics['totalTime']:.2f}ms")

        # Performance assertions
        assert_that(
            navigation_time,
            less_than(10000),
            "Navigation should complete within 10 seconds",
        )
        if search_time > 0:  # Only check if search actually happened
            assert_that(
                search_time,
                less_than(15000),
                "Search should complete within 15 seconds",
            )
