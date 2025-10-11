"""
Playwright base page providing modern browser automation capabilities.
Compatible interface with existing Selenium BasePage but with async capabilities.
"""

from pathlib import Path
from typing import Any, Optional

from playwright.async_api import ElementHandle, Page

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

    async def navigate_to_base_url(self) -> None:
        """Navigate to the base URL from settings."""
        await self.navigate_to(settings.BASE_URL)

    async def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """Wait for page to be fully loaded."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        await self.page.wait_for_load_state("networkidle", timeout=timeout_ms)

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page."""
        return await self.page.evaluate(script)


class PlaywrightElementActions:
    """Element interaction actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    async def click_element(self, selector: str) -> None:
        """Click an element by selector."""
        await self.page.click(selector)

    async def double_click_element(self, selector: str) -> None:
        """Double click an element by selector."""
        await self.page.dblclick(selector)

    async def right_click_element(self, selector: str) -> None:
        """Right click an element by selector."""
        await self.page.click(selector, button="right")

    async def hover_element(self, selector: str) -> None:
        """Hover over an element."""
        await self.page.hover(selector)

    async def send_keys(self, selector: str, text: str, clear: bool = True) -> None:
        """Send keys to an input element."""
        if clear:
            await self.page.fill(selector, text)
        else:
            await self.page.type(selector, text)

    async def clear_element(self, selector: str) -> None:
        """Clear an input element."""
        await self.page.fill(selector, "")

    async def get_element_text(self, selector: str) -> str:
        """Get element text content."""
        element = await self.page.wait_for_selector(selector)
        return await element.text_content() or ""

    async def get_element_attribute(
        self,
        selector: str,
        attribute: str,
    ) -> Optional[str]:
        """Get element attribute value."""
        return await self.page.get_attribute(selector, attribute)

    async def is_element_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        try:
            await self.page.wait_for_selector(selector, state="visible", timeout=5000)
        except TimeoutError:
            return False
        else:
            return True

    async def is_element_enabled(self, selector: str) -> bool:
        """Check if element is enabled."""
        return await self.page.is_enabled(selector)

    async def get_elements(self, selector: str) -> list[ElementHandle]:
        """Get all elements matching selector."""
        return await self.page.query_selector_all(selector)

    async def select_option(self, selector: str, value: str) -> None:
        """Select option in dropdown by value."""
        await self.page.select_option(selector, value=value)

    async def check_checkbox(self, selector: str) -> None:
        """Check a checkbox."""
        await self.page.check(selector)

    async def uncheck_checkbox(self, selector: str) -> None:
        """Uncheck a checkbox."""
        await self.page.uncheck(selector)


class PlaywrightNavigationActions:
    """Navigation actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_url(self, url: str) -> None:
        """Navigate to specific URL."""
        await self.page.goto(url)

    async def refresh_page(self) -> None:
        """Refresh the current page."""
        await self.page.reload()

    async def go_back(self) -> None:
        """Navigate back in browser history."""
        await self.page.go_back()

    async def go_forward(self) -> None:
        """Navigate forward in browser history."""
        await self.page.go_forward()

    async def get_current_url(self) -> str:
        """Get current page URL."""
        return self.page.url

    async def get_page_title(self) -> str:
        """Get page title."""
        return await self.page.title()

    async def wait_for_url_change(self, timeout: Optional[int] = None) -> None:
        """Wait for URL to change."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        await self.page.wait_for_url("**", timeout=timeout_ms)

    async def wait_for_navigation(self, timeout: Optional[int] = None) -> None:
        """Wait for navigation to complete."""
        timeout_ms = (timeout or settings.TIMEOUT) * 1000
        await self.page.wait_for_load_state("networkidle", timeout=timeout_ms)


class PlaywrightScreenshotActions:
    """Screenshot actions for Playwright."""

    def __init__(self, page: Page):
        self.page = page

    async def take_screenshot(
        *,
        self,
        filename: Optional[str] = None,
        full_page: bool = True,
    ) -> bytes:
        """Take a screenshot of the page."""
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await self.page.screenshot(path=str(screenshot_path), full_page=full_page)
            return b""
        return await self.page.screenshot(full_page=full_page)

    async def take_element_screenshot(
        self,
        selector: str,
        filename: Optional[str] = None,
    ) -> bytes:
        """Take a screenshot of a specific element."""
        element = await self.page.wait_for_selector(selector)
        if filename:
            screenshot_path = Path(settings.SCREENSHOTS_DIR) / filename
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await element.screenshot(path=str(screenshot_path))
            return b""
        return await element.screenshot()

    async def compare_screenshot(
        self,
        selector: str,
    ) -> bool:
        """Compare element screenshot with expected image."""
        # This is a placeholder for visual comparison functionality
        # In a real implementation, you'd integrate with visual comparison
        # tools
        await self.take_element_screenshot(selector)
        # Visual comparison logic would go here
        return True  # Placeholder return

    async def record_video_start(self) -> None:
        """Start video recording (if context was configured for video)."""
        # Playwright video recording is configured at context level
        # This is a placeholder for video control

    async def record_video_stop(self) -> Optional[str]:
        """Stop video recording and return path."""
        # Video recording control would be implemented here
        return None
