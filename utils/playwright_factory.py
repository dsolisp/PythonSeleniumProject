"""
Playwright factory for modern browser automation.
Provides sync browser automation capabilities alongside existing Selenium support.
"""

from typing import Any, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)
from playwright.sync_api import (
    Error as PlaywrightError,
)

from config.settings import settings

# Constants
SECONDS_TO_MILLISECONDS = 1000


class PlaywrightFactory:
    """Factory for creating Playwright browser instances."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    def create_browser(
        self,
        browser_type: str = "chromium",
        *,
        headless: Optional[bool] = None,
        **kwargs,
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

        self.playwright = sync_playwright().start()

        browser_options = {
            "headless": headless,
            "timeout": settings.TIMEOUT * SECONDS_TO_MILLISECONDS,
            **kwargs,
        }

        if browser_type.lower() == "chromium":
            self.browser = self.playwright.chromium.launch(**browser_options)
        elif browser_type.lower() == "firefox":
            self.browser = self.playwright.firefox.launch(**browser_options)
        elif browser_type.lower() == "webkit":
            self.browser = self.playwright.webkit.launch(**browser_options)
        else:
            message = f"Unsupported browser type: {browser_type}"
            raise ValueError(message)

        return self.browser

    def create_context(self, browser: Browser = None, **kwargs) -> BrowserContext:
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
            message = "No browser instance available"
            raise ValueError(message)

        # Set realistic user agent and headers to avoid bot detection
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/119.0.0.0 Safari/537.36"
            ),
            "extra_http_headers": {
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,image/apng,*/*;q=0.8,"
                    "application/signed-exchange;v=b3;q=0.7"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            },
            **kwargs,
        }

        self.context = browser.new_context(**context_options)
        return self.context

    def create_page(self, context: BrowserContext = None) -> Page:
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
            message = "No browser context available"
            raise ValueError(message)

        page = context.new_page()

        # Set default timeout
        page.set_default_timeout(settings.TIMEOUT * SECONDS_TO_MILLISECONDS)

        return page

    def cleanup(self):
        """Clean up browser resources with debug and timeouts."""
        try:
            if self.context:
                self.context.close(timeout=10000)
                self.context = None
        except Exception:  # noqa: BLE001
            pass

        try:
            if self.browser:
                self.browser.close(timeout=10000)
                self.browser = None
        except Exception:  # noqa: BLE001
            pass

        try:
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception:  # noqa: BLE001
            pass

    def safe_cleanup(self):
        """
        Safely clean up browser resources with exception handling.

        This method is designed for test teardown where cleanup failures
        should not cause test failures. All exceptions are caught and logged
        as warnings rather than being raised.

        Example:
            >>> factory = PlaywrightFactory()
            >>> # ... use factory ...
            >>> factory.safe_cleanup()  # Won't raise on cleanup errors
        """
        try:
            self.cleanup()
        except (AttributeError, ValueError, TypeError) as e:
            print(f"Cleanup warning: {e}")


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

    def navigate_to(self, url: str) -> None:
        """Navigate to URL."""
        self.page.goto(url)

    def find_element(self, selector: str) -> Optional[Any]:
        """Find element by selector."""
        try:
            return self.page.wait_for_selector(selector, timeout=5000)
        except (TimeoutError, PlaywrightError):
            # Return None if element not found or timeout
            return None

    def click(self, selector: str) -> None:
        """Click element by selector."""
        self.page.click(selector)

    def fill_text(self, selector: str, text: str) -> None:
        """Fill text in input field."""
        self.page.fill(selector, text)

    def get_text(self, selector: str) -> str:
        """Get text content of element."""
        element = self.page.wait_for_selector(selector)
        return element.text_content() or ""

    def get_title(self) -> str:
        """Get page title."""
        return self.page.title()

    def get_url(self) -> str:
        """Get current URL."""
        return self.page.url

    def wait_for_element(
        self,
        selector: str,
        timeout: Optional[int] = None,
    ) -> Any:
        """Wait for element to be visible."""
        timeout_ms = (timeout or settings.TIMEOUT) * SECONDS_TO_MILLISECONDS
        return self.page.wait_for_selector(selector, timeout=timeout_ms)

    def screenshot(self, path: Optional[str] = None) -> bytes:
        """Take screenshot."""
        if path:
            self.page.screenshot(path=path)
            return b""
        return self.page.screenshot()

    def evaluate_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return self.page.evaluate(script)


# Utility functions for easy usage
def create_playwright_session(
    *,
    browser_type: str = "chromium",
    headless: Optional[bool] = None,
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
    browser = factory.create_browser(browser_type=browser_type, headless=headless)
    context = factory.create_context(browser)
    page = factory.create_page(context)

    playwright_page = PlaywrightPage(page)

    return factory, playwright_page
