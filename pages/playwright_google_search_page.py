"""
Playwright Google Search page implementation.
Modern async alternative to Selenium GoogleSearchPage with enhanced capabilities.
"""

import asyncio
from typing import Optional, List
from playwright.async_api import Page

from pages.playwright_base_page import PlaywrightBasePage


class PlaywrightGoogleSearchPage(PlaywrightBasePage):
    """
    Playwright implementation of Google Search page.
    Provides modern async browser automation for Google search functionality.
    """
    
    # Page selectors (more robust than Selenium locators)
    SEARCH_INPUT = 'input[name="q"], textarea[name="q"]'
    SEARCH_BUTTON = 'input[name="btnK"], button[type="submit"]'
    SEARCH_SUGGESTIONS = '[role="listbox"] [role="option"]'
    RESULTS_CONTAINER = '#search, #rso'
    RESULT_LINKS = '#search a h3, #rso a h3'
    RESULT_TITLES = '#search h3, #rso h3'
    RESULT_DESCRIPTIONS = '.VwiC3b, .s3v9rd'
    CAPTCHA_CONTAINER = '#captcha-form, [data-google-captcha]'
    NO_RESULTS = 'p:has-text("did not match any documents")'
    
    def __init__(self, page: Page):
        """Initialize Google Search page."""
        super().__init__(page)
        self.base_url = "https://www.google.com"
        
    async def open_google(self) -> bool:
        """
        Navigate to Google homepage.
        
        Returns:
            bool: True if successful, False if CAPTCHA or error occurred
        """
        try:
            await self.navigate_to(self.base_url)
            await self.wait_for_page_load()
            
            # Check for CAPTCHA
            if await self.is_captcha_present():
                return False
                
            # Wait for search input to be ready
            await self.page.wait_for_selector(self.SEARCH_INPUT, timeout=10000)
            return True
            
        except Exception as e:
            print(f"Failed to open Google: {e}")
            return False
    
    async def search_for(self, search_term: str, wait_for_results: bool = True) -> bool:
        """
        Perform a search on Google.
        
        Args:
            search_term: The term to search for
            wait_for_results: Whether to wait for results to load
            
        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            # Clear and type search term
            await self.element_actions.send_keys(self.SEARCH_INPUT, search_term)
            
            # Submit search (Enter key is more reliable than clicking button)
            await self.page.keyboard.press('Enter')
            
            if wait_for_results:
                # Wait for navigation and results
                await self.navigation_actions.wait_for_navigation()
                
                # Check if we got CAPTCHA'd
                if await self.is_captcha_present():
                    return False
                    
                # Wait for results container
                await self.page.wait_for_selector(
                    f'{self.RESULTS_CONTAINER}, {self.NO_RESULTS}', 
                    timeout=15000
                )
                
            return True
            
        except Exception as e:
            print(f"Search failed: {e}")
            return False
    
    async def get_search_input(self) -> Optional[str]:
        """
        Get the search input element value.
        
        Returns:
            str: Current value in search input, None if not found
        """
        try:
            element = await self.page.wait_for_selector(self.SEARCH_INPUT, timeout=5000)
            return await element.input_value()
        except Exception:
            return None
    
    async def get_search_suggestions(self) -> List[str]:
        """
        Get search suggestions from dropdown.
        
        Returns:
            List[str]: List of suggestion texts
        """
        try:
            # Type in search input to trigger suggestions
            await self.page.wait_for_selector(self.SEARCH_SUGGESTIONS, timeout=5000)
            
            suggestions = await self.page.query_selector_all(self.SEARCH_SUGGESTIONS)
            suggestion_texts = []
            
            for suggestion in suggestions:
                text = await suggestion.text_content()
                if text:
                    suggestion_texts.append(text.strip())
                    
            return suggestion_texts
            
        except Exception:
            return []
    
    async def get_result_count(self) -> int:
        """
        Get the number of search results on the page.
        
        Returns:
            int: Number of results found
        """
        try:
            await self.page.wait_for_selector(self.RESULT_TITLES, timeout=10000)
            results = await self.page.query_selector_all(self.RESULT_TITLES)
            return len(results)
        except Exception:
            return 0
    
    async def get_result_titles(self) -> List[str]:
        """
        Get titles of search results.
        
        Returns:
            List[str]: List of result titles
        """
        try:
            await self.page.wait_for_selector(self.RESULT_TITLES, timeout=10000)
            title_elements = await self.page.query_selector_all(self.RESULT_TITLES)
            
            titles = []
            for element in title_elements:
                text = await element.text_content()
                if text:
                    titles.append(text.strip())
                    
            return titles
            
        except Exception:
            return []
    
    async def get_result_links(self) -> List[str]:
        """
        Get URLs of search result links.
        
        Returns:
            List[str]: List of result URLs
        """
        try:
            await self.page.wait_for_selector(self.RESULT_LINKS, timeout=10000)
            link_elements = await self.page.query_selector_all(self.RESULT_LINKS)
            
            links = []
            for element in link_elements:
                # Get parent link element
                link = await element.query_selector('xpath=ancestor::a')
                if link:
                    href = await link.get_attribute('href')
                    if href:
                        links.append(href)
                        
            return links
            
        except Exception:
            return []
    
    async def click_first_result(self) -> bool:
        """
        Click the first search result.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            first_result = await self.page.wait_for_selector(
                f'{self.RESULT_LINKS}:first-child', 
                timeout=10000
            )
            
            if first_result:
                await first_result.click()
                await self.navigation_actions.wait_for_navigation()
                return True
                
        except Exception as e:
            print(f"Failed to click first result: {e}")
            
        return False
    
    async def is_captcha_present(self) -> bool:
        """
        Check if CAPTCHA is present on the page.
        
        Returns:
            bool: True if CAPTCHA detected, False otherwise
        """
        try:
            # Check URL for CAPTCHA indicators
            current_url = await self.navigation_actions.get_current_url()
            if any(word in current_url.lower() for word in ['sorry', 'captcha', 'unusual+traffic']):
                return True
                
            # Check for CAPTCHA elements
            captcha_element = await self.page.query_selector(self.CAPTCHA_CONTAINER)
            return captcha_element is not None
            
        except Exception:
            return False
    
    async def has_results(self) -> bool:
        """
        Check if search results are present.
        
        Returns:
            bool: True if results found, False otherwise
        """
        try:
            # Check for results container
            results_present = await self.page.query_selector(self.RESULTS_CONTAINER)
            
            # Check for "no results" message
            no_results = await self.page.query_selector(self.NO_RESULTS)
            
            return results_present is not None and no_results is None
            
        except Exception:
            return False
    
    async def perform_advanced_search(
        self, 
        search_term: str,
        site_filter: Optional[str] = None,
        file_type: Optional[str] = None,
        date_range: Optional[str] = None
    ) -> bool:
        """
        Perform advanced search with filters.
        
        Args:
            search_term: Base search term
            site_filter: Site to search within (e.g., "site:github.com")
            file_type: File type filter (e.g., "filetype:pdf")
            date_range: Date range filter
            
        Returns:
            bool: True if search successful, False otherwise
        """
        try:
            # Build advanced search query
            query_parts = [search_term]
            
            if site_filter:
                query_parts.append(f"site:{site_filter}")
            if file_type:
                query_parts.append(f"filetype:{file_type}")
            if date_range:
                query_parts.append(date_range)
                
            advanced_query = " ".join(query_parts)
            
            return await self.search_for(advanced_query)
            
        except Exception as e:
            print(f"Advanced search failed: {e}")
            return False
    
    async def wait_for_search_completion(self, timeout: int = 15) -> bool:
        """
        Wait for search to complete and results to load.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if search completed, False if timeout or error
        """
        try:
            # Wait for either results or no-results message
            await self.page.wait_for_selector(
                f'{self.RESULTS_CONTAINER}, {self.NO_RESULTS}',
                timeout=timeout * 1000
            )
            
            # Additional wait for dynamic content
            await self.page.wait_for_load_state('networkidle', timeout=5000)
            
            return True
            
        except Exception:
            return False