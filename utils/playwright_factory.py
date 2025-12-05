"""
Playwright factory for modern browser automation.
Provides sync browser automation capabilities alongside existing Selenium support.
"""

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from config.constants import USER_AGENT_CHROME
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
        browser_type="chromium",
        *,
        headless=None,
        **kwargs,
    ):
        """
        Create a Playwright browser instance.

        Args:
            browser_type: Browser type ('chromium', 'firefox', 'webkit')
            headless: Run in headless mode
            **kwargs: Additional browser launch options
        """
        if headless is None:
            headless = settings.HEADLESS

        # Validate browser type BEFORE starting playwright
        browser_type_lower = browser_type.lower()
        if browser_type_lower not in ("chromium", "firefox", "webkit"):
            message = f"Unsupported browser type: {browser_type}"
            raise ValueError(message)

        # Reuse existing playwright instance if available
        if self.playwright is None:
            self.playwright = sync_playwright().start()

        browser_options = {
            "headless": headless,
            "timeout": settings.TIMEOUT * SECONDS_TO_MILLISECONDS,
            **kwargs,
        }

        if browser_type_lower == "chromium":
            self.browser = self.playwright.chromium.launch(**browser_options)
        elif browser_type_lower == "firefox":
            self.browser = self.playwright.firefox.launch(**browser_options)
        elif browser_type_lower == "webkit":
            self.browser = self.playwright.webkit.launch(**browser_options)

        return self.browser

    def create_context(self, browser=None, **kwargs):
        """
        Create a browser context with optional configuration.

        Args:
            browser: Browser instance (uses self.browser if None)
            **kwargs: Context options
        """
        if browser is None:
            browser = self.browser

        if browser is None:
            message = "No browser instance available"
            raise ValueError(message)

        # Set realistic user agent and headers to avoid bot detection
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": USER_AGENT_CHROME,
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

    def create_page(self, context=None):
        """
        Create a new page in the browser context.

        Args:
            context: Browser context (uses self.context if None)
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

    def __init__(self, page):
        """Initialize with Playwright page instance."""
        self.page = page

    def navigate_to(self, url):
        """Navigate to URL."""
        self.page.goto(url)

    def find_element(self, selector):
        """Find element by selector. Returns element or None."""
        try:
            return self.page.wait_for_selector(selector, timeout=5000)
        except (TimeoutError, PlaywrightError):
            # Return None if element not found or timeout
            return None

    def click(self, selector):
        """Click element by selector."""
        self.page.click(selector)

    def fill_text(self, selector, text):
        """Fill text in input field."""
        self.page.fill(selector, text)

    def get_text(self, selector):
        """Get text content of element."""
        element = self.page.wait_for_selector(selector)
        return element.text_content() or ""

    def get_title(self):
        """Get page title."""
        return self.page.title()

    def get_url(self):
        """Get current URL."""
        return self.page.url

    def wait_for_element(self, selector, timeout=None):
        """Wait for element to be visible."""
        timeout_ms = (timeout or settings.TIMEOUT) * SECONDS_TO_MILLISECONDS
        return self.page.wait_for_selector(selector, timeout=timeout_ms)

    def screenshot(self, path=None):
        """Take screenshot. Returns bytes or empty bytes if path provided."""
        if path:
            self.page.screenshot(path=path)
            return b""
        return self.page.screenshot()

    def evaluate_script(self, script):
        """Execute JavaScript on the page."""
        return self.page.evaluate(script)


# Utility functions for easy usage
def create_playwright_session(
    *,
    browser_type="chromium",
    headless=None,
):
    """
    Create a complete Playwright session with factory and page.
    Returns tuple of (factory, page_wrapper).
    """
    factory = PlaywrightFactory()
    browser = factory.create_browser(browser_type=browser_type, headless=headless)
    context = factory.create_context(browser)
    page = factory.create_page(context)

    playwright_page = PlaywrightPage(page)

    return factory, playwright_page
