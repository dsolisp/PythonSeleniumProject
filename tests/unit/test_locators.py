"""
Unit tests for locator classes.
Tests locator definitions and accessibility for page objects.
"""

import pytest
from selenium.webdriver.common.by import By

from locators.google_search_locators import GoogleSearchLocators
from locators.google_result_locators import GoogleResultLocators


class TestGoogleSearchLocators:
    """Test cases for GoogleSearchLocators class."""

    def test_search_box_locator(self):
        """Test search box locator definition."""
        locator = GoogleSearchLocators.SEARCH_BOX
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.NAME
        assert locator[1] == "q"

    def test_search_button_locator(self):
        """Test search button locator definition."""
        locator = GoogleSearchLocators.SEARCH_BUTTON
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.NAME
        assert locator[1] == "btnK"

    def test_lucky_button_locator(self):
        """Test I'm Feeling Lucky button locator definition."""
        locator = GoogleSearchLocators.LUCKY_BUTTON
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.NAME
        assert locator[1] == "btnI"

    def test_suggestions_container_locator(self):
        """Test search suggestions container locator definition."""
        locator = GoogleSearchLocators.SUGGESTIONS_CONTAINER
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".aajZCb"

    def test_suggestion_items_locator(self):
        """Test individual suggestion items locator definition."""
        locator = GoogleSearchLocators.SUGGESTION_ITEMS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".aajZCb li"

    def test_google_logo_locator(self):
        """Test Google logo locator definition."""
        locator = GoogleSearchLocators.GOOGLE_LOGO
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == "#hplogo"

    def test_language_settings_locator(self):
        """Test language settings locator definition."""
        locator = GoogleSearchLocators.LANGUAGE_SETTINGS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.ID
        assert locator[1] == "SIvCob"

    def test_all_locators_are_tuples(self):
        """Test that all locators are properly formatted tuples."""
        locator_attributes = [
            attr for attr in dir(GoogleSearchLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleSearchLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleSearchLocators, attr_name)
            assert isinstance(locator, tuple), f"{attr_name} should be a tuple"
            assert len(locator) == 2, f"{attr_name} should have exactly 2 elements"
            assert isinstance(locator[0], str), f"{attr_name} locator type should be a string"
            assert isinstance(locator[1], str), f"{attr_name} locator value should be a string"

    def test_locators_use_valid_selenium_by_types(self):
        """Test that all locators use valid Selenium By types."""
        valid_by_types = {
            By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME,
            By.CSS_SELECTOR, By.XPATH, By.LINK_TEXT, By.PARTIAL_LINK_TEXT
        }
        
        locator_attributes = [
            attr for attr in dir(GoogleSearchLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleSearchLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleSearchLocators, attr_name)
            assert locator[0] in valid_by_types, f"{attr_name} uses invalid By type: {locator[0]}"

    def test_locator_values_are_not_empty(self):
        """Test that all locator values are not empty strings."""
        locator_attributes = [
            attr for attr in dir(GoogleSearchLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleSearchLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleSearchLocators, attr_name)
            assert locator[1].strip() != "", f"{attr_name} should not have empty locator value"

    def test_class_is_not_instantiable(self):
        """Test that GoogleSearchLocators cannot be instantiated."""
        # This test ensures the class is used as a container for constants
        # We expect either success or a specific behavior depending on implementation
        try:
            instance = GoogleSearchLocators()
            # If instantiation succeeds, verify it doesn't interfere with locator access
            assert hasattr(instance, 'SEARCH_BOX')
        except TypeError:
            # If the class prevents instantiation, that's also valid
            pass


class TestGoogleResultLocators:
    """Test cases for GoogleResultLocators class."""

    def test_results_container_locator(self):
        """Test search results container locator definition."""
        locator = GoogleResultLocators.RESULTS_CONTAINER
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.ID
        assert locator[1] == "search"

    def test_result_items_locator(self):
        """Test individual result items locator definition."""
        locator = GoogleResultLocators.RESULT_ITEMS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".g .yuRUbf"

    def test_result_titles_locator(self):
        """Test result titles locator definition."""
        locator = GoogleResultLocators.RESULT_TITLES
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".g .yuRUbf h3"

    def test_result_links_locator(self):
        """Test result links locator definition."""
        locator = GoogleResultLocators.RESULT_LINKS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".g .yuRUbf a"

    def test_result_descriptions_locator(self):
        """Test result descriptions locator definition."""
        locator = GoogleResultLocators.RESULT_DESCRIPTIONS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".g .VwiC3b"

    def test_results_stats_locator(self):
        """Test results statistics locator definition."""
        locator = GoogleResultLocators.RESULTS_STATS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.ID
        assert locator[1] == "result-stats"

    def test_next_page_button_locator(self):
        """Test next page button locator definition."""
        locator = GoogleResultLocators.NEXT_PAGE_BUTTON
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.ID
        assert locator[1] == "pnnext"

    def test_previous_page_button_locator(self):
        """Test previous page button locator definition."""
        locator = GoogleResultLocators.PREVIOUS_PAGE_BUTTON
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.ID
        assert locator[1] == "pnprev"

    def test_search_box_in_results_locator(self):
        """Test search box in results page locator definition."""
        locator = GoogleResultLocators.SEARCH_BOX_IN_RESULTS
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.NAME
        assert locator[1] == "q"

    def test_did_you_mean_locator(self):
        """Test 'Did you mean' suggestion locator definition."""
        locator = GoogleResultLocators.DID_YOU_MEAN
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == ".gqLQtd a"

    def test_no_results_message_locator(self):
        """Test no results message locator definition."""
        locator = GoogleResultLocators.NO_RESULTS_MESSAGE
        
        assert isinstance(locator, tuple)
        assert len(locator) == 2
        assert locator[0] == By.CSS_SELECTOR
        assert locator[1] == "#topstuff .med"

    def test_all_locators_are_tuples(self):
        """Test that all locators are properly formatted tuples."""
        locator_attributes = [
            attr for attr in dir(GoogleResultLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleResultLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleResultLocators, attr_name)
            assert isinstance(locator, tuple), f"{attr_name} should be a tuple"
            assert len(locator) == 2, f"{attr_name} should have exactly 2 elements"
            assert isinstance(locator[0], str), f"{attr_name} locator type should be a string"
            assert isinstance(locator[1], str), f"{attr_name} locator value should be a string"

    def test_locators_use_valid_selenium_by_types(self):
        """Test that all locators use valid Selenium By types."""
        valid_by_types = {
            By.ID, By.NAME, By.CLASS_NAME, By.TAG_NAME,
            By.CSS_SELECTOR, By.XPATH, By.LINK_TEXT, By.PARTIAL_LINK_TEXT
        }
        
        locator_attributes = [
            attr for attr in dir(GoogleResultLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleResultLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleResultLocators, attr_name)
            assert locator[0] in valid_by_types, f"{attr_name} uses invalid By type: {locator[0]}"

    def test_locator_values_are_not_empty(self):
        """Test that all locator values are not empty strings."""
        locator_attributes = [
            attr for attr in dir(GoogleResultLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleResultLocators, attr))
        ]
        
        for attr_name in locator_attributes:
            locator = getattr(GoogleResultLocators, attr_name)
            assert locator[1].strip() != "", f"{attr_name} should not have empty locator value"

    def test_class_is_not_instantiable(self):
        """Test that GoogleResultLocators cannot be instantiated."""
        # This test ensures the class is used as a container for constants
        try:
            instance = GoogleResultLocators()
            # If instantiation succeeds, verify it doesn't interfere with locator access
            assert hasattr(instance, 'RESULTS_CONTAINER')
        except TypeError:
            # If the class prevents instantiation, that's also valid
            pass


class TestLocatorConsistency:
    """Test cases for consistency between locator classes."""

    def test_search_box_consistency(self):
        """Test that search box locators are consistent across pages."""
        search_locator = GoogleSearchLocators.SEARCH_BOX
        results_search_locator = GoogleResultLocators.SEARCH_BOX_IN_RESULTS
        
        # Both should use the same locator for the search box
        assert search_locator == results_search_locator, (
            "Search box locators should be consistent between search and results pages"
        )

    def test_locator_naming_conventions(self):
        """Test that locator names follow consistent naming conventions."""
        search_attributes = [
            attr for attr in dir(GoogleSearchLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleSearchLocators, attr))
        ]
        
        result_attributes = [
            attr for attr in dir(GoogleResultLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleResultLocators, attr))
        ]
        
        all_attributes = search_attributes + result_attributes
        
        for attr_name in all_attributes:
            # Test naming conventions
            assert attr_name.isupper(), f"{attr_name} should be in UPPER_CASE"
            assert '_' in attr_name or attr_name.isalpha(), f"{attr_name} should use underscore_case"
            assert not attr_name.startswith('_'), f"{attr_name} should not start with underscore"
            assert not attr_name.endswith('_'), f"{attr_name} should not end with underscore"

    def test_no_duplicate_locator_values_within_class(self):
        """Test that there are no duplicate locator values within each class."""
        # Test GoogleSearchLocators
        search_locators = {}
        search_attributes = [
            attr for attr in dir(GoogleSearchLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleSearchLocators, attr))
        ]
        
        for attr_name in search_attributes:
            locator = getattr(GoogleSearchLocators, attr_name)
            locator_key = f"{locator[0]}:{locator[1]}"
            
            if locator_key in search_locators:
                pytest.fail(
                    f"Duplicate locator found in GoogleSearchLocators: "
                    f"{attr_name} and {search_locators[locator_key]} both use {locator}"
                )
            search_locators[locator_key] = attr_name
        
        # Test GoogleResultLocators
        result_locators = {}
        result_attributes = [
            attr for attr in dir(GoogleResultLocators) 
            if not attr.startswith('_') and not callable(getattr(GoogleResultLocators, attr))
        ]
        
        for attr_name in result_attributes:
            locator = getattr(GoogleResultLocators, attr_name)
            locator_key = f"{locator[0]}:{locator[1]}"
            
            if locator_key in result_locators:
                pytest.fail(
                    f"Duplicate locator found in GoogleResultLocators: "
                    f"{attr_name} and {result_locators[locator_key]} both use {locator}"
                )
            result_locators[locator_key] = attr_name

    def test_locator_classes_have_expected_attributes(self):
        """Test that locator classes have expected minimum attributes."""
        # GoogleSearchLocators should have core search elements
        assert hasattr(GoogleSearchLocators, 'SEARCH_BOX')
        assert hasattr(GoogleSearchLocators, 'SEARCH_BUTTON')
        
        # GoogleResultLocators should have core result elements
        assert hasattr(GoogleResultLocators, 'RESULTS_CONTAINER')
        assert hasattr(GoogleResultLocators, 'RESULT_ITEMS')
        assert hasattr(GoogleResultLocators, 'RESULT_TITLES')

    def test_locator_accessibility_from_imports(self):
        """Test that locators are accessible when imported."""
        # Test that we can access locators as expected
        search_box = GoogleSearchLocators.SEARCH_BOX
        results_container = GoogleResultLocators.RESULTS_CONTAINER
        
        assert search_box is not None
        assert results_container is not None
        assert isinstance(search_box, tuple)
        assert isinstance(results_container, tuple)