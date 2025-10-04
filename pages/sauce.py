from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class SaucePage(BasePage):

    def fill_login_input(self):
        user = "standard_user"
        password = "secret_sauce"
        wait = WebDriverWait(self.driver, 10)

        username_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//input[@data-test="username"]')
            )
        )
        password_input = self.driver.find_element(
            By.XPATH, '//input[@data-test="password"]'
        )
        login_button = self.driver.find_element(
            By.XPATH, '//input[@data-test="login-button"]'
        )
        username_input.send_keys(user)
        password_input.send_keys(password)
        login_button.click()

        # Wait for login to complete by checking inventory container appears
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="inventory_list"]')
            )
        )

    def is_logged_in(self):
        """Check if user is logged in by verifying inventory page loaded."""
        try:
            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="inventory_list"]')
                )
            )
            return True
        except Exception:
            return False

    def get_logout_button(self):
        return self.driver.find_elements(
            By.XPATH, "//a[@id='logout_sidebar_link']"
        )

    def add_default_products_to_cart(self):
        wait = WebDriverWait(self.driver, 10)

        add_backpack_to_cart_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-test="add-to-cart-sauce-labs-backpack"]')
            )
        )
        add_backpack_to_cart_button.click()

        add_bikelight_to_cart_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[@data-test="add-to-cart-sauce-labs-bike-light"]',
                )
            )
        )
        add_bikelight_to_cart_button.click()

        add_shirt_to_cart_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[@data-test="add-to-cart-sauce-labs-bolt-t-shirt"]',
                )
            )
        )
        add_shirt_to_cart_button.click()

    def get_cart_element(self):
        wait = WebDriverWait(self.driver, 10)
        return wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@data-test="shopping-cart-badge"]')
            )
        )


