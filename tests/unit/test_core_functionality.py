from hamcrest import (
    assert_that,
    equal_to,
    greater_than,
    has_property,
    instance_of,
    is_,
    not_none,
)

"""
Essential Unit Tests - Only What You Actually Need
A practical, minimal test suite for a Selenium automation framework.
"""

from unittest.mock import Mock


# Test Base Page Core Functionality
class TestBasePage:
    """Test essential BasePage functionality."""

    def test_base_page_init(self):
        """Test BasePage initialization."""
        from pages.base_page import BasePage

        mock_driver = Mock()
        mock_sql = Mock()

        page = BasePage(mock_driver, mock_sql)
        assert_that(page.driver, equal_to(mock_driver))
        assert_that(page.database, equal_to(mock_sql))


# Test Locators Structure
class TestLocators:
    """Test that locators are properly defined with correct structure."""

    def test_google_search_locators_structure(self):
        """Test that Google search locators have correct tuple structure."""
        from locators.search_engine_locators import SearchEngineLocators

        # Test key locators exist and are properly structured
        assert_that(SearchEngineLocators, has_property("SEARCH_BOX"))
        assert_that(SearchEngineLocators, has_property("SEARCH_BUTTON"))

        # Test locators are tuples with correct length
        assert_that(SearchEngineLocators.SEARCH_BOX, instance_of(tuple))
        assert_that(len(SearchEngineLocators.SEARCH_BOX), equal_to(2))
        assert_that(SearchEngineLocators.SEARCH_BOX[1], instance_of(str))
        assert_that(len(SearchEngineLocators.SEARCH_BOX[1]), greater_than(0))

    def test_google_result_locators_structure(self):
        """Test that Google result locators have correct structure."""
        from locators.result_page_locators import ResultPageLocators

        assert_that(ResultPageLocators, has_property("RESULTS_CONTAINER"))
        assert_that(ResultPageLocators.RESULTS_CONTAINER, instance_of(tuple))
        assert_that(len(ResultPageLocators.RESULTS_CONTAINER), equal_to(2))


# Test Page Object Structure
class TestPageObjects:
    """Test that page objects follow correct inheritance patterns."""

    def test_page_object_inheritance(self):
        """Test page objects inherit from BasePage correctly."""
        from pages.base_page import BasePage
        from pages.result_page import ResultPage
        from pages.search_engine_page import SearchEnginePage

        # Test inheritance structure
        assert_that(issubclass(SearchEnginePage, BasePage), is_(True))
        assert_that(issubclass(ResultPage, BasePage), is_(True))

    def test_page_object_initialization(self):
        """Test page objects can be initialized with mock driver."""
        from pages.result_page import ResultPage
        from pages.search_engine_page import SearchEnginePage

        mock_driver = Mock()

        search_page = SearchEnginePage(mock_driver)
        result_page = ResultPage(mock_driver)

        assert_that(search_page, is_(not_none()))
        assert_that(result_page, is_(not_none()))
        assert_that(search_page, has_property("driver"))
        assert_that(result_page, has_property("driver"))
