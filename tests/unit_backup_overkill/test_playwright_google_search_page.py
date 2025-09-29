"""
Unit tests for Playwright Google Search page functionality.
Tests class instantiation, method signatures, and search operations.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from playwright.async_api import Page

from pages.playwright_google_search_page import PlaywrightGoogleSearchPage


class TestPlaywrightGoogleSearchPage:
    """Unit tests for PlaywrightGoogleSearchPage class."""
    
    def test_google_search_page_instantiation(self):
        """Test that PlaywrightGoogleSearchPage can be instantiated."""
        mock_page = Mock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        assert search_page is not None
        assert search_page.page == mock_page
        assert search_page.base_url == "https://www.google.com"
    
    def test_google_search_page_has_required_methods(self):
        """Test that Google search page has all expected methods."""
        mock_page = Mock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        expected_methods = [
            'open_google', 'search_for', 'get_search_input', 'get_search_suggestions',
            'get_result_count', 'get_result_titles', 'get_result_links',
            'click_first_result', 'is_captcha_present', 'has_results',
            'perform_advanced_search', 'wait_for_search_completion'
        ]
        
        for method_name in expected_methods:
            assert hasattr(search_page, method_name)
            assert callable(getattr(search_page, method_name))
    
    def test_search_page_selectors_defined(self):
        """Test that all necessary selectors are defined."""
        mock_page = Mock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        required_selectors = [
            'SEARCH_INPUT', 'SEARCH_BUTTON', 'SEARCH_SUGGESTIONS',
            'RESULTS_CONTAINER', 'RESULT_LINKS', 'RESULT_TITLES',
            'RESULT_DESCRIPTIONS', 'CAPTCHA_CONTAINER', 'NO_RESULTS'
        ]
        
        for selector_name in required_selectors:
            assert hasattr(search_page, selector_name)
            assert isinstance(getattr(search_page, selector_name), str)
    
    @pytest.mark.asyncio
    async def test_open_google_success(self):
        """Test open_google method success case."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock successful navigation
        search_page.is_captcha_present = AsyncMock(return_value=False)
        
        result = await search_page.open_google()
        
        assert result is True
        mock_page.goto.assert_called_once_with("https://www.google.com")
        mock_page.wait_for_load_state.assert_called_once()
        mock_page.wait_for_selector.assert_called()
    
    @pytest.mark.asyncio
    async def test_open_google_captcha_detected(self):
        """Test open_google method when CAPTCHA is detected."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock CAPTCHA detection
        search_page.is_captcha_present = AsyncMock(return_value=True)
        
        result = await search_page.open_google()
        
        assert result is False
        mock_page.goto.assert_called_once_with("https://www.google.com")
    
    @pytest.mark.asyncio
    async def test_open_google_exception(self):
        """Test open_google method when exception occurs."""
        mock_page = AsyncMock()
        mock_page.goto.side_effect = Exception("Navigation failed")
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.open_google()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_search_for_success(self):
        """Test search_for method success case."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock successful search
        search_page.is_captcha_present = AsyncMock(return_value=False)
        
        result = await search_page.search_for("test query")
        
        assert result is True
        # Verify that fill was called (send_keys uses fill internally)
        assert mock_page.fill.called or mock_page.type.called
        mock_page.keyboard.press.assert_called_once_with('Enter')
    
    @pytest.mark.asyncio
    async def test_search_for_captcha_detected(self):
        """Test search_for method when CAPTCHA is detected."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock CAPTCHA detection after search
        search_page.is_captcha_present = AsyncMock(return_value=True)
        
        result = await search_page.search_for("test query", wait_for_results=True)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_search_for_without_waiting(self):
        """Test search_for method without waiting for results."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.search_for("test query", wait_for_results=False)
        
        assert result is True
        # Should not wait for navigation when wait_for_results=False
        mock_page.wait_for_load_state.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_search_input(self):
        """Test get_search_input method."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.input_value.return_value = "current search"
        mock_page.wait_for_selector.return_value = mock_element
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_search_input()
        
        assert result == "current search"
        mock_page.wait_for_selector.assert_called_once()
        mock_element.input_value.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_search_input_not_found(self):
        """Test get_search_input method when input not found."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Element not found")
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_search_input()
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_result_count(self):
        """Test get_result_count method."""
        mock_page = AsyncMock()
        # Mock 5 result elements
        mock_results = [Mock() for _ in range(5)]
        mock_page.query_selector_all.return_value = mock_results
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_result_count()
        
        assert result == 5
        mock_page.wait_for_selector.assert_called_once()
        mock_page.query_selector_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_result_count_no_results(self):
        """Test get_result_count method when no results found."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("No results")
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_result_count()
        
        assert result == 0
    
    @pytest.mark.asyncio
    async def test_get_result_titles(self):
        """Test get_result_titles method."""
        mock_page = AsyncMock()
        
        # Mock title elements
        mock_title1 = AsyncMock()
        mock_title1.text_content.return_value = "First Result Title"
        mock_title2 = AsyncMock()
        mock_title2.text_content.return_value = "Second Result Title"
        
        mock_page.query_selector_all.return_value = [mock_title1, mock_title2]
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_result_titles()
        
        assert result == ["First Result Title", "Second Result Title"]
        mock_page.wait_for_selector.assert_called_once()
        mock_page.query_selector_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_result_links(self):
        """Test get_result_links method."""
        mock_page = AsyncMock()
        
        # Mock link elements
        mock_link_element = AsyncMock()
        mock_parent_link = AsyncMock()
        mock_parent_link.get_attribute.return_value = "https://example.com"
        mock_link_element.query_selector.return_value = mock_parent_link
        
        mock_page.query_selector_all.return_value = [mock_link_element]
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.get_result_links()
        
        assert result == ["https://example.com"]
        mock_page.wait_for_selector.assert_called_once()
        mock_page.query_selector_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_is_captcha_present_url_check(self):
        """Test is_captcha_present method with URL check."""
        mock_page = Mock()  # Using Mock for sync property access
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock navigation actions to return CAPTCHA URL
        search_page.navigation_actions = AsyncMock()
        search_page.navigation_actions.get_current_url.return_value = "https://www.google.com/sorry"
        
        result = await search_page.is_captcha_present()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_captcha_present_element_check(self):
        """Test is_captcha_present method with element check."""
        mock_page = AsyncMock()
        mock_captcha_element = Mock()
        mock_page.query_selector.return_value = mock_captcha_element
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock navigation actions to return normal URL
        search_page.navigation_actions = AsyncMock()
        search_page.navigation_actions.get_current_url.return_value = "https://www.google.com/search"
        
        result = await search_page.is_captcha_present()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_captcha_present_false(self):
        """Test is_captcha_present method returns False."""
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock navigation actions to return normal URL
        search_page.navigation_actions = AsyncMock()
        search_page.navigation_actions.get_current_url.return_value = "https://www.google.com/search"
        
        result = await search_page.is_captcha_present()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_has_results_true(self):
        """Test has_results method returns True."""
        mock_page = AsyncMock()
        mock_results_element = Mock()
        mock_page.query_selector.side_effect = [mock_results_element, None]  # results present, no "no results" message
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.has_results()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_has_results_false(self):
        """Test has_results method returns False."""
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None  # no results container
        
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.has_results()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_perform_advanced_search(self):
        """Test perform_advanced_search method."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Mock the search_for method
        search_page.search_for = AsyncMock(return_value=True)
        
        result = await search_page.perform_advanced_search(
            "python", 
            site_filter="github.com",
            file_type="py"
        )
        
        assert result is True
        search_page.search_for.assert_called_once_with("python site:github.com filetype:py")
    
    @pytest.mark.asyncio
    async def test_wait_for_search_completion_success(self):
        """Test wait_for_search_completion method success."""
        mock_page = AsyncMock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.wait_for_search_completion()
        
        assert result is True
        mock_page.wait_for_selector.assert_called()
        mock_page.wait_for_load_state.assert_called_once_with('networkidle', timeout=5000)
    
    @pytest.mark.asyncio
    async def test_wait_for_search_completion_timeout(self):
        """Test wait_for_search_completion method timeout."""
        mock_page = AsyncMock()
        mock_page.wait_for_selector.side_effect = Exception("Timeout")
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        result = await search_page.wait_for_search_completion()
        
        assert result is False


class TestPlaywrightGoogleSearchPageIntegration:
    """Integration tests for Playwright Google Search page."""
    
    def test_imports_work(self):
        """Test that all imports are successful."""
        from pages.playwright_google_search_page import PlaywrightGoogleSearchPage
        assert PlaywrightGoogleSearchPage is not None
    
    def test_inheritance_structure(self):
        """Test that inheritance structure is correct."""
        mock_page = Mock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Should inherit from PlaywrightBasePage
        from pages.playwright_base_page import PlaywrightBasePage
        assert isinstance(search_page, PlaywrightBasePage)
        
        # Should have all base page functionality
        assert hasattr(search_page, 'element_actions')
        assert hasattr(search_page, 'navigation_actions')
        assert hasattr(search_page, 'screenshot_actions')
    
    def test_selector_robustness(self):
        """Test that selectors are robust and well-formed."""
        mock_page = Mock()
        search_page = PlaywrightGoogleSearchPage(mock_page)
        
        # Search input should handle both input and textarea
        assert 'input[name="q"]' in search_page.SEARCH_INPUT
        assert 'textarea[name="q"]' in search_page.SEARCH_INPUT
        
        # Results container should handle different Google layouts
        assert '#search' in search_page.RESULTS_CONTAINER
        assert '#rso' in search_page.RESULTS_CONTAINER
        
        # Result links should be comprehensive
        assert 'h3' in search_page.RESULT_LINKS