"""
Playwright base page providing modern browser automation capabilities.
Compatible interface with existing Selenium BasePage but with sync capabilities.
"""

from pathlib import Path
from typing import Any, Optional

from playwright.sync_api import Page

from config.settings import settings
from utils.playwright_factory import PlaywrightPage


class PlaywrightBasePage(PlaywrightPage):
    """
    Enhanced Playwright base page with specialized action handlers.
    Provides similar interface to Selenium BasePage for compatibility.
    """

    def __init__(self, page: Page):
        """Initialize with Playwright page."""
        super().__init__(page)
        self.element_actions = PlaywrightElementActions(page)
        self.navigation_actions = PlaywrightNavigationActions(page)
        self.screenshot_actions = PlaywrightScreenshotActions(page)

    def navigate_to_base_url(self) -> None:
        """Navigate to the base URL from settings."""
        self.navigate_to(settings.BASE_URL)

    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """Wait for page to be fully loaded."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        self.page.wait_for_load_state("networkidle", timeout=timeout_ms)

    def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return self.page.evaluate(script)


class PlaywrightElementActions:
    """Element interaction actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    def click_element(self, selector: str) -> None:
        """Click an element by selector."""
        self.page.click(selector)

    def double_click_element(self, selector: str) -> None:
        """Double click an element by selector."""
        self.page.dblclick(selector)

    def right_click_element(self, selector: str) -> None:
        """Right click an element by selector."""
        self.page.click(selector, button="right")

    def hover_element(self, selector: str) -> None:
        """Hover over an element."""
        self.page.hover(selector)

    def send_keys(self, selector: str, text: str, *, clear: bool = True) -> None:
        """Send keys to an input element."""
        if clear:
            self.page.fill(selector, text)
        else:
            self.page.type(selector, text)

    def clear_element(self, selector: str) -> None:
        """Clear an input element."""
        self.page.fill(selector, "")

    def get_element_text(self, selector: str) -> str:
        """Get element text content."""
        element = self.page.wait_for_selector(selector)
        return element.text_content() or ""

    def get_element_attribute(
        self,
        selector: str,
        attribute: str,
    ) -> Optional[str]:
        """Get element attribute value."""
        return self.page.get_attribute(selector, attribute)

    def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=5000)
        except TimeoutError:
            return False
        else:
            return True

    def is_element_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        return self.page.is_enabled(selector)

    def get_elements(self, selector: str):
        """Get all elements matching selector."""
        return self.page.query_selector_all(selector)

    def select_option(self, selector: str, value: str) -> None:
        """Select option in dropdown by value."""
        self.page.select_option(selector, value=value)

    def check_checkbox(self, selector: str) -> None:
        """Check a checkbox."""
        self.page.check(selector)

    def uncheck_checkbox(self, selector: str) -> None:
        """Uncheck a checkbox."""
        self.page.uncheck(selector)


class PlaywrightNavigationActions:
    """Navigation actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    def navigate_to_url(self, url: str) -> None:
        """Navigate to specific URL."""
        self.page.goto(url)

    def refresh_page(self) -> None:
        """Refresh the current page."""
        self.page.reload()

    def go_back(self) -> None:
        """Navigate back in browser history."""
        self.page.go_back()

    def go_forward(self) -> None:
        """Navigate forward in browser history."""
        self.page.go_forward()

    def get_current_url(self) -> str:
        """Get current page URL."""
        return self.page.url

    def get_page_title(self) -> str:
        """Get page title."""
        return self.page.title()

    def wait_for_url_change(self, timeout: Optional[int] = None) -> None:
        """Wait for URL to change."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        self.page.wait_for_url("**", timeout=timeout_ms)

    def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """Wait for navigation to complete."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        self.page.wait_for_load_state("networkidle", timeout=timeout_ms)


class PlaywrightScreenshotActions:
    """Screenshot actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    def take_screenshot(
        self,
        filename: Optional[str] = None,
        *,
        full_page: bool = True,
    ) -> bytes:
        """Take a screenshot of the page."""
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path), full_page=full_page)
            return b""
        return self.page.screenshot(full_page=full_page)

    def take_element_screenshot(
        self,
        selector: str,
        filename: Optional[str] = None,
    ) -> bytes:
        """Take a screenshot of a specific element."""
        element = self.page.wait_for_selector(selector)
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            element.screenshot(path=str(screenshot_path))
            return b""
        return element.screenshot()

    def compare_screenshot(
        self,
        selector: str,
    ) -> bool:
        """Compare element screenshot with expected image."""
        # This is a placeholder for visual comparison functionality
        # In a real implementation, you'd integrate with visual comparison
        # tools
        self.take_element_screenshot(selector)
        # Visual comparison logic would go here
        return True  # Placeholder return

    def record_video_start(self) -> None:
        """Start video recording (if context was configured for video)."""
        # Playwright video recording is configured at context level
        # This is a placeholder for video control

    def record_video_stop(self) -> Optional[str]:
        """Stop video recording and return path."""
        # Video recording control would be implemented here
        return None
