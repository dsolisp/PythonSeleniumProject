"""
Unit tests for Playwright base page functionality.
Tests class instantiation, method signatures, and action handlers.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from playwright.async_api import Page

from pages.playwright_base_page import (
    PlaywrightBasePage, 
    PlaywrightElementActions,
    PlaywrightNavigationActions,
    PlaywrightScreenshotActions
)


class TestPlaywrightBasePage:
    """Unit tests for PlaywrightBasePage class."""
    
    def test_base_page_instantiation(self):
        """Test that PlaywrightBasePage can be instantiated."""
        mock_page = Mock()
        base_page = PlaywrightBasePage(mock_page)
        
        assert base_page is not None
        assert base_page.page == mock_page
        assert hasattr(base_page, 'element_actions')
        assert hasattr(base_page, 'navigation_actions')
        assert hasattr(base_page, 'screenshot_actions')
    
    def test_base_page_has_required_methods(self):
        """Test that base page has all expected methods."""
        mock_page = Mock()
        base_page = PlaywrightBasePage(mock_page)
        
        expected_methods = [
            'navigate_to_base_url', 'wait_for_page_load', 'execute_script',
            'navigate_to', 'find_element', 'click', 'fill_text', 'get_text',
            'get_title', 'get_url', 'wait_for_element', 'screenshot'
        ]
        
        for method_name in expected_methods:
            assert hasattr(base_page, method_name)
            assert callable(getattr(base_page, method_name))
    
    @pytest.mark.asyncio
    async def test_navigate_to_base_url(self):
        """Test navigate_to_base_url method."""
        mock_page = AsyncMock()
        base_page = PlaywrightBasePage(mock_page)
        
        with patch('pages.playwright_base_page.settings') as mock_settings:
            mock_settings.BASE_URL = "https://example.com"
            
            await base_page.navigate_to_base_url()
            mock_page.goto.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_wait_for_page_load(self):
        """Test wait_for_page_load method."""
        mock_page = AsyncMock()
        base_page = PlaywrightBasePage(mock_page)
        
        with patch('pages.playwright_base_page.settings') as mock_settings:
            mock_settings.TIMEOUT = 10
            
            await base_page.wait_for_page_load()
            mock_page.wait_for_load_state.assert_called_once_with('networkidle', timeout=10000)
    
    @pytest.mark.asyncio
    async def test_execute_script(self):
        """Test execute_script method."""
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = "script_result"
        base_page = PlaywrightBasePage(mock_page)
        
        result = await base_page.execute_script("return 'test';")
        assert result == "script_result"
        mock_page.evaluate.assert_called_once_with("return 'test';")


class TestPlaywrightElementActions:
    """Unit tests for PlaywrightElementActions class."""
    
    def test_element_actions_instantiation(self):
        """Test that PlaywrightElementActions can be instantiated."""
        mock_page = Mock()
        actions = PlaywrightElementActions(mock_page)
        
        assert actions is not None
        assert actions.page == mock_page
    
    def test_element_actions_has_required_methods(self):
        """Test that element actions has all expected methods."""
        mock_page = Mock()
        actions = PlaywrightElementActions(mock_page)
        
        expected_methods = [
            'click_element', 'double_click_element', 'right_click_element',
            'hover_element', 'send_keys', 'clear_element', 'get_element_text',
            'get_element_attribute', 'is_element_visible', 'is_element_enabled',
            'get_elements', 'select_option', 'check_checkbox', 'uncheck_checkbox'
        ]
        
        for method_name in expected_methods:
            assert hasattr(actions, method_name)
            assert callable(getattr(actions, method_name))
    
    @pytest.mark.asyncio
    async def test_click_element(self):
        """Test click_element method."""
        mock_page = AsyncMock()
        actions = PlaywrightElementActions(mock_page)
        
        await actions.click_element("#test-selector")
        mock_page.click.assert_called_once_with("#test-selector")
    
    @pytest.mark.asyncio
    async def test_send_keys_with_clear(self):
        """Test send_keys method with clear=True."""
        mock_page = AsyncMock()
        actions = PlaywrightElementActions(mock_page)
        
        await actions.send_keys("#input", "test text", clear=True)
        mock_page.fill.assert_called_once_with("#input", "test text")
    
    @pytest.mark.asyncio
    async def test_send_keys_without_clear(self):
        """Test send_keys method with clear=False."""
        mock_page = AsyncMock()
        actions = PlaywrightElementActions(mock_page)
        
        await actions.send_keys("#input", "test text", clear=False)
        mock_page.type.assert_called_once_with("#input", "test text")
    
    @pytest.mark.asyncio
    async def test_get_element_text(self):
        """Test get_element_text method."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "element text"
        mock_page.wait_for_selector.return_value = mock_element
        
        actions = PlaywrightElementActions(mock_page)
        
        text = await actions.get_element_text("#selector")
        assert text == "element text"
        mock_page.wait_for_selector.assert_called_once_with("#selector")
        mock_element.text_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_element_visible_true(self):
        """Test is_element_visible returns True when element is visible."""
        mock_page = AsyncMock()
        actions = PlaywrightElementActions(mock_page)
        
        result = await actions.is_element_visible("#visible-element")
        assert result is True
        mock_page.wait_for_selector.assert_called_once_with(
            "#visible-element", state='visible', timeout=5000
        )
    
    @pytest.mark.asyncio
    async def test_is_element_visible_false(self):
        """Test is_element_visible returns False when element not visible."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Element not found")
        actions = PlaywrightElementActions(mock_page)
        
        result = await actions.is_element_visible("#hidden-element")
        assert result is False


class TestPlaywrightNavigationActions:
    """Unit tests for PlaywrightNavigationActions class."""
    
    def test_navigation_actions_instantiation(self):
        """Test that PlaywrightNavigationActions can be instantiated."""
        mock_page = Mock()
        actions = PlaywrightNavigationActions(mock_page)
        
        assert actions is not None
        assert actions.page == mock_page
    
    def test_navigation_actions_has_required_methods(self):
        """Test that navigation actions has all expected methods."""
        mock_page = Mock()
        actions = PlaywrightNavigationActions(mock_page)
        
        expected_methods = [
            'navigate_to_url', 'refresh_page', 'go_back', 'go_forward',
            'get_current_url', 'get_page_title', 'wait_for_url_change',
            'wait_for_navigation'
        ]
        
        for method_name in expected_methods:
            assert hasattr(actions, method_name)
            assert callable(getattr(actions, method_name))
    
    @pytest.mark.asyncio
    async def test_navigate_to_url(self):
        """Test navigate_to_url method."""
        mock_page = AsyncMock()
        actions = PlaywrightNavigationActions(mock_page)
        
        await actions.navigate_to_url("https://example.com")
        mock_page.goto.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_refresh_page(self):
        """Test refresh_page method."""
        mock_page = AsyncMock()
        actions = PlaywrightNavigationActions(mock_page)
        
        await actions.refresh_page()
        mock_page.reload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_current_url(self):
        """Test get_current_url method."""
        mock_page = Mock()
        mock_page.url = "https://current-url.com"
        actions = PlaywrightNavigationActions(mock_page)
        
        url = await actions.get_current_url()
        assert url == "https://current-url.com"
    
    @pytest.mark.asyncio
    async def test_get_page_title(self):
        """Test get_page_title method."""
        mock_page = AsyncMock()
        mock_page.title.return_value = "Page Title"
        actions = PlaywrightNavigationActions(mock_page)
        
        title = await actions.get_page_title()
        assert title == "Page Title"
        mock_page.title.assert_called_once()


class TestPlaywrightScreenshotActions:
    """Unit tests for PlaywrightScreenshotActions class."""
    
    def test_screenshot_actions_instantiation(self):
        """Test that PlaywrightScreenshotActions can be instantiated."""
        mock_page = Mock()
        actions = PlaywrightScreenshotActions(mock_page)
        
        assert actions is not None
        assert actions.page == mock_page
    
    def test_screenshot_actions_has_required_methods(self):
        """Test that screenshot actions has all expected methods."""
        mock_page = Mock()
        actions = PlaywrightScreenshotActions(mock_page)
        
        expected_methods = [
            'take_screenshot', 'take_element_screenshot', 'compare_screenshot',
            'record_video_start', 'record_video_stop'
        ]
        
        for method_name in expected_methods:
            assert hasattr(actions, method_name)
            assert callable(getattr(actions, method_name))
    
    @pytest.mark.asyncio
    async def test_take_screenshot_no_filename(self):
        """Test take_screenshot without filename."""
        mock_page = AsyncMock()
        mock_page.screenshot.return_value = b"screenshot_data"
        actions = PlaywrightScreenshotActions(mock_page)
        
        result = await actions.take_screenshot()
        assert result == b"screenshot_data"
        mock_page.screenshot.assert_called_once_with(full_page=True)
    
    @pytest.mark.asyncio
    async def test_take_element_screenshot(self):
        """Test take_element_screenshot method."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.screenshot.return_value = b"element_screenshot"
        mock_page.wait_for_selector.return_value = mock_element
        
        actions = PlaywrightScreenshotActions(mock_page)
        
        result = await actions.take_element_screenshot("#element")
        assert result == b"element_screenshot"
        mock_page.wait_for_selector.assert_called_once_with("#element")
        mock_element.screenshot.assert_called_once()


class TestPlaywrightPageIntegration:
    """Integration tests for Playwright page components."""
    
    def test_all_imports_work(self):
        """Test that all imports are successful."""
        from pages.playwright_base_page import (
            PlaywrightBasePage, 
            PlaywrightElementActions,
            PlaywrightNavigationActions,
            PlaywrightScreenshotActions
        )
        
        assert PlaywrightBasePage is not None
        assert PlaywrightElementActions is not None
        assert PlaywrightNavigationActions is not None
        assert PlaywrightScreenshotActions is not None
    
    def test_action_handlers_integration(self):
        """Test that action handlers are properly integrated in base page."""
        mock_page = Mock()
        base_page = PlaywrightBasePage(mock_page)
        
        # Check that all action handlers are properly instantiated
        assert isinstance(base_page.element_actions, PlaywrightElementActions)
        assert isinstance(base_page.navigation_actions, PlaywrightNavigationActions)
        assert isinstance(base_page.screenshot_actions, PlaywrightScreenshotActions)
        
        # Check that they share the same page instance
        assert base_page.element_actions.page == mock_page
        assert base_page.navigation_actions.page == mock_page
        assert base_page.screenshot_actions.page == mock_page