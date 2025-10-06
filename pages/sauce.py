from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from locators.sauce_locators import SauceLocators


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
            EC.presence_of_element_located(SauceLocators.USERNAME_INPUT)
        )
        password_input = self.driver.find_element(
            *SauceLocators.PASSWORD_INPUT
        )
        login_button = self.driver.find_element(*SauceLocators.LOGIN_BUTTON)
        username_input.send_keys(user)
        password_input.send_keys(password)
        login_button.click()

        # Wait for login to complete by checking inventory container appears
        wait.until(
            EC.presence_of_element_located(SauceLocators.INVENTORY_LIST)
        )

    def is_logged_in(self):
        """Check if user is logged in by verifying inventory page loaded."""
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located(SauceLocators.INVENTORY_LIST)
            )
            return True
        except Exception:
            return False

    def get_logout_button(self):
        return self.driver.find_elements(*SauceLocators.LOGOUT_BUTTON)

    def add_default_products_to_cart(self):
        wait = WebDriverWait(self.driver, 10)

        add_backpack_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_BACKPACK_BUTTON)
        )
        add_backpack_to_cart_button.click()

        add_bikelight_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_BIKELIGHT_BUTTON)
        )
        add_bikelight_to_cart_button.click()

        add_shirt_to_cart_button = wait.until(
            EC.element_to_be_clickable(SauceLocators.ADD_SHIRT_BUTTON)
        )
        add_shirt_to_cart_button.click()

    def get_cart_element(self):
        wait = WebDriverWait(self.driver, 10)
        return wait.until(
            EC.presence_of_element_located(SauceLocators.CART_BADGE)
        )
