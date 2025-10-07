"""
Playwright Search Engine page implementation.
Modern async alternative to Selenium SearchEnginePage.
"""

from typing import List, Optional

from playwright.async_api import Page

from config.settings import settings
from locators.playwright_search_engine_locators import (
    PlaywrightSearchEngineLocators,
)
from pages.playwright_base_page import PlaywrightBasePage


class PlaywrightSearchEnginePage(PlaywrightBasePage):
    """
    Playwright implementation of Search Engine page.
    Provides modern async browser automation.
    Uses centralized locators.
    """

    def __init__(self, page: Page):
        """Initialize Search Engine page with centralized locators."""
        super().__init__(page)
        self.base_url = settings.BASE_URL
        self.locators = PlaywrightSearchEngineLocators

    async def open_search_engine(self) -> bool:
        """
        Navigate to Search engine homepage.

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
            await self.page.wait_for_selector(self.locators.SEARCH_INPUT, timeout=10000)
            return True

        except Exception as e:
            print(f"Failed to open search engine: {e}")
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
            await self.element_actions.send_keys(
                self.locators.SEARCH_INPUT, search_term
            )

            # Submit search (Enter key is more reliable than clicking button)
            await self.page.keyboard.press("Enter")

            if wait_for_results:
                # Wait for navigation and results
                await self.navigation_actions.wait_for_navigation()

                # Check if we got CAPTCHA'd
                if await self.is_captcha_present():
                    return False

                # Wait for results container indicating search completed
                try:
                    selector = (
                        f"{self.locators.RESULTS_CONTAINER}, "
                        f"{self.locators.NO_RESULTS}, "
                        f"{self.locators.FALLBACK_CONTENT}"
                    )
                    await self.page.wait_for_selector(
                        selector,
                        timeout=15000,
                    )
                except Exception as e:
                    print(f"Results wait timed out: {e}")
                    # Even if timeout, search may have completed
                    # Check if URL changed to indicate search happened
                    current_url = await self.navigation_actions.get_current_url()
                    if "q=" in current_url or "search" in current_url.lower():
                        return True
                    return False

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
            element = await self.page.wait_for_selector(
                self.locators.SEARCH_INPUT, timeout=5000
            )
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
            await self.page.wait_for_selector(
                self.locators.SEARCH_SUGGESTIONS, timeout=5000
            )

            suggestions = await self.page.query_selector_all(
                self.locators.SEARCH_SUGGESTIONS
            )
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
            await self.page.wait_for_selector(
                self.locators.RESULT_TITLES, timeout=10000
            )
            results = await self.page.query_selector_all(self.locators.RESULT_TITLES)
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
            await self.page.wait_for_selector(
                self.locators.RESULT_TITLES, timeout=10000
            )
            title_elements = await self.page.query_selector_all(
                self.locators.RESULT_TITLES
            )

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
            await self.page.wait_for_selector(self.locators.RESULT_LINKS, timeout=10000)
            link_elements = await self.page.query_selector_all(
                self.locators.RESULT_LINKS
            )

            links = []
            for element in link_elements:
                # Get parent link element
                link = await element.query_selector(self.locators.ANCESTOR_LINK_XPATH)
                if link:
                    href = await link.get_attribute("href")
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
                f"{self.locators.RESULT_LINKS}:first-child", timeout=10000
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
            if any(
                word in current_url.lower()
                for word in ["sorry", "captcha", "unusual+traffic"]
            ):
                return True

            # Check for CAPTCHA elements
            captcha_element = await self.page.query_selector(
                self.locators.CAPTCHA_CONTAINER
            )
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
            results_present = await self.page.query_selector(
                self.locators.RESULTS_CONTAINER
            )

            # Check for "no results" message
            no_results = await self.page.query_selector(self.locators.NO_RESULTS)

            return results_present is not None and no_results is None

        except Exception:
            return False

    async def perform_advanced_search(
        self,
        search_term: str,
        site_filter: Optional[str] = None,
        file_type: Optional[str] = None,
        date_range: Optional[str] = None,
    ) -> bool:
        """
        Perform advanced search with filters.

        Note: DuckDuckGo has limited support for advanced operators.
        It supports:
        - site:example.com (works well)
        - filetype:pdf (limited support, may not return results)

        Best practice: Use site: filter alone with simple terms.

        Args:
            search_term: Base search term
            site_filter: Site (e.g., "github.com" adds site: prefix)
            file_type: File type (e.g., "pdf" adds filetype: prefix)
            date_range: Date range filter (limited DuckDuckGo support)

        Returns:
            bool: True if search successful, False otherwise
        """
        try:
            # Build advanced search query
            query_parts = [search_term]

            # DuckDuckGo supports site: operator well
            if site_filter:
                # Remove site: prefix if user included it
                site = site_filter.replace("site:", "").strip()
                query_parts.append(f"site:{site}")

            # Note: DuckDuckGo's filetype: support is limited
            # Combining site: + filetype: often returns no results
            # Only add filetype if no site filter is specified
            if file_type and not site_filter:
                filetype = file_type.replace("filetype:", "").strip()
                query_parts.append(f"filetype:{filetype}")
            elif file_type and site_filter:
                print(
                    f"⚠️ Skipping filetype:{file_type} - "
                    "DuckDuckGo limited support with site: filter"
                )

            if date_range:
                query_parts.append(date_range)

            advanced_query = " ".join(query_parts)
            print(f"🔍 Advanced search query: {advanced_query}")

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
            selector = (
                f"{self.locators.RESULTS_CONTAINER}, " f"{self.locators.NO_RESULTS}"
            )
            await self.page.wait_for_selector(
                selector,
                timeout=timeout * 1000,
            )

            # Additional wait for dynamic content
            await self.page.wait_for_load_state("networkidle", timeout=5000)

            return True

        except Exception:
            return False
