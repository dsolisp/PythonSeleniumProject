import json
from pathlib import Path

from selenium.webdriver.support.ui import Select

from locators.sauce_locators import SauceLocators
from pages.base_page import BasePage

# Load credentials from data file
_CREDENTIALS_FILE = Path(__file__).parent.parent / "data" / "test_credentials.json"
_CREDENTIALS = {}
if _CREDENTIALS_FILE.exists():
    with open(_CREDENTIALS_FILE) as f:
        _CREDENTIALS = json.load(f).get("saucedemo", {})


class SaucePage(BasePage):
    """SauceDemo page using BasePage methods exclusively."""

    def open(self):
        """Navigate to SauceDemo website."""
        self.navigate_to("https://www.saucedemo.com/")
        return True

    def fill_login_input(self, user_type: str = "standard_user"):
        """Fill login form with credentials from data file."""
        creds = _CREDENTIALS.get(user_type, _CREDENTIALS.get("standard_user", {}))
        username = creds.get("username", "standard_user")
        password = creds.get("password", "secret_sauce")

        self.send_keys(SauceLocators.USERNAME_INPUT, username)
        self.send_keys(SauceLocators.PASSWORD_INPUT, password)
        self.click(SauceLocators.LOGIN_BUTTON)
        self.wait_for_element(SauceLocators.INVENTORY_LIST)

    def is_logged_in(self):
        """Check if user is logged in by verifying inventory page loaded."""
        return self.wait_for_element(SauceLocators.INVENTORY_LIST) is not None

    def get_logout_button(self):
        """Get logout button elements."""
        return self.find_elements(SauceLocators.LOGOUT_BUTTON)

    def add_default_products_to_cart(self):
        """Add default products to cart."""
        self.click(SauceLocators.ADD_BACKPACK_BUTTON)
        self.click(SauceLocators.ADD_BIKELIGHT_BUTTON)
        self.click(SauceLocators.ADD_SHIRT_BUTTON)

    def get_cart_element(self):
        """Get cart badge element."""
        return self.wait_for_element(SauceLocators.CART_BADGE)

    def get_inventory_items(self):
        """Get all inventory items on the page."""
        self.wait_for_element(SauceLocators.INVENTORY_ITEM)
        return self.find_elements(SauceLocators.INVENTORY_ITEM)

    def get_inventory_item_names(self):
        """Get all inventory item names."""
        self.wait_for_element(SauceLocators.INVENTORY_ITEM)
        items = self.find_elements(SauceLocators.INVENTORY_ITEM_NAME)
        return [item.text for item in items]

    def get_inventory_item_prices(self):
        """Get all inventory item prices."""
        items = self.find_elements(SauceLocators.INVENTORY_ITEM_PRICE)
        return [item.text for item in items]

    def go_to_cart(self):
        """Navigate to cart page."""
        self.click(SauceLocators.CART_LINK)
        self.wait_for_element(SauceLocators.CHECKOUT_BUTTON)

    def get_cart_items(self):
        """Get all items in cart."""
        return self.find_elements(SauceLocators.CART_ITEM)

    def remove_item_from_cart(self):
        """Remove backpack from cart."""
        self.click(SauceLocators.REMOVE_BACKPACK_BUTTON)

    def proceed_to_checkout(self):
        """Click checkout button."""
        self.click(SauceLocators.CHECKOUT_BUTTON)

    def fill_checkout_info(
        self, first_name="Test", last_name="User", postal_code="12345"
    ):
        """Fill checkout information form."""
        self.send_keys(SauceLocators.FIRST_NAME_INPUT, first_name)
        self.send_keys(SauceLocators.LAST_NAME_INPUT, last_name)
        self.send_keys(SauceLocators.POSTAL_CODE_INPUT, postal_code)
        self.click(SauceLocators.CONTINUE_BUTTON)

    def complete_checkout(self):
        """Click finish button to complete checkout."""
        self.click(SauceLocators.FINISH_BUTTON)

    def is_checkout_complete(self):
        """Check if checkout was completed successfully."""
        header = self.wait_for_element(SauceLocators.CHECKOUT_COMPLETE_HEADER)
        return header is not None and "Thank you" in header.text

    def get_order_total(self):
        """Get the order total from checkout summary."""
        total = self.wait_for_element(SauceLocators.SUMMARY_TOTAL)
        return total.text if total else ""

    def sort_products(self, sort_option):
        """Sort products by given option."""
        dropdown = self.wait_for_element(SauceLocators.SORT_DROPDOWN)
        if dropdown:
            select = Select(dropdown)
            select.select_by_value(sort_option)

    def login_with_credentials(self, username, password):
        """Login with specific credentials."""
        self.send_keys(SauceLocators.USERNAME_INPUT, username, clear_first=True)
        self.send_keys(SauceLocators.PASSWORD_INPUT, password, clear_first=True)
        self.click(SauceLocators.LOGIN_BUTTON)

    def get_error_message(self):
        """Get error message if present."""
        error = self.wait_for_element(SauceLocators.ERROR_MESSAGE)
        return error.text if error else None
