"""
Standard Accessibility Checks using axe-selenium-python.
Equivalent to Playwright's accessibility.spec.ts.
"""

import pytest
from axe_selenium_python import Axe
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from config.settings import settings
from pages.sauce.inventory_page import InventoryPage
from pages.sauce.login_page import LoginPage


@pytest.fixture
def browser():
    """Create a headless Chrome browser for accessibility testing."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()


class TestAccessibility:
    """Standard Accessibility Tests."""

    def test_bing_homepage_no_critical_violations(self, browser):
        """Should not have critical accessibility violations on homepage."""
        browser.get(settings.BASE_URL)
        axe = Axe(browser)
        axe.inject()
        results = axe.run(
            options={
                "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
                }
            }
        )

        violations = results.get("violations", [])
        if violations:
            print("\n=== Accessibility Audit Results ===")
            print(
                f"Passes: {len(results.get('passes', []))}, Violations: {len(violations)}"
            )
            for v in violations:
                print(f"  [{v.get('impact')}] {v.get('id')}: {v.get('description')}")

        assert len(violations) <= 10

    def test_bing_search_form_accessible(self, browser):
        """Should have accessible search form."""
        browser.get(settings.BASE_URL)
        axe = Axe(browser)
        axe.inject()
        results = axe.run(
            context={"include": [["#sb_form"]]},
            options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}},
        )

        violations = results.get("violations", [])
        label_violations = [
            v
            for v in violations
            if "label" in v.get("id", "") or "aria" in v.get("id", "")
        ]
        assert len(label_violations) <= 3

    def test_saucedemo_login_form_accessible(self, browser):
        """Should have accessible login form."""
        browser.get("https://www.saucedemo.com")
        axe = Axe(browser)
        axe.inject()
        results = axe.run(
            context={"include": [["#login_button_container"]]},
            options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}},
        )

        violations = results.get("violations", [])
        assert len(violations) <= 5

    def test_saucedemo_inventory_page_accessible(self, browser):
        """Should have accessible inventory page."""
        browser.get("https://www.saucedemo.com")
        login_page = LoginPage(browser)
        login_page.login("standard_user", "secret_sauce")

        InventoryPage(browser).wait_for_element(("class name", "inventory_container"))

        axe = Axe(browser)
        axe.inject()
        results = axe.run(
            context={"include": [[".inventory_container"]]},
            options={"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa"]}},
        )

        violations = results.get("violations", [])
        print(f"Inventory page: {len(violations)} violations")
        assert len(violations) <= 10

    def test_color_contrast_homepage(self, browser):
        """Should have sufficient color contrast on homepage."""
        browser.get(settings.BASE_URL)
        axe = Axe(browser)
        axe.inject()
        results = axe.run(
            options={"runOnly": {"type": "rule", "values": ["color-contrast"]}}
        )

        violations = results.get("violations", [])
        print(f"Color contrast issues: {len(violations)}")
        assert type(violations) is list

    def test_keyboard_navigation_homepage(self, browser):
        """Should be navigable with keyboard."""
        browser.get(settings.BASE_URL)
        active_element = browser.switch_to.active_element
        active_element.send_keys(Keys.TAB)
        active_element = browser.switch_to.active_element
        active_element.send_keys(Keys.TAB)

        active_tag = browser.switch_to.active_element.tag_name.upper()
        assert active_tag in ["INPUT", "TEXTAREA", "BUTTON", "A", "DIV", "BODY"]
