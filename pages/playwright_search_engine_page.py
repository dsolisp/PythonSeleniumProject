"""Playwright implementation of Search Engine page."""

import contextlib
import time

from playwright.sync_api import Error as PlaywrightError

from config.settings import settings
from locators.playwright_search_engine_locators import PlaywrightSearchEngineLocators
from pages.playwright_base_page import TIMEOUT_DEFAULT_MS, PlaywrightBasePage


class PlaywrightSearchEnginePage(PlaywrightBasePage):
    """Playwright Search Engine page with modern browser automation."""

    def __init__(self, page):
        """Initialize Search Engine page."""
        super().__init__(page)
        self.base_url = settings.BASE_URL
        self.locators = PlaywrightSearchEngineLocators

    def open_search_engine(self):
        """Navigate to Search engine homepage. Returns True on success."""
        try:
            self.navigate_to(self.base_url)
            self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_DEFAULT_MS)
            time.sleep(0.5)
            if self.is_captcha_present():
                return False
            self.page.wait_for_selector(
                self.locators.SEARCH_INPUT,
                timeout=TIMEOUT_DEFAULT_MS,
            )
        except (TimeoutError, PlaywrightError):
            return False
        else:
            return True

    def search_for(self, search_term, *, wait_for_results=True):
        """
        Perform a search.

        Args:
            search_term: The term to search for
            wait_for_results: Whether to wait for results to load

        Returns True on success.
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
                    self.page.wait_for_load_state(
                        "networkidle", timeout=TIMEOUT_DEFAULT_MS
                    )
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
                        timeout=TIMEOUT_DEFAULT_MS,
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

    def get_search_input(self):
        """Get the search input value. Returns string or None."""
        try:
            element = self.page.wait_for_selector(
                self.locators.SEARCH_INPUT,
                timeout=TIMEOUT_DEFAULT_MS,
            )
            return element.input_value()
        except TimeoutError:
            return None

    def get_search_suggestions(self):
        """Get search suggestions. Returns list of strings."""
        try:
            self.page.wait_for_selector(
                self.locators.SEARCH_SUGGESTIONS,
                timeout=TIMEOUT_DEFAULT_MS,
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

    def get_result_count(self):
        """Get number of search results. Returns int."""
        try:
            self.page.wait_for_selector(
                self.locators.RESULT_TITLES,
                timeout=TIMEOUT_DEFAULT_MS,
            )
            results = self.page.query_selector_all(self.locators.RESULT_TITLES)
            return len(results)
        except TimeoutError:
            return 0

    def get_result_titles(self):
        """Get titles of search results. Returns list of strings."""
        try:
            self.page.wait_for_selector(
                self.locators.RESULT_TITLES,
                timeout=TIMEOUT_DEFAULT_MS,
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

    def get_result_links(self):
        """Get URLs of search result links. Returns list of strings."""
        try:
            self.page.wait_for_selector(
                self.locators.RESULT_LINKS, timeout=TIMEOUT_DEFAULT_MS
            )
            link_elements = self.page.query_selector_all(
                self.locators.RESULT_LINKS,
            )

            links = []
            for element in link_elements:
                link = element.query_selector(self.locators.ANCESTOR_LINK_XPATH)
                if link:
                    href = link.get_attribute("href")
                    if href:
                        links.append(href)

        except TimeoutError:
            return []
        else:
            return links

    def click_first_result(self):
        """Click the first search result. Returns True on success."""
        try:
            first_result = self.page.wait_for_selector(
                f"{self.locators.RESULT_LINKS}:first-child",
                timeout=TIMEOUT_DEFAULT_MS,
            )

            if first_result:
                first_result.click()
                self.navigation_actions.wait_for_navigation()
                return True

        except TimeoutError as e:
            print(f"Failed to click first result: {e}")

        return False

    def is_captcha_present(self):
        """Check if CAPTCHA is present. Returns True or False."""
        try:
            current_url = self.navigation_actions.get_current_url()
            if any(
                word in current_url.lower()
                for word in ["sorry", "captcha", "unusual+traffic"]
            ):
                return True

            captcha_element = self.page.query_selector(
                self.locators.CAPTCHA_CONTAINER,
            )
        except TimeoutError:
            return False
        else:
            return captcha_element is not None

    def has_results(self):
        """Check if search results are present. Returns True or False."""
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
        search_term,
        site_filter=None,
        file_type=None,
        date_range=None,
    ):
        """
        Perform advanced search with filters.

        Args:
            search_term: Base search term
            site_filter: Site (e.g., "github.com" adds site: prefix)
            file_type: File type (e.g., "pdf" adds filetype: prefix)
            date_range: Date range filter (limited support)

        Returns True on success.
        """
        try:
            query_parts = [search_term]

            if site_filter:
                site = site_filter.replace("site:", "").strip()
                query_parts.append(f"site:{site}")

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

    def wait_for_search_completion(self):
        """Wait for search to complete. Returns True on success."""
        try:
            selector = f"{self.locators.RESULTS_CONTAINER}, {self.locators.NO_RESULTS}"
            self.page.wait_for_selector(
                selector,
                timeout=TIMEOUT_DEFAULT_MS,
            )
            self.page.wait_for_load_state("networkidle", timeout=TIMEOUT_DEFAULT_MS)
        except TimeoutError:
            return False
        else:
            return True

    def take_element_screenshot(self, selector, filename=None):
        """Take element screenshot. Returns bytes."""
        return self.screenshot_actions.take_element_screenshot(selector, filename)
