"""
Playwright factory for modern browser automation.
Provides async browser automation capabilities alongside existing Selenium support.
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from config.settings import settings


class PlaywrightFactory:
    """Factory for creating Playwright browser instances."""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def create_browser(
        self, 
        browser_type: str = "chromium",
        headless: bool = None,
        **kwargs
    ) -> Browser:
        """
        Create a Playwright browser instance.
        
        Args:
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            headless: Run in headless mode
            **kwargs: Additional browser launch options
            
        Returns:
            Browser instance
        """
        if headless is None:
            headless = settings.HEADLESS
            
        self.playwright = await async_playwright().start()
        
        browser_options = {
            "headless": headless,
            "timeout": settings.TIMEOUT * 1000,  # Playwright uses milliseconds
            **kwargs
        }
        
        if browser_type.lower() == "chromium":
            self.browser = await self.playwright.chromium.launch(**browser_options)
        elif browser_type.lower() == "firefox":
            self.browser = await self.playwright.firefox.launch(**browser_options)
        elif browser_type.lower() == "webkit":
            self.browser = await self.playwright.webkit.launch(**browser_options)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
            
        return self.browser
    
    async def create_context(
        self, 
        browser: Browser = None,
        **kwargs
    ) -> BrowserContext:
        """
        Create a browser context with optional configuration.
        
        Args:
            browser: Browser instance (uses self.browser if None)
            **kwargs: Context options
            
        Returns:
            BrowserContext instance
        """
        if browser is None:
            browser = self.browser
            
        if browser is None:
            raise ValueError("No browser instance available")
            
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            **kwargs
        }
        
        self.context = await browser.new_context(**context_options)
        return self.context
    
    async def create_page(
        self, 
        context: BrowserContext = None
    ) -> Page:
        """
        Create a new page in the browser context.
        
        Args:
            context: Browser context (uses self.context if None)
            
        Returns:
            Page instance
        """
        if context is None:
            context = self.context
            
        if context is None:
            raise ValueError("No browser context available")
            
        page = await context.new_page()
        
        # Set default timeout
        page.set_default_timeout(settings.TIMEOUT * 1000)
        
        return page
    
    async def cleanup(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
            self.context = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None


class PlaywrightPage:
    """
    Playwright page wrapper with similar interface to Selenium BasePage.
    Provides compatibility layer for existing test patterns.
    """
    
    def __init__(self, page: Page):
        """
        Initialize with Playwright page instance.
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        
    async def navigate_to(self, url: str) -> None:
        """Navigate to URL."""
        await self.page.goto(url)
        
    async def find_element(self, selector: str) -> Optional[Any]:
        """Find element by selector."""
        try:
            return await self.page.wait_for_selector(selector, timeout=5000)
        except Exception:
            return None
            
    async def click(self, selector: str) -> None:
        """Click element by selector."""
        await self.page.click(selector)
        
    async def fill_text(self, selector: str, text: str) -> None:
        """Fill text in input field."""
        await self.page.fill(selector, text)
        
    async def get_text(self, selector: str) -> str:
        """Get text content of element."""
        element = await self.page.wait_for_selector(selector)
        return await element.text_content() or ""
        
    async def get_title(self) -> str:
        """Get page title."""
        return await self.page.title()
        
    async def get_url(self) -> str:
        """Get current URL."""
        return self.page.url
        
    async def wait_for_element(self, selector: str, timeout: int = None) -> Any:
        """Wait for element to be visible."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        return await self.page.wait_for_selector(selector, timeout=timeout_ms)
        
    async def screenshot(self, path: str = None) -> bytes:
        """Take screenshot."""
        if path:
            await self.page.screenshot(path=path)
            return b""
        else:
            return await self.page.screenshot()
            
    async def evaluate_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return await self.page.evaluate(script)


# Utility functions for easy usage
async def create_playwright_session(
    browser_type: str = "chromium",
    headless: bool = None
) -> tuple[PlaywrightFactory, PlaywrightPage]:
    """
    Create a complete Playwright session with factory and page.
    
    Args:
        browser_type: Browser type
        headless: Headless mode
        
    Returns:
        Tuple of (factory, page_wrapper)
    """
    factory = PlaywrightFactory()
    browser = await factory.create_browser(browser_type, headless)
    context = await factory.create_context(browser)
    page = await factory.create_page(context)
    
    playwright_page = PlaywrightPage(page)
    
    return factory, playwright_page