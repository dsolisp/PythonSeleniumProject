"""
Real Unit Tests for Playwright Factory Functions
Testing actual factory logic and configuration.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from hamcrest import assert_that, equal_to, instance_of, is_, none, not_none

from utils.playwright_factory import (
    PlaywrightFactory,
    PlaywrightPage,
    create_playwright_session,
)


class TestPlaywrightFactory:
    """Test PlaywrightFactory methods."""

    @pytest.mark.asyncio
    async def test_create_browser_chromium(self):
        """Test Chromium browser creation."""
        factory = PlaywrightFactory()

        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)

            result = await factory.create_browser("chromium", headless=True)

            assert_that(result, equal_to(mock_browser))
            assert_that(factory.browser, equal_to(mock_browser))
            mock_pw.chromium.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_browser_firefox(self):
        """Test Firefox browser creation."""
        factory = PlaywrightFactory()

        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.firefox.launch = AsyncMock(return_value=mock_browser)

            result = await factory.create_browser("firefox", headless=True)

            assert_that(result, equal_to(mock_browser))
            assert_that(factory.browser, equal_to(mock_browser))
            mock_pw.firefox.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_browser_webkit(self):
        """Test WebKit browser creation."""
        factory = PlaywrightFactory()

        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.webkit.launch = AsyncMock(return_value=mock_browser)

            result = await factory.create_browser("webkit", headless=False)

            assert_that(result, equal_to(mock_browser))
            assert_that(factory.browser, equal_to(mock_browser))
            mock_pw.webkit.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_browser_unsupported_type(self):
        """Test unsupported browser type raises error."""
        factory = PlaywrightFactory()

        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance

            with pytest.raises(ValueError, match="Unsupported browser type: safari"):
                await factory.create_browser("safari")

    @pytest.mark.asyncio
    async def test_create_context_with_browser(self):
        """Test context creation with provided browser."""
        factory = PlaywrightFactory()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        result = await factory.create_context(mock_browser)

        assert_that(result, equal_to(mock_context))
        assert_that(factory.context, equal_to(mock_context))
        mock_browser.new_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_context_without_browser_raises_error(self):
        """Test context creation without browser raises error."""
        factory = PlaywrightFactory()

        with pytest.raises(ValueError, match="No browser instance available"):
            await factory.create_context()

    @pytest.mark.asyncio
    async def test_create_context_uses_factory_browser(self):
        """Test context creation uses factory's browser if not provided."""
        factory = PlaywrightFactory()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context
        factory.browser = mock_browser

        result = await factory.create_context()

        assert_that(result, equal_to(mock_context))
        mock_browser.new_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_with_context(self):
        """Test page creation with provided context."""
        factory = PlaywrightFactory()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_context.new_page.return_value = mock_page

        result = await factory.create_page(mock_context)

        assert_that(result, equal_to(mock_page))
        mock_context.new_page.assert_called_once()
        mock_page.set_default_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_without_context_raises_error(self):
        """Test page creation without context raises error."""
        factory = PlaywrightFactory()

        with pytest.raises(ValueError, match="No browser context available"):
            await factory.create_page()

    @pytest.mark.asyncio
    async def test_create_page_uses_factory_context(self):
        """Test page creation uses factory's context if not provided."""
        factory = PlaywrightFactory()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_context.new_page.return_value = mock_page
        factory.context = mock_context

        result = await factory.create_page()

        assert_that(result, equal_to(mock_page))
        mock_context.new_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_full_session(self):
        """Test cleanup of full session."""
        factory = PlaywrightFactory()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()
        factory.context = mock_context
        factory.browser = mock_browser
        factory.playwright = mock_playwright

        await factory.cleanup()

        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        assert_that(factory.context, is_(none()))
        assert_that(factory.browser, is_(none()))
        assert_that(factory.playwright, is_(none()))

    @pytest.mark.asyncio
    async def test_cleanup_handles_none_values(self):
        """Test cleanup handles None values gracefully."""
        factory = PlaywrightFactory()
        factory.context = None
        factory.browser = None
        factory.playwright = None

        # Should not raise exception
        await factory.cleanup()

        assert_that(factory.context, is_(none()))
        assert_that(factory.browser, is_(none()))
        assert_that(factory.playwright, is_(none()))

    @pytest.mark.asyncio
    async def test_cleanup_partial_session(self):
        """Test cleanup of partial session (only browser)."""
        factory = PlaywrightFactory()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()
        factory.context = None
        factory.browser = mock_browser
        factory.playwright = mock_playwright

        await factory.cleanup()

        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()


class TestPlaywrightPage:
    """Test PlaywrightPage wrapper methods."""

    @pytest.mark.asyncio
    async def test_navigate_to(self):
        """Test navigate_to method."""
        mock_page = AsyncMock()
        wrapper = PlaywrightPage(mock_page)

        await wrapper.navigate_to("https://example.com")

        mock_page.goto.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_find_element_success(self):
        """Test find_element when element exists."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.find_element("button")

        assert_that(result, equal_to(mock_element))
        mock_page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_element_not_found(self):
        """Test find_element when element not found."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = TimeoutError("Timeout")
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.find_element("button")

        assert_that(result, is_(none()))

    @pytest.mark.asyncio
    async def test_click(self):
        """Test click method."""
        mock_page = AsyncMock()
        wrapper = PlaywrightPage(mock_page)

        await wrapper.click("button")

        mock_page.click.assert_called_once_with("button")

    @pytest.mark.asyncio
    async def test_fill_text(self):
        """Test fill_text method."""
        mock_page = AsyncMock()
        wrapper = PlaywrightPage(mock_page)

        await wrapper.fill_text("input", "test text")

        mock_page.fill.assert_called_once_with("input", "test text")

    @pytest.mark.asyncio
    async def test_get_text(self):
        """Test get_text method."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Sample Text"
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.get_text("h1")

        assert_that(result, equal_to("Sample Text"))

    @pytest.mark.asyncio
    async def test_get_text_empty(self):
        """Test get_text when element has no text."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content.return_value = None
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.get_text("h1")

        assert_that(result, equal_to(""))

    @pytest.mark.asyncio
    async def test_get_title(self):
        """Test get_title method."""
        mock_page = AsyncMock()
        mock_page.title.return_value = "Test Page"
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.get_title()

        assert_that(result, equal_to("Test Page"))

    @pytest.mark.asyncio
    async def test_get_url(self):
        """Test get_url method."""
        mock_page = MagicMock()
        mock_page.url = "https://example.com"
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.get_url()

        assert_that(result, equal_to("https://example.com"))

    @pytest.mark.asyncio
    async def test_wait_for_element(self):
        """Test wait_for_element method."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_page.wait_for_selector.return_value = mock_element
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.wait_for_element("div", timeout=5)

        assert_that(result, equal_to(mock_element))
        mock_page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_screenshot_with_path(self):
        """Test screenshot with file path."""
        mock_page = AsyncMock()
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.screenshot(path="test.png")

        mock_page.screenshot.assert_called_once_with(path="test.png")
        assert_that(result, equal_to(b""))

    @pytest.mark.asyncio
    async def test_screenshot_without_path(self):
        """Test screenshot without file path returns bytes."""
        mock_page = AsyncMock()
        mock_page.screenshot.return_value = b"screenshot_data"
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.screenshot()

        assert_that(result, equal_to(b"screenshot_data"))

    @pytest.mark.asyncio
    async def test_evaluate_script(self):
        """Test evaluate_script method."""
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = 42
        wrapper = PlaywrightPage(mock_page)

        result = await wrapper.evaluate_script("return 40 + 2")

        assert_that(result, equal_to(42))
        mock_page.evaluate.assert_called_once_with("return 40 + 2")


class TestCreatePlaywrightSession:
    """Test create_playwright_session utility function."""

    @pytest.mark.asyncio
    async def test_create_playwright_session_basic(self):
        """Test basic session creation."""
        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)

            factory, page_wrapper = await create_playwright_session()

            assert_that(factory, is_(not_none()))
            assert_that(page_wrapper, is_(not_none()))
            assert_that(page_wrapper, instance_of(PlaywrightPage))
            assert_that(factory.browser, equal_to(mock_browser))
            assert_that(factory.context, equal_to(mock_context))

    @pytest.mark.asyncio
    async def test_create_playwright_session_firefox(self):
        """Test session creation with Firefox."""
        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.firefox.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)

            factory, page_wrapper = await create_playwright_session(
                browser_type="firefox",
                headless=True,
            )

            assert_that(factory, is_(not_none()))
            assert_that(page_wrapper, instance_of(PlaywrightPage))
            mock_pw.firefox.launch.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_playwright_session_returns_tuple(self):
        """Test session creation returns proper tuple."""
        with patch("utils.playwright_factory.async_playwright") as mock_playwright:
            mock_pw = AsyncMock()
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()

            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.start = AsyncMock(return_value=mock_pw)
            mock_playwright.return_value = mock_playwright_instance
            mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            mock_context.new_page = AsyncMock(return_value=mock_page)

            result = await create_playwright_session()

            assert_that(isinstance(result, tuple), is_(True))
            assert_that(len(result), equal_to(2))
            assert_that(result[0], instance_of(PlaywrightFactory))
            assert_that(result[1], instance_of(PlaywrightPage))
