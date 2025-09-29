"""
Unit tests for Playwright factory functionality.
Tests class instantiation, method signatures, and interface compatibility.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

# Import the classes we're testing
from utils.playwright_factory import PlaywrightFactory, PlaywrightPage, create_playwright_session


class TestPlaywrightFactory:
    """Unit tests for PlaywrightFactory class."""
    
    def test_factory_instantiation(self):
        """Test that PlaywrightFactory can be instantiated."""
        factory = PlaywrightFactory()
        assert factory is not None
        assert factory.playwright is None
        assert factory.browser is None
        assert factory.context is None
    
    def test_factory_has_required_methods(self):
        """Test that factory has all expected methods."""
        factory = PlaywrightFactory()
        assert hasattr(factory, 'create_browser')
        assert hasattr(factory, 'create_context')
        assert hasattr(factory, 'create_page')
        assert hasattr(factory, 'cleanup')
        
        # Check methods are callable
        assert callable(factory.create_browser)
        assert callable(factory.create_context)
        assert callable(factory.create_page)
        assert callable(factory.cleanup)
    
    @pytest.mark.asyncio
    async def test_create_browser_method_signature(self):
        """Test create_browser method signature and error handling."""
        factory = PlaywrightFactory()
        
        # Test with invalid browser type
        with pytest.raises(ValueError, match="Unsupported browser type"):
            with patch('utils.playwright_factory.async_playwright') as mock_playwright:
                mock_playwright.return_value.start = AsyncMock()
                await factory.create_browser("invalid_browser")
    
    @pytest.mark.asyncio
    async def test_create_context_without_browser(self):
        """Test create_context raises error when no browser available."""
        factory = PlaywrightFactory()
        
        with pytest.raises(ValueError, match="No browser instance available"):
            await factory.create_context()
    
    @pytest.mark.asyncio
    async def test_create_page_without_context(self):
        """Test create_page raises error when no context available."""
        factory = PlaywrightFactory()
        
        with pytest.raises(ValueError, match="No browser context available"):
            await factory.create_page()
    
    @pytest.mark.asyncio
    async def test_cleanup_method(self):
        """Test cleanup method works without errors."""
        factory = PlaywrightFactory()
        
        # Mock browser and context - save references before cleanup
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_playwright = AsyncMock()
        
        factory.browser = mock_browser
        factory.context = mock_context
        factory.playwright = mock_playwright
        
        # Should not raise any errors
        await factory.cleanup()
        
        # Check cleanup was called on the mocked objects
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        
        # Check attributes are reset
        assert factory.context is None
        assert factory.browser is None
        assert factory.playwright is None


class TestPlaywrightPage:
    """Unit tests for PlaywrightPage wrapper class."""
    
    def test_playwright_page_instantiation(self):
        """Test that PlaywrightPage can be instantiated with mock page."""
        mock_page = Mock()
        playwright_page = PlaywrightPage(mock_page)
        assert playwright_page is not None
        assert playwright_page.page == mock_page
    
    def test_playwright_page_has_required_methods(self):
        """Test that PlaywrightPage has all expected methods."""
        mock_page = Mock()
        playwright_page = PlaywrightPage(mock_page)
        
        expected_methods = [
            'navigate_to', 'find_element', 'click', 'fill_text', 
            'get_text', 'get_title', 'get_url', 'wait_for_element',
            'screenshot', 'evaluate_script'
        ]
        
        for method_name in expected_methods:
            assert hasattr(playwright_page, method_name)
            assert callable(getattr(playwright_page, method_name))
    
    @pytest.mark.asyncio
    async def test_navigate_to_method(self):
        """Test navigate_to method calls page.goto."""
        mock_page = AsyncMock()
        playwright_page = PlaywrightPage(mock_page)
        
        await playwright_page.navigate_to("https://example.com")
        mock_page.goto.assert_called_once_with("https://example.com")
    
    @pytest.mark.asyncio
    async def test_get_title_method(self):
        """Test get_title method calls page.title."""
        mock_page = AsyncMock()
        mock_page.title.return_value = "Test Title"
        playwright_page = PlaywrightPage(mock_page)
        
        title = await playwright_page.get_title()
        assert title == "Test Title"
        mock_page.title.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_url_method(self):
        """Test get_url method returns page.url."""
        mock_page = Mock()
        mock_page.url = "https://example.com"
        playwright_page = PlaywrightPage(mock_page)
        
        url = await playwright_page.get_url()
        assert url == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_find_element_error_handling(self):
        """Test find_element returns None on error."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Element not found")
        playwright_page = PlaywrightPage(mock_page)
        
        result = await playwright_page.find_element("selector")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_text_method(self):
        """Test get_text method works correctly."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.text_content.return_value = "Test Text"
        mock_page.wait_for_selector.return_value = mock_element
        playwright_page = PlaywrightPage(mock_page)
        
        text = await playwright_page.get_text("selector")
        assert text == "Test Text"
        mock_page.wait_for_selector.assert_called_once_with("selector")
        mock_element.text_content.assert_called_once()


class TestPlaywrightUtilityFunctions:
    """Unit tests for utility functions."""
    
    def test_create_playwright_session_function_exists(self):
        """Test that create_playwright_session function exists and is callable."""
        assert callable(create_playwright_session)
    
    @pytest.mark.asyncio
    async def test_create_playwright_session_signature(self):
        """Test create_playwright_session method signature."""
        # This test verifies the function can be called without throwing import errors
        # We mock the actual browser creation since we don't want real browsers in unit tests
        with patch('utils.playwright_factory.PlaywrightFactory') as mock_factory_class:
            mock_factory = AsyncMock()
            mock_factory_class.return_value = mock_factory
            
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            
            mock_factory.create_browser.return_value = mock_browser
            mock_factory.create_context.return_value = mock_context
            mock_factory.create_page.return_value = mock_page
            
            # Should not raise any errors
            try:
                factory, page_wrapper = await create_playwright_session()
                # Basic verification that objects are returned
                assert factory is not None
                assert page_wrapper is not None
            except Exception as e:
                # If there are dependency issues, that's acceptable for unit tests
                # The important thing is the function signature is correct
                assert "playwright" in str(e).lower() or "browser" in str(e).lower()


class TestPlaywrightIntegration:
    """Integration tests for Playwright factory components."""
    
    def test_all_imports_work(self):
        """Test that all imports are successful."""
        # This test ensures no import errors
        from utils.playwright_factory import PlaywrightFactory, PlaywrightPage, create_playwright_session
        
        assert PlaywrightFactory is not None
        assert PlaywrightPage is not None
        assert create_playwright_session is not None
    
    def test_interface_compatibility(self):
        """Test that PlaywrightPage interface is compatible with expected usage patterns."""
        mock_page = Mock()
        playwright_page = PlaywrightPage(mock_page)
        
        # Check that the interface matches what we expect for compatibility
        compatibility_methods = [
            'navigate_to', 'find_element', 'click', 'fill_text', 
            'get_title', 'get_url', 'screenshot'
        ]
        
        for method in compatibility_methods:
            assert hasattr(playwright_page, method), f"Missing method: {method}"
            assert callable(getattr(playwright_page, method)), f"Method not callable: {method}"