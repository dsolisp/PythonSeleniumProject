"""
SauceDemo E2E Tests.
Comprehensive tests for login, inventory, cart, and checkout functionality.
"""

import pytest
from hamcrest import assert_that, contains_string, equal_to, greater_than, is_

from pages.sauce import SaucePage


@pytest.mark.web
class TestSauceDemoLogin:
    """Login functionality tests."""

    def test_standard_user_login(self, driver):
        """Test that standard user can login successfully."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()

        assert_that(sauce_page.is_logged_in(), is_(True))
        print("✅ Standard user login successful")

    def test_locked_out_user_login(self, driver):
        """Test that locked out user cannot login."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.login_with_credentials("locked_out_user", "secret_sauce")

        error = sauce_page.get_error_message()
        assert_that(error, contains_string("locked out"))
        print("✅ Locked out user correctly rejected")

    def test_invalid_credentials_login(self, driver):
        """Test that invalid credentials show error."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.login_with_credentials("invalid_user", "wrong_password")

        error = sauce_page.get_error_message()
        assert_that(error is not None, is_(True))
        print("✅ Invalid credentials correctly rejected")


@pytest.mark.web
class TestSauceDemoInventory:
    """Inventory page tests."""

    def test_inventory_displays_products(self, driver):
        """Test that inventory page displays products."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()

        items = sauce_page.get_inventory_items()
        assert_that(len(items), greater_than(0))
        print(f"✅ Found {len(items)} inventory items")

    def test_inventory_item_names(self, driver):
        """Test that inventory items have names."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()

        names = sauce_page.get_inventory_item_names()
        assert_that(len(names), equal_to(6))
        assert_that("Sauce Labs Backpack" in names, is_(True))
        print(f"✅ Inventory items: {names}")

    def test_inventory_item_prices(self, driver):
        """Test that inventory items have prices."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()

        prices = sauce_page.get_inventory_item_prices()
        assert_that(len(prices), greater_than(0))
        assert_that(all("$" in p for p in prices), is_(True))
        print(f"✅ Prices found: {prices}")

    def test_sort_products_by_price_low_to_high(self, driver):
        """Test sorting products by price low to high."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()

        sauce_page.sort_products("lohi")
        prices = sauce_page.get_inventory_item_prices()

        # Extract numeric values
        numeric_prices = [float(p.replace("$", "")) for p in prices]
        assert_that(numeric_prices, equal_to(sorted(numeric_prices)))
        print("✅ Products sorted by price low to high")


@pytest.mark.web
class TestSauceDemoCart:
    """Cart functionality tests."""

    def test_add_items_to_cart(self, driver):
        """Test adding items to cart."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()
        sauce_page.add_default_products_to_cart()

        cart_element = sauce_page.get_cart_element()
        assert_that(cart_element.text, equal_to("3"))
        print("✅ Added 3 items to cart")

    def test_view_cart_items(self, driver):
        """Test viewing items in cart."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()
        sauce_page.add_default_products_to_cart()
        sauce_page.go_to_cart()

        cart_items = sauce_page.get_cart_items()
        assert_that(len(cart_items), equal_to(3))
        print(f"✅ Cart contains {len(cart_items)} items")

    def test_remove_item_from_cart(self, driver):
        """Test removing item from cart."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()
        sauce_page.add_default_products_to_cart()
        sauce_page.go_to_cart()
        sauce_page.remove_item_from_cart()

        cart_items = sauce_page.get_cart_items()
        assert_that(len(cart_items), equal_to(2))
        print("✅ Removed item from cart")


@pytest.mark.web
class TestSauceDemoCheckout:
    """Checkout functionality tests."""

    def test_complete_checkout_flow(self, driver):
        """Test complete checkout flow."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()
        sauce_page.add_default_products_to_cart()
        sauce_page.go_to_cart()
        sauce_page.proceed_to_checkout()
        sauce_page.fill_checkout_info("Test", "User", "12345")
        sauce_page.complete_checkout()

        assert_that(sauce_page.is_checkout_complete(), is_(True))
        print("✅ Checkout completed successfully")

    def test_checkout_displays_total(self, driver):
        """Test that checkout displays order total."""
        sauce_page = SaucePage(driver[0])
        sauce_page.open()
        sauce_page.fill_login_input()
        sauce_page.add_default_products_to_cart()
        sauce_page.go_to_cart()
        sauce_page.proceed_to_checkout()
        sauce_page.fill_checkout_info()

        total = sauce_page.get_order_total()
        assert_that("$" in total, is_(True))
        print(f"✅ Order total: {total}")
