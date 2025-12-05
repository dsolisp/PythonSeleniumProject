"""
Playwright base page providing modern browser automation capabilities.
Compatible interface with existing Selenium BasePage but with sync capabilities.
"""

from pathlib import Path

from config.settings import settings
from utils.playwright_factory import PlaywrightPage

# Timeout constants (in milliseconds for Playwright)
TIMEOUT_DEFAULT_MS = 20000  # 20 seconds for standard operations
TIMEOUT_SLOW_MS = 45000  # 45 seconds for slow-loading elements


class PlaywrightBasePage(PlaywrightPage):
    """Enhanced Playwright base page with specialized action handlers."""

    def __init__(self, page):
        """Initialize with Playwright page."""
        super().__init__(page)
        self.element_actions = PlaywrightElementActions(page)
        self.navigation_actions = PlaywrightNavigationActions(page)
        self.screenshot_actions = PlaywrightScreenshotActions(page)

    def navigate_to_base_url(self):
        """Navigate to the base URL from settings."""
        self.navigate_to(settings.BASE_URL)

    def wait_for_page_load(self):
        """Wait for page to be fully loaded."""
        self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_SLOW_MS)

    def execute_script(self, script):
        """Execute JavaScript on the page. Returns result."""
        return self.page.evaluate(script)


class PlaywrightElementActions:
    """Element interaction actions for Playwright."""

    def __init__(self, page):
        self.page = page

    def click_element(self, selector):
        """Click an element by selector."""
        self.page.click(selector)

    def double_click_element(self, selector):
        """Double click an element by selector."""
        self.page.dblclick(selector)

    def right_click_element(self, selector):
        """Right click an element by selector."""
        self.page.click(selector, button="right")

    def hover_element(self, selector):
        """Hover over an element."""
        self.page.hover(selector)

    def send_keys(self, selector, text, *, clear=True):
        """Send keys to an input element."""
        if clear:
            self.page.fill(selector, text)
        else:
            self.page.type(selector, text)

    def clear_element(self, selector):
        """Clear an input element."""
        self.page.fill(selector, "")

    def get_element_text(self, selector):
        """Get element text content. Returns string."""
        element = self.page.wait_for_selector(selector)
        return element.text_content() or ""

    def get_element_attribute(self, selector, attribute):
        """Get element attribute value. Returns string or None."""
        return self.page.get_attribute(selector, attribute)

    def is_element_visible(self, selector):
        """Check if element is visible. Returns True or False."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=5000)
        except TimeoutError:
            return False
        else:
            return True

    def is_element_enabled(self, selector):
        """Check if element is enabled. Returns True or False."""
        return self.page.is_enabled(selector)

    def get_elements(self, selector):
        """Get all elements matching selector. Returns list."""
        return self.page.query_selector_all(selector)

    def select_option(self, selector, value):
        """Select option in dropdown by value."""
        self.page.select_option(selector, value=value)

    def check_checkbox(self, selector):
        """Check a checkbox."""
        self.page.check(selector)

    def uncheck_checkbox(self, selector):
        """Uncheck a checkbox."""
        self.page.uncheck(selector)


class PlaywrightNavigationActions:
    """Navigation actions for Playwright."""

    def __init__(self, page):
        self.page = page

    def navigate_to_url(self, url):
        """Navigate to specific URL."""
        self.page.goto(url)

    def refresh_page(self):
        """Refresh the current page."""
        self.page.reload()

    def go_back(self):
        """Navigate back in browser history."""
        self.page.go_back()

    def go_forward(self):
        """Navigate forward in browser history."""
        self.page.go_forward()

    def get_current_url(self):
        """Get current page URL. Returns string."""
        return self.page.url

    def get_page_title(self):
        """Get page title. Returns string."""
        return self.page.title()

    def wait_for_url_change(self):
        """Wait for URL to change."""
        self.page.wait_for_url("**", timeout=TIMEOUT_DEFAULT_MS)

    def wait_for_navigation(self):
        """Wait for navigation to complete."""
        self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_SLOW_MS)


class PlaywrightScreenshotActions:
    """Screenshot actions for Playwright."""

    def __init__(self, page):
        self.page = page

    def take_screenshot(self, filename=None, *, full_page=True):
        """Take a screenshot. Returns bytes or empty bytes if saved to file."""
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path), full_page=full_page)
            return b""
        return self.page.screenshot(full_page=full_page)

    def take_element_screenshot(self, selector, filename=None):
        """Take element screenshot. Returns bytes or empty bytes if saved."""
        element = self.page.wait_for_selector(selector)
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            element.screenshot(path=str(screenshot_path))
            return b""
        return element.screenshot()

    def compare_screenshot(self, selector):
        """Compare element screenshot. Returns True (placeholder)."""
        self.take_element_screenshot(selector)
        return True

    def record_video_start(self):
        """Start video recording (placeholder)."""
        pass

    def record_video_stop(self):
        """Stop video recording. Returns path or None (placeholder)."""
