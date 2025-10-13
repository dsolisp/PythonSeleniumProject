import contextlib
import time
from typing import Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

from config.settings import settings
from locators.playwright_search_engine_locators import PlaywrightSearchEngineLocators
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

    def open_search_engine(self) -> bool:
        """
        Navigate to Search engine homepage with robust navigation and CAPTCHA check.
        Returns:
            bool: True if successful, False if CAPTCHA or error occurred
        """
        try:
            self.navigate_to(self.base_url)
            self.page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(0.5)
            if self.is_captcha_present():
                return False
            self.page.wait_for_selector(
                self.locators.SEARCH_INPUT,
                timeout=20000,
            )
        except (TimeoutError, PlaywrightError):
            return False
        else:
            return True

    def search_for(
        self,
        search_term: str,
        *,
        wait_for_results: bool = True,
    ) -> bool:
        """
        Perform a search on the search engine.

        Args:
            search_term: The term to search for
            wait_for_results: Whether to wait for results to load (keyword-only)

        Returns:
            bool: True if search was successful, False otherwise
        """
        try:
            time.sleep(0.5)
            self.element_actions.send_keys(
                self.locators.SEARCH_INPUT,
                search_term,
            )
            time.sleep(0.3)
            self.page.keyboard.press("Enter")

            if wait_for_results:
                with contextlib.suppress(TimeoutError):
                    self.page.wait_for_load_state("networkidle", timeout=20000)
                try:
                    if self.is_captcha_present():
                        return False
                except PlaywrightError:
                    pass
                try:
                    selector = (
                        f"{self.locators.RESULTS_CONTAINER}, "
                        f"{self.locators.NO_RESULTS}, "
                        f"{self.locators.FALLBACK_CONTENT}"
                    )
                    self.page.wait_for_selector(
                        selector,
                        timeout=20000,
                    )
                except TimeoutError:
                    try:
                        current_url = self.navigation_actions.get_current_url()
                        return bool(
                            "q=" in current_url or "search" in current_url.lower(),
                        )
                    except PlaywrightError:
                        return False
                time.sleep(2)
        except TimeoutError:
            return False
        except PlaywrightError:
            return False
        else:
            return True

    def get_search_input(self) -> Optional[str]:
        """
        Get the search input element value.

        Returns:
            str: Current value in search input, None if not found
        """
        try:
            element = self.page.wait_for_selector(
                self.locators.SEARCH_INPUT,
                timeout=5000,
            )
            return element.input_value()
        except TimeoutError:
            return None

    def get_search_suggestions(self) -> list[str]:
        """
        Get search suggestions from dropdown.

        Returns:
            List[str]: List of suggestion texts
        """
        try:
            # Type in search input to trigger suggestions
            self.page.wait_for_selector(
                self.locators.SEARCH_SUGGESTIONS,
                timeout=5000,
            )

            suggestions = self.page.query_selector_all(
                self.locators.SEARCH_SUGGESTIONS,
            )
            suggestion_texts = []

            for suggestion in suggestions:
                text = suggestion.text_content()
                if text:
                    suggestion_texts.append(text.strip())

        except TimeoutError:
            return []
        else:
            return suggestion_texts

    def get_result_count(self) -> int:
        """
        Get the number of search results on the page.

        Returns:
            int: Number of results found
        """
        try:
            self.page.wait_for_selector(
                self.locators.RESULT_TITLES,
                timeout=10000,
            )
            results = self.page.query_selector_all(self.locators.RESULT_TITLES)
            return len(results)
        except TimeoutError:
            return 0

    def get_result_titles(self) -> list[str]:
        """
        Get titles of search results.

        Returns:
            List[str]: List of result titles
        """
        try:
            self.page.wait_for_selector(
                self.locators.RESULT_TITLES,
                timeout=10000,
            )
            title_elements = self.page.query_selector_all(
                self.locators.RESULT_TITLES,
            )

            titles = []
            for element in title_elements:
                text = element.text_content()
                if text:
                    titles.append(text.strip())

        except TimeoutError:
            return []
        else:
            return titles

    def get_result_links(self) -> list[str]:
        """
        Get URLs of search result links.

        Returns:
            List[str]: List of result URLs
        """
        try:
            self.page.wait_for_selector(self.locators.RESULT_LINKS, timeout=10000)
            link_elements = self.page.query_selector_all(
                self.locators.RESULT_LINKS,
            )

            links = []
            for element in link_elements:
                # Get parent link element
                link = element.query_selector(self.locators.ANCESTOR_LINK_XPATH)
                if link:
                    href = link.get_attribute("href")
                    if href:
                        links.append(href)

        except TimeoutError:
            return []
        else:
            return links

    def click_first_result(self) -> bool:
        """
        Click the first search result.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            first_result = self.page.wait_for_selector(
                f"{self.locators.RESULT_LINKS}:first-child",
                timeout=10000,
            )

            if first_result:
                first_result.click()
                self.navigation_actions.wait_for_navigation()
                return True

        except TimeoutError as e:
            print(f"Failed to click first result: {e}")

        return False

    def is_captcha_present(self) -> bool:
        """
        Check if CAPTCHA is present on the page.

        Returns:
            bool: True if CAPTCHA detected, False otherwise
        """
        try:
            # Check URL for CAPTCHA indicators
            current_url = self.navigation_actions.get_current_url()
            if any(
                word in current_url.lower()
                for word in ["sorry", "captcha", "unusual+traffic"]
            ):
                return True

            # Check for CAPTCHA elements
            captcha_element = self.page.query_selector(
                self.locators.CAPTCHA_CONTAINER,
            )
        except TimeoutError:
            return False
        else:
            return captcha_element is not None

    def has_results(self) -> bool:
        """
        Check if search results are present.

        Returns:
            bool: True if results found, False otherwise
        """
        try:
            current_url = self.navigation_actions.get_current_url()
            if "q=" in current_url or "search" in current_url.lower():
                return True
            results_present = self.page.query_selector(
                self.locators.RESULTS_CONTAINER,
            )
            no_results = self.page.query_selector(self.locators.NO_RESULTS)
        except PlaywrightError as e:
            print(f"has_results error: {e}")
            return False
        else:
            return results_present is not None and no_results is None

    def perform_advanced_search(
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
                    "DuckDuckGo limited support with site: filter",
                )

            if date_range:
                query_parts.append(date_range)

            advanced_query = " ".join(query_parts)
            print(f"🔍 Advanced search query: {advanced_query}")

            return self.search_for(advanced_query)

        except TimeoutError as e:
            print(f"Advanced search failed: {e}")
            return False

    def wait_for_search_completion(self, timeout: int = 15) -> bool:
        """
        Wait for search to complete and results to load.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if search completed, False if timeout or error
        """
        try:
            # Wait for either results or no-results message
            selector = f"{self.locators.RESULTS_CONTAINER}, {self.locators.NO_RESULTS}"
            self.page.wait_for_selector(
                selector,
                timeout=timeout * 1000,
            )

            # Additional wait for dynamic content
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except TimeoutError:
            return False
        else:
            return True
