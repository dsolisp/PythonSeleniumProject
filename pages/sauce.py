from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locators.sauce_locators import SauceLocators
from pages.base_page import BasePage


class SaucePage(BasePage):
    def open(self):
        """Navigate to SauceDemo website."""
        self.navigate_to("https://www.saucedemo.com/")
        return True

    def fill_login_input(self):
        user = "standard_user"
        password = "secret_sauce"
        wait = WebDriverWait(self.driver, 10)

        username_input = wait.until(
            EC.presence_of_element_located(SauceLocators.USERNAME_INPUT),
        )
        password_input = self.driver.find_element(*SauceLocators.PASSWORD_INPUT)
        login_button = self.driver.find_element(*SauceLocators.LOGIN_BUTTON)
        username_input.send_keys(user)
        password_input.send_keys(password)
        login_button.click()

        # Wait for login to complete by checking inventory container appears
        wait.until(EC.presence_of_element_located(SauceLocators.INVENTORY_LIST))

    def is_logged_in(self):
        """Check if user is logged in by verifying inventory page loaded."""
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located(SauceLocators.INVENTORY_LIST))
        except TimeoutException:
            return False
        else:
            return True

    def get_logout_button(self):
        return self.driver.find_elements(*SauceLocators.LOGOUT_BUTTON)

    def add_default_products_to_cart(self):
        wait = WebDriverWait(self.driver, 10)

        add_backpack_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_BACKPACK_BUTTON),
        )
        add_backpack_to_cart_button.click()

        add_bikelight_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_BIKELIGHT_BUTTON),
        )
        add_bikelight_to_cart_button.click()

        add_shirt_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_SHIRT_BUTTON),
        )
        add_shirt_to_cart_button.click()

    def get_cart_element(self):
        wait = WebDriverWait(self.driver, 10)
        return wait.until(EC.presence_of_element_located(SauceLocators.CART_BADGE))

    def get_inventory_items(self):
        """Get all inventory items on the page."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located(SauceLocators.INVENTORY_ITEM))
        return self.driver.find_elements(*SauceLocators.INVENTORY_ITEM)

    def get_inventory_item_names(self):
        """Get all inventory item names."""
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located(SauceLocators.INVENTORY_ITEM))
        items = self.driver.find_elements(*SauceLocators.INVENTORY_ITEM_NAME)
        return [item.text for item in items]

    def get_inventory_item_prices(self):
        """Get all inventory item prices."""
        items = self.driver.find_elements(*SauceLocators.INVENTORY_ITEM_PRICE)
        return [item.text for item in items]

    def go_to_cart(self):
        """Navigate to cart page."""
        wait = WebDriverWait(self.driver, 10)
        cart_link = wait.until(EC.element_to_be_clickable(SauceLocators.CART_LINK))
        cart_link.click()
        wait.until(EC.presence_of_element_located(SauceLocators.CHECKOUT_BUTTON))

    def get_cart_items(self):
        """Get all items in cart."""
        return self.driver.find_elements(*SauceLocators.CART_ITEM)

    def remove_item_from_cart(self):
        """Remove backpack from cart."""
        wait = WebDriverWait(self.driver, 10)
        remove_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.REMOVE_BACKPACK_BUTTON)
        )
        remove_button.click()

    def proceed_to_checkout(self):
        """Click checkout button."""
        wait = WebDriverWait(self.driver, 10)
        checkout_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.CHECKOUT_BUTTON)
        )
        checkout_button.click()

    def fill_checkout_info(self, first_name="Test", last_name="User", postal_code="12345"):
        """Fill checkout information form."""
        wait = WebDriverWait(self.driver, 10)

        first_name_input = wait.until(
            EC.presence_of_element_located(SauceLocators.FIRST_NAME_INPUT)
        )
        first_name_input.send_keys(first_name)

        last_name_input = self.driver.find_element(*SauceLocators.LAST_NAME_INPUT)
        last_name_input.send_keys(last_name)

        postal_code_input = self.driver.find_element(*SauceLocators.POSTAL_CODE_INPUT)
        postal_code_input.send_keys(postal_code)

        continue_button = self.driver.find_element(*SauceLocators.CONTINUE_BUTTON)
        continue_button.click()

    def complete_checkout(self):
        """Click finish button to complete checkout."""
        wait = WebDriverWait(self.driver, 10)
        finish_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.FINISH_BUTTON)
        )
        finish_button.click()

    def is_checkout_complete(self):
        """Check if checkout was completed successfully."""
        try:
            wait = WebDriverWait(self.driver, 10)
            header = wait.until(
                EC.presence_of_element_located(SauceLocators.CHECKOUT_COMPLETE_HEADER)
            )
            return "Thank you" in header.text
        except TimeoutException:
            return False

    def get_order_total(self):
        """Get the order total from checkout summary."""
        wait = WebDriverWait(self.driver, 10)
        total = wait.until(
            EC.presence_of_element_located(SauceLocators.SUMMARY_TOTAL)
        )
        return total.text

    def sort_products(self, sort_option):
        """Sort products by given option."""
        from selenium.webdriver.support.ui import Select
        wait = WebDriverWait(self.driver, 10)
        dropdown = wait.until(
            EC.presence_of_element_located(SauceLocators.SORT_DROPDOWN)
        )
        select = Select(dropdown)
        select.select_by_value(sort_option)

    def login_with_credentials(self, username, password):
        """Login with specific credentials."""
        wait = WebDriverWait(self.driver, 10)

        username_input = wait.until(
            EC.presence_of_element_located(SauceLocators.USERNAME_INPUT)
        )
        username_input.clear()
        username_input.send_keys(username)

        password_input = self.driver.find_element(*SauceLocators.PASSWORD_INPUT)
        password_input.clear()
        password_input.send_keys(password)

        login_button = self.driver.find_element(*SauceLocators.LOGIN_BUTTON)
        login_button.click()

    def get_error_message(self):
        """Get error message if present."""
        try:
            wait = WebDriverWait(self.driver, 5)
            error = wait.until(
                EC.presence_of_element_located(SauceLocators.ERROR_MESSAGE)
            )
            return error.text
        except TimeoutException:
            return None
