from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    is_,
    not_none,
)

"""
Framework functionality tests without external dependencies.
"""

import pytest

from locators.test_framework_locators import TestFrameworkLocators
from pages.base_page import BasePage
from utils.webdriver_factory import DatabaseFactory, WebDriverFactory, get_driver


@pytest.mark.framework
def test_webdriver_factory():
    driver = WebDriverFactory.create_chrome_driver(headless=True)
    assert_that(driver, is_(not_none())), "WebDriver should be created"

    test_html = (
        "data:text/html,<html><body><h1>Test Page</h1>"
        "<input name='test' value='framework'></body></html>"
    )
    driver.get(test_html)

    element = driver.find_element(*TestFrameworkLocators.TEST_INPUT)
    assert_that(element, is_(not_none()), "Should find test element")
    assert_that(
        element.get_attribute("value"),
        equal_to("framework"),
        "Element should have correct value",
    )

    driver.quit()


@pytest.mark.framework
def test_database_factory():
    db = DatabaseFactory.create_database_connection()

    if db:
        assert_that(db, is_(not_none())), "Database connection should be created"
        db.close()
    else:
        pytest.skip("No database available for testing")


@pytest.mark.framework
def test_base_page_functionality(driver):
    test_html = """
    <html>
    <head><title>Framework Test Page</title></head>
    <body>
        <h1 id="title">Test Framework</h1>
        <input id="input1" name="testinput" placeholder="Enter text">
        <button id="btn1">Click Me</button>
        <div id="result"></div>
        <a href="#" id="link1">Test Link</a>
    </body>
    </html>
    """

    base_page = BasePage(driver)

    base_page.navigate_to(f"data:text/html,{test_html}")

    title = base_page.get_title()
    assert_that(
        title,
        contains_string("Framework Test Page"),
        f"Title should contain test page name, got: {title}",
    )

    title_element = base_page.find_element(TestFrameworkLocators.TITLE_ELEMENT)
    assert_that(title_element, is_(not_none())), "Should find title element"

    title_text = base_page.get_text(TestFrameworkLocators.TITLE_ELEMENT)
    assert_that(
        title_text, contains_string("Test Framework")
    ), f"Should get correct text, got: {title_text}"

    is_visible = base_page.is_element_visible(TestFrameworkLocators.TEST_INPUT_1)
    assert_that(is_visible, is_(True)), "Input element should be visible"

    type_success = base_page.send_keys(
        TestFrameworkLocators.TEST_INPUT_1, "Hello Framework!"
    )
    assert_that(type_success, is_(True)), "Should be able to type in input"

    click_success = base_page.click(TestFrameworkLocators.TEST_BUTTON_1)
    assert_that(click_success, is_(True)), "Should be able to click button"

    screenshot_path = base_page.take_screenshot("framework_test.png")
    assert_that(screenshot_path, not_none()), "Should be able to take screenshot"

    print("✅ All BasePage functionality tests passed!")


@pytest.mark.framework
def test_base_page_element_actions_integration():
    driver = WebDriverFactory.create_chrome_driver(headless=True)
    base_page = BasePage(driver)

    try:
        test_html = """
        <html><body>
            <input id="test" name="test" value="initial">
            <button id="clickme">Click</button>
        </body></html>
        """
        driver.get(f"data:text/html,{test_html}")

        element = base_page.find_element(TestFrameworkLocators.TEST_ELEMENT_ID)
        assert_that(element, is_(not_none())), "Should find element"

        success = base_page.send_keys(
            TestFrameworkLocators.TEST_ELEMENT_ID, "new value"
        )
        assert_that(success, is_(True)), "Should be able to type"

        success = base_page.click(TestFrameworkLocators.CLICK_ME_BUTTON)
        assert_that(success, is_(True)), "Should be able to click"

        print("✅ BasePage element actions integration test passed!")

    finally:
        driver.quit()


@pytest.mark.framework
def test_framework_integration():
    driver, db = get_driver(headless=True)

    try:
        base_page = BasePage((driver, db))

        simple_page = (
            "data:text/html,<html><body><h1>Integration Test</h1>"
            "<p>Framework working!</p></body></html>"
        )
        success = base_page.navigate_to(simple_page)
        assert_that(success, is_(True)), "Should be able to navigate"

        current_url = base_page.get_current_url()
        assert_that(
            current_url, contains_string("data:text/html")
        ), "Should be on test page"

        if db:
            query_result = base_page.execute_query("SELECT 1 as test")
            print(f"Database query result: {query_result}")

        print("✅ Framework integration test passed!")

    finally:
        from utils.webdriver_factory import cleanup_driver_and_database

        cleanup_driver_and_database(driver, db)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
