"""
Simple Playwright test to verify basic functionality.
"""
import pytest
from utils.playwright_factory import create_playwright_session


@pytest.mark.asyncio
async def test_playwright_simple_navigation():
    """Simple test to verify Playwright can open a page."""
    factory, page = None, None
    
    try:
        # Create Playwright session
        factory, page = await create_playwright_session(
            browser_type="chromium",
            headless=True
        )
        
        # Navigate to a simple page
        await page.navigate_to("https://httpbin.org/html")
        
        # Wait a moment for page to load
        await page.wait_for_element("body", timeout=10)
        
        # Debug: check current URL and content
        current_url = await page.get_url()
        title = await page.get_title()
        print(f"🔍 Current URL: {current_url}")
        print(f"🔍 Page title: '{title}' (length: {len(title)})")
        
        # Try to get page content for debugging
        try:
            content_snippet = await page.page.content()
            print(f"🔍 Content snippet (first 200 chars): {content_snippet[:200]}")
        except Exception as e:
            print(f"🔍 Could not get content: {e}")
        
        # Try to find the heading with a longer timeout
        try:
            heading_text = await page.get_text("h1")
            print(f"🔍 Found heading: {heading_text}")
        except Exception as e:
            print(f"🔍 Could not find heading: {e}")
            # Try alternative selectors
            try:
                all_text = await page.page.text_content("body")
                print(f"🔍 Body text (first 200 chars): {all_text[:200] if all_text else 'None'}")
            except Exception as e2:
                print(f"🔍 Could not get body text: {e2}")
        
        # Basic assertion - page should at least load
        assert current_url is not None
        print(f"✅ Successfully navigated to: {current_url}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.asyncio
async def test_playwright_factory_browsers():
    """Test that our factory can create different browser types."""
    for browser_type in ["chromium", "firefox"]:
        factory, page = None, None
        
        try:
            factory, page = await create_playwright_session(
                browser_type=browser_type,
                headless=True
            )
            
            # Navigate to a test page
            await page.navigate_to("https://httpbin.org/json")
            
            # Check we get JSON response by accessing the underlying page
            content = await page.page.content()
            assert "slideshow" in content
            
            print(f"✅ {browser_type} browser working correctly")
            
        finally:
            if factory:
                await factory.cleanup()