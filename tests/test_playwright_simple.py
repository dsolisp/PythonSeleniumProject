"""
Simple Playwright test to verify basic functionality.
"""
import pytest
from hamcrest import assert_that, is_, not_none, contains_string
from utils.playwright_factory import create_playwright_session
from config.settings import settings


@pytest.mark.asyncio
async def test_playwright_simple_navigation():
    factory, page = None, None
    
    try:
        factory, page = await create_playwright_session(
            browser_type="chromium",
            headless=True
        )
        
        await page.navigate_to(settings.TEST_HTML_URL)
        
        await page.wait_for_element("body", timeout=10)
        
        current_url = await page.get_url()
        title = await page.get_title()
        print(f"🔍 Current URL: {current_url}")
        print(f"🔍 Page title: '{title}' (length: {len(title)})")
        
        try:
            content_snippet = await page.page.content()
            print(f"🔍 Content snippet (first 200 chars): {content_snippet[:200]}")
        except Exception as e:
            print(f"🔍 Could not get content: {e}")
        
        try:
            heading_text = await page.get_text("h1")
            print(f"🔍 Found heading: {heading_text}")
        except Exception as e:
            print(f"🔍 Could not find heading: {e}")
            try:
                all_text = await page.page.text_content("body")
                print(f"🔍 Body text (first 200 chars): {all_text[:200] if all_text else 'None'}")
            except Exception as e2:
                print(f"🔍 Could not get body text: {e2}")
        
        assert_that(current_url, is_(not_none()))
        print(f"✅ Successfully navigated to: {current_url}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    
    finally:
        if factory:
            await factory.cleanup()


@pytest.mark.asyncio
async def test_playwright_factory_browsers():
    for browser_type in ["chromium", "firefox"]:
        factory, page = None, None
        
        try:
            factory, page = await create_playwright_session(
                browser_type=browser_type,
                headless=True
            )
            
            await page.navigate_to(settings.TEST_API_URL)
            
            content = await page.page.content()
            assert_that(content, contains_string("slideshow"))
            
            print(f"✅ {browser_type} browser working correctly")
            
        finally:
            if factory:
                await factory.cleanup()