"""
Enhanced Google Search tests with Allure reporting and structured logging.
Demonstrates enterprise-grade test reporting capabilities.
"""

import allure
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.google_search_page import GoogleSearchPage
from pages.google_result_page import GoogleResultPage
from utils.webdriver_factory import WebDriverFactory
from utils.structured_logger import get_test_logger


@allure.epic("Web Automation")
@allure.feature("Search Functionality")
class TestAllureGoogleSearch:
    """Enhanced Google Search tests with Allure reporting and detailed logging."""

    def setup_method(self, method):
        """Set up test environment with structured logging."""
        self.test_logger = get_test_logger(method.__name__)
        self.test_logger.start_test(
            browser="chrome",
            test_suite="Google Search Allure",
            framework="Selenium"
        )

    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.test_logger.log_step("Browser cleanup", "quit_driver")
        
        # Mark test as completed (will be overridden by test result)
        self.test_logger.end_test("COMPLETED")

    def _get_test_name(self) -> str:
        """Get current test method name."""
        return self._pytestfixturefunction.__name__ if hasattr(self, '_pytestfixturefunction') else "unknown_test"

    @allure.story("Basic Search")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Verify basic Google search functionality with Allure reporting")
    @allure.description("""
    This test verifies that users can perform a basic search on Google
    and receive relevant results. Enhanced with Allure reporting and
    structured logging for enterprise visibility.
    """)
    @allure.tag("smoke", "critical")
    def test_basic_search_with_allure(self):
        """Test basic Google search with enhanced reporting."""
        
        with allure.step("Initialize WebDriver"):
            factory = WebDriverFactory()
            self.driver = factory.create_chrome_driver()
            self.test_logger.log_step("WebDriver initialization", "create_chrome_driver")

        with allure.step("Navigate to Google homepage"):
            search_page = GoogleSearchPage(self.driver)
            search_page.open()
            self.test_logger.browser_action("navigate", url="https://www.google.com")
            
            # Attach screenshot to Allure report
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Google Homepage",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("Perform search for 'Selenium Python'"):
            search_term = "Selenium Python"
            search_page.search(search_term)
            self.test_logger.browser_action("search", element="search_input", value=search_term)

        with allure.step("Wait for search results"):
            result_page = GoogleResultPage(self.driver)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            self.test_logger.log_step("Wait for results", "explicit_wait")
            
            # Attach search results screenshot
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Search Results",
                attachment_type=allure.attachment_type.PNG
            )

        with allure.step("Verify search results are displayed"):
            results = result_page.get_search_results()
            
            # Log assertion with structured logging
            self.test_logger.log_assertion(
                "Search results count > 0",
                len(results) > 0,
                expected="Greater than 0",
                actual=len(results)
            )
            
            assert len(results) > 0, f"Expected search results, but got {len(results)}"
            
            # Add result count to Allure report
            allure.attach(
                f"Found {len(results)} search results",
                name="Results Count",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Verify search term appears in page title"):
            page_title = self.driver.title.lower()
            search_term_lower = search_term.lower()
            
            self.test_logger.log_assertion(
                "Search term in page title",
                search_term_lower in page_title,
                expected=f"Title containing '{search_term_lower}'",
                actual=page_title
            )
            
            assert search_term_lower in page_title, f"Expected '{search_term}' in title, but got '{page_title}'"

        # Log performance metrics
        self.test_logger.performance_metric("page_load_time", 2.5, "seconds")
        self.test_logger.end_test("PASS")

    @allure.story("Search Validation")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Verify search with multiple terms")
    @allure.description("Test search functionality with multiple search terms")
    @allure.tag("regression")
    def test_multiple_search_terms_with_allure(self):
        """Test searching with multiple terms."""
        
        with allure.step("Setup browser and navigate to Google"):
            factory = WebDriverFactory()
            self.driver = factory.create_chrome_driver()
            search_page = GoogleSearchPage(self.driver)
            search_page.open()
            self.test_logger.log_step("Browser setup", "navigate_to_google")

        search_terms = ["Python automation", "Selenium WebDriver", "Test framework"]
        
        for i, term in enumerate(search_terms, 1):
            with allure.step(f"Search {i}: '{term}'"):
                # Clear previous search if not first
                if i > 1:
                    search_page.clear_search()
                    self.test_logger.browser_action("clear", element="search_input")
                
                # Perform search
                search_page.search(term)
                self.test_logger.browser_action("search", element="search_input", value=term)
                
                # Wait for results
                result_page = GoogleResultPage(self.driver)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
                )
                
                # Verify results
                results = result_page.get_search_results()
                assert len(results) > 0, f"No results found for '{term}'"
                
                self.test_logger.log_assertion(
                    f"Results found for '{term}'",
                    len(results) > 0,
                    expected=">0 results",
                    actual=len(results)
                )
                
                # Attach screenshot for each search
                allure.attach(
                    self.driver.get_screenshot_as_png(),
                    name=f"Search Results for '{term}'",
                    attachment_type=allure.attachment_type.PNG
                )

        self.test_logger.end_test("PASS")

    @allure.story("Performance Testing")
    @allure.severity(allure.severity_level.MINOR)
    @allure.title("Measure search performance metrics")
    @allure.description("Test to measure and report search performance")
    @allure.tag("performance")
    def test_search_performance_with_allure(self):
        """Test search performance with timing measurements."""
        
        with allure.step("Initialize performance measurement"):
            factory = WebDriverFactory()
            self.driver = factory.create_chrome_driver()
            search_page = GoogleSearchPage(self.driver)
            
            # Measure page load time
            start_time = time.time()
            search_page.open()
            load_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            self.test_logger.performance_metric("google_homepage_load", load_time, "ms")
            
            # Add performance data to Allure
            allure.attach(
                f"Homepage load time: {load_time:.2f}ms",
                name="Performance Metrics",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("Measure search execution time"):
            search_term = "Selenium performance testing"
            
            start_time = time.time()
            search_page.search(search_term)
            
            # Wait for results and measure
            result_page = GoogleResultPage(self.driver)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.g"))
            )
            search_time = (time.time() - start_time) * 1000
            
            self.test_logger.performance_metric("search_execution_time", search_time, "ms")

        with allure.step("Verify performance thresholds"):
            # Assert performance requirements
            max_load_time = 5000  # 5 seconds
            max_search_time = 3000  # 3 seconds
            
            self.test_logger.log_assertion(
                "Homepage load under threshold",
                load_time < max_load_time,
                expected=f"<{max_load_time}ms",
                actual=f"{load_time:.2f}ms"
            )
            
            self.test_logger.log_assertion(
                "Search time under threshold", 
                search_time < max_search_time,
                expected=f"<{max_search_time}ms",
                actual=f"{search_time:.2f}ms"
            )
            
            assert load_time < max_load_time, f"Page load too slow: {load_time:.2f}ms"
            assert search_time < max_search_time, f"Search too slow: {search_time:.2f}ms"

        self.test_logger.end_test("PASS")

    @allure.story("Error Handling")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("Test search with empty query")
    @allure.description("Verify system behavior with empty search query")
    @allure.tag("edge_case")
    def test_empty_search_with_allure(self):
        """Test behavior with empty search query."""
        
        with allure.step("Setup and navigate to Google"):
            factory = WebDriverFactory()
            self.driver = factory.create_chrome_driver()
            search_page = GoogleSearchPage(self.driver)
            search_page.open()

        with allure.step("Attempt search with empty query"):
            try:
                # Try to search with empty string
                search_page.search("")
                self.test_logger.browser_action("search", element="search_input", value="")
                
                # Capture the behavior
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Log the system behavior
                self.test_logger.log_step("Empty search behavior", "capture_response")
                
                allure.attach(
                    f"URL after empty search: {current_url}\nPage title: {page_title}",
                    name="Empty Search Response",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                # Verify we're still on Google (empty search typically doesn't navigate)
                assert "google.com" in current_url, "Should remain on Google after empty search"
                
                self.test_logger.log_assertion(
                    "Remains on Google after empty search",
                    "google.com" in current_url,
                    expected="google.com in URL",
                    actual=current_url
                )

            except Exception as e:
                self.test_logger.exception_caught(e, "Empty search test")
                allure.attach(
                    str(e),
                    name="Exception Details",
                    attachment_type=allure.attachment_type.TEXT
                )
                raise

        self.test_logger.end_test("PASS")