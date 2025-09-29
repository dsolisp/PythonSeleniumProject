"""
Test framework locators - for internal test elements.
"""

from selenium.webdriver.common.by import By


class TestFrameworkLocators:
    """Locators for test framework internal elements."""

    # Basic test elements
    TEST_INPUT = (By.NAME, "test")
    TITLE_ELEMENT = (By.ID, "title")
    TEST_ELEMENT_ID = (By.ID, "test")
    
    # Test page elements from test_framework_core.py
    TEST_HEADING = (By.TAG_NAME, "h1")
    TEST_INPUT_1 = (By.ID, "input1")
    TEST_BUTTON_1 = (By.ID, "btn1")
    TEST_LINK_1 = (By.ID, "link1")
    TEST_RESULT_DIV = (By.ID, "result")
    TEST_INPUT_BY_NAME = (By.NAME, "testinput")
    CLICK_ME_BUTTON = (By.ID, "clickme")
    
    # Dynamic test elements
    NONEXISTENT_ELEMENT = (By.ID, "nonexistent-element")
    
    # Fallback element for testing
    ANY_INPUT = (By.TAG_NAME, "input")