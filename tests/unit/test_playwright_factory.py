"""
Unit Tests for Playwright Factory Functions
Testing synchronous factory logic and configuration.
"""

from unittest.mock import MagicMock, patch

import pytest
from hamcrest import assert_that, equal_to, instance_of, is_, none, not_none

from utils.playwright_factory import (
    PlaywrightFactory,
    PlaywrightPage,
    create_playwright_session,
)


class TestPlaywrightFactory:
    """Test PlaywrightFactory methods."""

    def test_factory_initialization(self):
        """Test factory initializes with None values."""
        factory = PlaywrightFactory()

        assert_that(factory.playwright, is_(none()))
        assert_that(factory.browser, is_(none()))
        assert_that(factory.context, is_(none()))

    def test_create_browser_unsupported_type(self):
        """Test unsupported browser type raises error."""
        factory = PlaywrightFactory()

        with pytest.raises(ValueError, match="Unsupported browser type: safari"):
            factory.create_browser("safari")

    def test_create_context_without_browser_raises_error(self):
        """Test context creation without browser raises error."""
        factory = PlaywrightFactory()

        with pytest.raises(ValueError, match="No browser instance available"):
            factory.create_context()

    def test_create_page_without_context_raises_error(self):
        """Test page creation without context raises error."""
        factory = PlaywrightFactory()

        with pytest.raises(ValueError, match="No browser context available"):
            factory.create_page()

    def test_cleanup_handles_none_values(self):
        """Test cleanup handles None values gracefully."""
        factory = PlaywrightFactory()
        factory.context = None
        factory.browser = None
        factory.playwright = None

        # Should not raise exception
        factory.cleanup()

        assert_that(factory.context, is_(none()))
        assert_that(factory.browser, is_(none()))
        assert_that(factory.playwright, is_(none()))

    @patch("utils.playwright_factory.sync_playwright")
    def test_create_browser_chromium(self, mock_sync_playwright):
        """Test Chromium browser creation."""
        factory = PlaywrightFactory()

        # Mock the playwright chain
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_sync_playwright.return_value.start.return_value = mock_pw
        mock_pw.chromium.launch.return_value = mock_browser

        result = factory.create_browser("chromium", headless=True)

        assert_that(result, equal_to(mock_browser))
        assert_that(factory.browser, equal_to(mock_browser))
        mock_pw.chromium.launch.assert_called_once()

    @patch("utils.playwright_factory.sync_playwright")
    def test_create_browser_firefox(self, mock_sync_playwright):
        """Test Firefox browser creation."""
        factory = PlaywrightFactory()

        # Mock the playwright chain
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_sync_playwright.return_value.start.return_value = mock_pw
        mock_pw.firefox.launch.return_value = mock_browser

        result = factory.create_browser("firefox", headless=True)

        assert_that(result, equal_to(mock_browser))
        assert_that(factory.browser, equal_to(mock_browser))
        mock_pw.firefox.launch.assert_called_once()

    def test_create_context_with_browser(self):
        """Test context creation with provided browser."""
        factory = PlaywrightFactory()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_browser.new_context.return_value = mock_context

        result = factory.create_context(mock_browser)

        assert_that(result, equal_to(mock_context))
        assert_that(factory.context, equal_to(mock_context))
        mock_browser.new_context.assert_called_once()

    def test_create_context_uses_factory_browser(self):
        """Test context creation uses factory's browser if not provided."""
        factory = PlaywrightFactory()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_browser.new_context.return_value = mock_context
        factory.browser = mock_browser

        result = factory.create_context()

        assert_that(result, equal_to(mock_context))
        mock_browser.new_context.assert_called_once()

    def test_create_page_with_context(self):
        """Test page creation with provided context."""
        factory = PlaywrightFactory()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_context.new_page.return_value = mock_page

        result = factory.create_page(mock_context)

        assert_that(result, equal_to(mock_page))
        mock_context.new_page.assert_called_once()
        mock_page.set_default_timeout.assert_called_once()

    def test_create_page_uses_factory_context(self):
        """Test page creation uses factory's context if not provided."""
        factory = PlaywrightFactory()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_context.new_page.return_value = mock_page
        factory.context = mock_context

        result = factory.create_page()

        assert_that(result, equal_to(mock_page))
        mock_context.new_page.assert_called_once()


class TestPlaywrightPage:
    """Test PlaywrightPage wrapper methods."""

    def test_navigate_to(self):
        """Test navigate_to method."""
        mock_page = MagicMock()
        wrapper = PlaywrightPage(mock_page)

        wrapper.navigate_to("https://example.com")

        mock_page.goto.assert_called_once_with("https://example.com")

    def test_find_element_success(self):
        """Test find_element when element exists."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.find_element("button")

        assert_that(result, equal_to(mock_element))
        mock_page.wait_for_selector.assert_called_once()

    def test_find_element_not_found(self):
        """Test find_element when element not found."""
        mock_page = MagicMock()
        mock_page.wait_for_selector.side_effect = TimeoutError("Timeout")
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.find_element("button")

        assert_that(result, is_(none()))

    def test_click(self):
        """Test click method."""
        mock_page = MagicMock()
        wrapper = PlaywrightPage(mock_page)

        wrapper.click("button")

        mock_page.click.assert_called_once_with("button")

    def test_fill_text(self):
        """Test fill_text method."""
        mock_page = MagicMock()
        wrapper = PlaywrightPage(mock_page)

        wrapper.fill_text("input", "test text")

        mock_page.fill.assert_called_once_with("input", "test text")

    def test_get_text(self):
        """Test get_text method."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.text_content.return_value = "Sample Text"
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.get_text("h1")

        assert_that(result, equal_to("Sample Text"))

    def test_get_text_empty(self):
        """Test get_text when element has no text."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_element.text_content.return_value = None
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.get_text("h1")

        assert_that(result, equal_to(""))

    def test_get_title(self):
        """Test get_title method."""
        mock_page = MagicMock()
        mock_page.title.return_value = "Test Page"
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.get_title()

        assert_that(result, equal_to("Test Page"))

    def test_get_url(self):
        """Test get_url method."""
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.get_url()

        assert_that(result, equal_to("https://example.com"))

    def test_wait_for_element(self):
        """Test wait_for_element method."""
        mock_page = MagicMock()
        mock_element = MagicMock()
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.wait_for_element("div", timeout=5)

        assert_that(result, equal_to(mock_element))
        mock_page.wait_for_selector.assert_called_once()

    def test_screenshot_with_path(self):
        """Test screenshot with file path."""
        mock_page = MagicMock()
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.screenshot(path="test.png")

        mock_page.screenshot.assert_called_once_with(path="test.png")
        assert_that(result, equal_to(b""))

    def test_screenshot_without_path(self):
        """Test screenshot without file path returns bytes."""
        mock_page = MagicMock()
        mock_page.screenshot.return_value = b"screenshot_data"
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.screenshot()

        assert_that(result, equal_to(b"screenshot_data"))

    def test_evaluate_script(self):
        """Test evaluate_script method."""
        mock_page = MagicMock()
        mock_page.evaluate.return_value = 42
        wrapper = PlaywrightPage(mock_page)

        result = wrapper.evaluate_script("return 40 + 2")

        assert_that(result, equal_to(42))
        mock_page.evaluate.assert_called_once_with("return 40 + 2")


class TestCreatePlaywrightSession:
    """Test create_playwright_session utility function."""

    @patch("utils.playwright_factory.sync_playwright")
    def test_create_playwright_session_basic(self, mock_sync_playwright):
        """Test basic session creation."""
        # Mock the playwright chain
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_pw
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        factory, page_wrapper = create_playwright_session()

        assert_that(factory, is_(not_none()))
        assert_that(page_wrapper, is_(not_none()))
        assert_that(page_wrapper, instance_of(PlaywrightPage))
        assert_that(factory.browser, equal_to(mock_browser))
        assert_that(factory.context, equal_to(mock_context))

    @patch("utils.playwright_factory.sync_playwright")
    def test_create_playwright_session_firefox(self, mock_sync_playwright):
        """Test session creation with Firefox."""
        # Mock the playwright chain
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_pw
        mock_pw.firefox.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        factory, page_wrapper = create_playwright_session(
            browser_type="firefox",
            headless=True,
        )

        assert_that(factory, is_(not_none()))
        assert_that(page_wrapper, instance_of(PlaywrightPage))
        mock_pw.firefox.launch.assert_called_once()

    @patch("utils.playwright_factory.sync_playwright")
    def test_create_playwright_session_returns_tuple(self, mock_sync_playwright):
        """Test session creation returns proper tuple."""
        # Mock the playwright chain
        mock_pw = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        mock_sync_playwright.return_value.start.return_value = mock_pw
        mock_pw.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        result = create_playwright_session()

        assert_that(isinstance(result, tuple), is_(True))
        assert_that(len(result), equal_to(2))
        assert_that(result[0], instance_of(PlaywrightFactory))
        assert_that(result[1], instance_of(PlaywrightPage))
