"""
NEW Playwright Google search tests demonstrating modern browser automation.
This file showcases Playwright capabilities alongside existing Selenium tests.
Original Selenium tests in test_google_search.py remain UNCHANGED.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright

from config.settings import settings
from utils.playwright_factory import create_playwright_session, PlaywrightFactory
from pages.playwright_google_search_page import PlaywrightGoogleSearchPage


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_google_search_basic():
    """
    Basic Google search test using Playwright.
    Demonstrates modern async browser automation.
    """
    factory, playwright_page = None, None
    
    try:
        # Create Playwright session
        factory, playwright_page = await create_playwright_session(
            browser_type="chromium",
            headless=settings.HEADLESS
        )
        
        # Create Google search page
        google_page = PlaywrightGoogleSearchPage(playwright_page.page)
        
        # Test navigation
        success = await google_page.open_google()
        if not success:
            pytest.skip("Could not open Google - likely CAPTCHA or network issue")
        
        # Verify page loaded
        title = await google_page.get_title()
        assert "Google" in title
        
        # Perform search
        search_term = "Python automation testing playwright"
        search_success = await google_page.search_for(search_term, wait_for_results=True)
        
        if not search_success:
            pytest.skip("Search failed - likely CAPTCHA or network issue")
        
        # Wait for search completion
        completion_success = await google_page.wait_for_search_completion()
        assert completion_success, "Search should complete within timeout"
        
        # Verify search was performed
        current_url = await google_page.get_url()
        assert "search" in current_url.lower(), f"Should be on search results page: {current_url}"
        
        # Check for results (if not blocked by CAPTCHA)
        if await google_page.has_results():
            result_count = await google_page.get_result_count()
            assert result_count > 0, "Should have search results"
            
            # Get result titles
            titles = await google_page.get_result_titles()
            assert len(titles) > 0, "Should have result titles"
            
            # Verify search term relevance (basic check)
            titles_text = " ".join(titles).lower()
            assert any(word in titles_text for word in ["python", "automation", "testing"]), \
                "Results should be relevant to search term"
            
            print(f"✅ Found {result_count} results for '{search_term}'")
            print(f"First result: {titles[0][:100]}...")
        else:
            print("⚠️ No results found - may be blocked by anti-bot measures")
            
    except Exception as e:
        print(f"Test error: {e}")
        raise
    finally:
        # Clean up
        if factory:
            await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_google_search_with_suggestions():
    """
    Test Google search suggestions using Playwright.
    Demonstrates advanced element interactions.
    """
    factory, playwright_page = None, None
    
    try:
        factory, playwright_page = await create_playwright_session(
            browser_type="chromium",
            headless=settings.HEADLESS
        )
        
        google_page = PlaywrightGoogleSearchPage(playwright_page.page)
        
        # Open Google
        success = await google_page.open_google()
        if not success:
            pytest.skip("Could not open Google")
        
        # Type partial search term to trigger suggestions
        await google_page.element_actions.send_keys(
            google_page.SEARCH_INPUT, 
            "playwright browser", 
            clear=True
        )
        
        # Wait a moment for suggestions to appear
        await asyncio.sleep(1)
        
        # Try to get suggestions (may not always appear due to anti-bot measures)
        suggestions = await google_page.get_search_suggestions()
        
        if suggestions:
            assert len(suggestions) > 0, "Should have search suggestions"
            print(f"✅ Found {len(suggestions)} search suggestions")
            for i, suggestion in enumerate(suggestions[:3]):
                print(f"  {i+1}. {suggestion}")
        else:
            print("⚠️ No suggestions found - may be disabled for automation")
        
        # Complete the search
        await playwright_page.page.keyboard.press('Enter')
        
        # Verify search completed
        await google_page.wait_for_search_completion()
        current_url = await google_page.get_url()
        assert "search" in current_url.lower()
        
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_advanced_search():
    """
    Test advanced Google search with filters using Playwright.
    Demonstrates advanced search capabilities.
    """
    factory, playwright_page = None, None
    
    try:
        factory, playwright_page = await create_playwright_session(
            browser_type="chromium", 
            headless=settings.HEADLESS
        )
        
        google_page = PlaywrightGoogleSearchPage(playwright_page.page)
        
        # Open Google
        success = await google_page.open_google()
        if not success:
            pytest.skip("Could not open Google")
        
        # Perform advanced search
        search_success = await google_page.perform_advanced_search(
            search_term="python testing",
            site_filter="github.com",
            file_type="py"
        )
        
        if not search_success:
            pytest.skip("Advanced search failed - likely CAPTCHA")
        
        # Verify advanced search
        current_url = await google_page.get_url()
        assert "search" in current_url.lower()
        
        # The URL should contain our search parameters
        url_lower = current_url.lower()
        expected_terms = ["python", "testing", "site%3agithub.com", "filetype%3apy"]
        
        found_terms = [term for term in expected_terms if term in url_lower]
        print(f"✅ Advanced search URL contains: {found_terms}")
        
        # Check if we have results
        if await google_page.has_results():
            result_count = await google_page.get_result_count()
            print(f"✅ Advanced search returned {result_count} results")
            
            # Get some result links to verify they're from GitHub
            links = await google_page.get_result_links()
            if links:
                github_links = [link for link in links[:5] if "github.com" in link.lower()]
                print(f"✅ Found {len(github_links)} GitHub links in results")
        
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_multiple_browsers():
    """
    Test the same search across multiple browsers.
    Demonstrates Playwright's multi-browser capabilities.
    """
    browsers_to_test = ["chromium", "firefox"] if not settings.HEADLESS else ["chromium"]
    
    for browser_type in browsers_to_test:
        factory, playwright_page = None, None
        
        try:
            print(f"\n🌐 Testing with {browser_type}")
            
            factory, playwright_page = await create_playwright_session(
                browser_type=browser_type,
                headless=settings.HEADLESS
            )
            
            google_page = PlaywrightGoogleSearchPage(playwright_page.page)
            
            # Open Google
            success = await google_page.open_google()
            if not success:
                print(f"⚠️ Could not open Google in {browser_type}")
                continue
            
            # Verify browser-specific behavior
            user_agent = await playwright_page.page.evaluate("navigator.userAgent")
            print(f"User-Agent: {user_agent[:100]}...")
            
            # Perform basic search
            search_success = await google_page.search_for("playwright browser automation")
            
            if search_success and await google_page.has_results():
                result_count = await google_page.get_result_count()
                print(f"✅ {browser_type}: Found {result_count} results")
            else:
                print(f"⚠️ {browser_type}: Search blocked or no results")
                
        except Exception as e:
            print(f"❌ {browser_type}: Error - {e}")
        finally:
            if factory:
                await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_network_interception():
    """
    Test with network interception capabilities.
    Demonstrates Playwright's advanced network features.
    """
    factory, playwright_page = None, None
    
    try:
        factory, playwright_page = await create_playwright_session(
            browser_type="chromium",
            headless=settings.HEADLESS
        )
        
        # Set up network interception
        intercepted_requests = []
        
        async def handle_request(route):
            request = route.request
            intercepted_requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type
            })
            await route.continue_()
        
        # Enable request interception
        await playwright_page.page.route("**/*", handle_request)
        
        google_page = PlaywrightGoogleSearchPage(playwright_page.page)
        
        # Navigate to Google (this will trigger network requests)
        success = await google_page.open_google()
        if not success:
            pytest.skip("Could not open Google")
        
        # Verify we intercepted requests
        assert len(intercepted_requests) > 0, "Should have intercepted network requests"
        
        # Analyze intercepted requests
        google_requests = [req for req in intercepted_requests if 'google' in req['url']]
        assert len(google_requests) > 0, "Should have Google-related requests"
        
        # Check for different resource types
        resource_types = set(req['resource_type'] for req in intercepted_requests)
        print(f"✅ Intercepted {len(intercepted_requests)} requests")
        print(f"Resource types: {sorted(resource_types)}")
        
        # Verify we got the main document
        document_requests = [req for req in intercepted_requests if req['resource_type'] == 'document']
        assert len(document_requests) > 0, "Should have document requests"
        
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio
async def test_playwright_mobile_emulation():
    """
    Test Google search with mobile device emulation.
    Demonstrates responsive testing capabilities.
    """
    factory = None
    
    try:
        # Create factory
        factory = PlaywrightFactory()
        browser = await factory.create_browser("chromium", headless=settings.HEADLESS)
        
        # Create mobile context (iPhone 12 Pro)
        context = await factory.create_context(
            browser,
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        )
        
        page = await factory.create_page(context)
        google_page = PlaywrightGoogleSearchPage(page)
        
        # Test mobile navigation
        success = await google_page.open_google()
        if not success:
            pytest.skip("Could not open Google on mobile")
        
        # Verify mobile layout
        viewport_size = await page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
        assert viewport_size['width'] == 390, "Should have mobile viewport width"
        assert viewport_size['height'] == 844, "Should have mobile viewport height"
        
        # Test mobile search
        search_success = await google_page.search_for("mobile testing playwright")
        
        if search_success and await google_page.has_results():
            result_count = await google_page.get_result_count()
            print(f"✅ Mobile: Found {result_count} results")
        else:
            print("⚠️ Mobile search blocked or no results")
        
        print(f"✅ Mobile emulation test completed")
        
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.playwright
@pytest.mark.asyncio 
@pytest.mark.slow
async def test_playwright_performance_metrics():
    """
    Test with performance metrics collection.
    Demonstrates Playwright's performance monitoring capabilities.
    """
    factory, playwright_page = None, None
    
    try:
        factory, playwright_page = await create_playwright_session(
            browser_type="chromium",
            headless=settings.HEADLESS
        )
        
        google_page = PlaywrightGoogleSearchPage(playwright_page.page)
        
        # Start performance monitoring
        await playwright_page.page.evaluate("performance.mark('test-start')")
        
        # Navigate and measure
        navigation_start = await playwright_page.page.evaluate("performance.now()")
        success = await google_page.open_google()
        navigation_end = await playwright_page.page.evaluate("performance.now()")
        
        if not success:
            pytest.skip("Could not open Google")
        
        navigation_time = navigation_end - navigation_start
        print(f"✅ Navigation time: {navigation_time:.2f}ms")
        
        # Measure search performance
        search_start = await playwright_page.page.evaluate("performance.now()")
        search_success = await google_page.search_for("performance testing")
        search_end = await playwright_page.page.evaluate("performance.now()")
        
        if search_success:
            search_time = search_end - search_start
            print(f"✅ Search time: {search_time:.2f}ms")
            
            # Get basic performance metrics
            metrics = await playwright_page.page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    return {
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                        totalTime: perfData.loadEventEnd - perfData.fetchStart
                    };
                }
            """)
            
            print(f"✅ Performance metrics:")
            print(f"  DOM Content Loaded: {metrics['domContentLoaded']:.2f}ms")
            print(f"  Load Complete: {metrics['loadComplete']:.2f}ms") 
            print(f"  Total Time: {metrics['totalTime']:.2f}ms")
            
            # Performance assertions
            assert navigation_time < 10000, "Navigation should complete within 10 seconds"
            if search_time > 0:  # Only assert if search actually happened
                assert search_time < 15000, "Search should complete within 15 seconds"
        
    finally:
        if factory:
            await factory.cleanup()


# Helper function for test cleanup
async def cleanup_playwright_session(factory):
    """Helper function to clean up Playwright sessions safely."""
    if factory:
        try:
            await factory.cleanup()
        except Exception as e:
            print(f"Cleanup warning: {e}")


# Fixture for Playwright factory cleanup
@pytest.fixture
async def playwright_factory():
    """Fixture providing Playwright factory with automatic cleanup."""
    factory = None
    try:
        from utils.playwright_factory import PlaywrightFactory
        factory = PlaywrightFactory()
        yield factory
    finally:
        if factory:
            await factory.cleanup()