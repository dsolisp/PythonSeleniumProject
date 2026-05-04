"""
SauceDemo E2E Tests — Gold Standard refactor (Phase 3).

Architecture:
- Uses split page objects: LoginPage / InventoryPage / CartPage / CheckoutPage
- Builders: UserBuilder for credentials, CheckoutBuilder for form data
- selenium_driver fixture: function-scoped, returns WebDriver directly
- authenticated_driver fixture: session-scoped, reuses auth state (ADR-009)
"""

import pytest
from hamcrest import assert_that, contains_string, equal_to, greater_than, has_item, is_

from pages.sauce.cart_page import CartPage
from pages.sauce.checkout_page import CheckoutPage
from pages.sauce.inventory_page import InventoryPage
from pages.sauce.login_page import LoginPage
from utils.builders.checkout_builder import CheckoutBuilder
from utils.builders.user_builder import UserBuilder

# ── Login tests ───────────────────────────────────────────────────────────────


@pytest.mark.web
@pytest.mark.sauce
class TestSauceDemoLogin:
    """Login page — credential validation and error handling."""

    def test_standard_user_login(self, selenium_driver):
        """should login with valid credentials"""
        creds = UserBuilder().standard().build()
        login = LoginPage(selenium_driver).open()
        login.login(creds.username, creds.password)
        assert_that(login.is_logged_in(), is_(True))

    def test_locked_out_user_is_rejected(self, selenium_driver):
        """should show error for locked out user"""
        creds = UserBuilder().locked_out().build()
        login = LoginPage(selenium_driver).open()
        login.login(creds.username, creds.password)
        error = login.get_error_message()
        assert_that(error, contains_string("locked out"))

    def test_invalid_credentials_show_error(self, selenium_driver):
        """should show error for invalid credentials"""
        creds = UserBuilder().with_username("bad_user").with_password("bad_pass").build()
        login = LoginPage(selenium_driver).open()
        login.login(creds.username, creds.password)
        error = login.get_error_message()
        assert_that(error, contains_string("do not match"))

    def test_empty_username_shows_error(self, selenium_driver):
        """should show error for empty username"""
        login = LoginPage(selenium_driver).open()
        login.login("", "secret_sauce")
        error = login.get_error_message()
        assert_that(error, contains_string("Username is required"))

    def test_empty_password_shows_error(self, selenium_driver):
        """should show error for empty password"""
        creds = UserBuilder().standard().build()
        login = LoginPage(selenium_driver).open()
        login.login(creds.username, "")
        error = login.get_error_message()
        assert_that(error, contains_string("Password is required"))


# ── Inventory tests ───────────────────────────────────────────────────────────


@pytest.mark.web
@pytest.mark.sauce
class TestSauceDemoInventory:
    """Inventory page — product listing and sort."""

    def test_inventory_displays_six_products(self, authenticated_driver):
        """should display 6 products"""
        inventory = InventoryPage(authenticated_driver)
        items = inventory.get_items()
        assert_that(len(items), equal_to(6))

    def test_inventory_displays_product_names(self, authenticated_driver):
        """should display product names"""
        inventory = InventoryPage(authenticated_driver)
        names = inventory.get_item_names()
        assert_that(len(names), equal_to(6))

    def test_add_item_to_cart_updates_badge(self, authenticated_driver):
        """should add item to cart and update badge"""
        inventory = InventoryPage(authenticated_driver)
        inventory.add_backpack()
        cart = CartPage(authenticated_driver)
        assert_that(cart.get_cart_badge_count(), equal_to("1"))

    def test_add_multiple_items_to_cart(self, authenticated_driver):
        """should add multiple items to cart"""
        inventory = InventoryPage(authenticated_driver)
        inventory.add_backpack()
        inventory.add_bike_light()
        cart = CartPage(authenticated_driver)
        assert_that(cart.get_cart_badge_count(), equal_to("2"))

    def test_sort_products_by_name_az(self, authenticated_driver):
        """should sort products by name A-Z"""
        inventory = InventoryPage(authenticated_driver)
        inventory.sort_by("az")
        names = inventory.get_item_names()
        assert_that(names, equal_to(sorted(names)))

    def test_sort_products_by_price_low_to_high(self, authenticated_driver):
        """should sort products by price low to high"""
        inventory = InventoryPage(authenticated_driver)
        inventory.sort_by("lohi")
        prices = inventory.get_item_prices()
        numeric = [float(p.replace("$", "")) for p in prices]
        assert_that(numeric, equal_to(sorted(numeric)))


# ── Checkout tests ────────────────────────────────────────────────────────────


@pytest.mark.web
@pytest.mark.sauce
class TestSauceDemoCheckout:
    """Checkout pages — form submission and order confirmation."""

    def test_complete_full_checkout_flow(self, authenticated_driver):
        """should complete full checkout flow"""
        info = CheckoutBuilder().build()

        # Add item and go to cart
        inventory = InventoryPage(authenticated_driver)
        inventory.add_backpack()
        inventory.go_to_cart()

        # Verify cart
        cart = CartPage(authenticated_driver)
        items = cart.get_items()
        assert_that(len(items), equal_to(1))

        # Checkout
        cart.proceed_to_checkout()
        checkout = CheckoutPage(authenticated_driver)
        checkout.fill_info(info)
        checkout.finish()

        # Verify completion
        assert_that(checkout.is_complete(), is_(True))

    def test_allow_removing_item_from_cart(self, authenticated_driver):
        """should allow removing item from cart"""
        # Add item and go to cart
        inventory = InventoryPage(authenticated_driver)
        inventory.add_backpack()
        inventory.go_to_cart()

        # Verify cart has 1 item
        cart = CartPage(authenticated_driver)
        items = cart.get_items()
        assert_that(len(items), equal_to(1))

        # Remove item
        cart.remove_backpack()

        # Verify cart is empty
        items = cart.get_items()
        assert_that(len(items), equal_to(0))
