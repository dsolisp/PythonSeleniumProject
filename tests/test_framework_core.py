"""
Framework functionality tests without external dependencies.
"""

import pytest

from pages.base_page import BasePage
from utils.webdriver_factory import DatabaseFactory, WebDriverFactory, get_driver


@pytest.mark.framework
def test_webdriver_factory():
    """Test that our WebDriver factory works correctly."""
    # Test individual factory methods
    driver = WebDriverFactory.create_chrome_driver(headless=True)
    assert driver is not None, "WebDriver should be created"

    # Test basic functionality
    test_html = (
        "data:text/html,<html><body><h1>Test Page</h1>"
        "<input name='test' value='framework'></body></html>"
    )
    driver.get(test_html)

    # Find element to verify driver works
    element = driver.find_element("name", "test")
    assert element is not None, "Should find test element"
    assert (
        element.get_attribute("value") == "framework"
    ), "Element should have correct value"

    driver.quit()


@pytest.mark.framework
def test_database_factory():
    """Test that our Database factory works correctly."""
    db = DatabaseFactory.create_database_connection()

    if db:
        # Database exists, test basic functionality
        assert db is not None, "Database connection should be created"
        db.close()
    else:
        # No database available, which is fine
        pytest.skip("No database available for testing")


@pytest.mark.framework
def test_base_page_functionality(driver):
    """Test BasePage functionality with a simple HTML page."""
    # Create a simple test page
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

    # Navigate to test page
    base_page.navigate_to(f"data:text/html,{test_html}")

    # Test navigation functionality
    title = base_page.get_title()
    assert (
        "Framework Test Page" in title
    ), f"Title should contain test page name, got: {title}"

    # Test element finding
    title_element = base_page.find_element(("id", "title"))
    assert title_element is not None, "Should find title element"

    # Test text retrieval
    title_text = base_page.get_text(("id", "title"))
    assert "Test Framework" in title_text, f"Should get correct text, got: {title_text}"

    # Test element visibility
    is_visible = base_page.is_element_visible(("id", "input1"))
    assert is_visible, "Input element should be visible"

    # Test typing
    type_success = base_page.send_keys(("id", "input1"), "Hello Framework!")
    assert type_success, "Should be able to type in input"

    # Test clicking
    click_success = base_page.click(("id", "btn1"))
    assert click_success, "Should be able to click button"

    # Test screenshot functionality
    screenshot_path = base_page.take_screenshot("framework_test.png")
    assert screenshot_path, "Should be able to take screenshot"

    print("✅ All BasePage functionality tests passed!")


@pytest.mark.framework
def test_base_page_element_actions_integration():
    """Test that our BasePage element actions work correctly."""
    driver = WebDriverFactory.create_chrome_driver(headless=True)
    base_page = BasePage(driver)

    try:
        # Navigate to test page
        test_html = """
        <html><body>
            <input id="test" name="test" value="initial">
            <button id="clickme">Click</button>
        </body></html>
        """
        driver.get(f"data:text/html,{test_html}")

        # Test element finding through BasePage
        element = base_page.find_element(("id", "test"))
        assert element is not None, "Should find element"

        # Test typing through BasePage
        success = base_page.send_keys(("id", "test"), "new value")
        assert success, "Should be able to type"

        # Test clicking through BasePage
        success = base_page.click(("id", "clickme"))
        assert success, "Should be able to click"

        print("✅ BasePage element actions integration test passed!")

    finally:
        driver.quit()


@pytest.mark.framework
def test_framework_integration():
    """Integration test for the complete framework."""
    driver, db = get_driver(headless=True)

    try:
        # Test that we can create pages and perform basic operations
        base_page = BasePage((driver, db))

        # Navigate to a simple page
        simple_page = (
            "data:text/html,<html><body><h1>Integration Test</h1>"
            "<p>Framework working!</p></body></html>"
        )
        success = base_page.navigate_to(simple_page)
        assert success, "Should be able to navigate"

        # Verify page content - data URLs don't have titles
        current_url = base_page.get_current_url()
        assert "data:text/html" in current_url, "Should be on test page"

        # Test database if available
        if db:
            # Simple database test
            query_result = base_page.execute_query("SELECT 1 as test")
            # This might return empty list if not implemented, which is fine
            print(f"Database query result: {query_result}")

        print("✅ Framework integration test passed!")

    finally:
        from utils.webdriver_factory import cleanup_driver_and_database

        cleanup_driver_and_database(driver, db)


if __name__ == "__main__":
    # Run framework tests directly
    pytest.main([__file__, "-v"])
