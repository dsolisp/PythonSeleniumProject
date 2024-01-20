from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    # Locators
    USERNAME_INPUT = (By.ID, 'username')
    PASSWORD_INPUT = (By.ID, 'password')
    LOGIN_BUTTON = (By.ID, 'login-button')
    # Locators
    ELEMENT_TO_CAPTURE = (By.XPATH, "//textarea[@name='q']/../../../../..")

    def capture_element_screenshot(self, output_path):
        element = self.wait_for_element(self.ELEMENT_TO_CAPTURE)
        element.screenshot(output_path)

    def refresh_page(self):
        self.driver.refresh()

    def get_search_input(self):
        return self.driver.find_element(By.NAME, 'q')

    def get_first_result(self):
        return self.driver.find_element(By.XPATH, "//h3[.='Naruto - Wikipedia, la enciclopedia libre']")

    def get_title(self):
        return self.driver.title

    def enter_username(self, username):
        self.driver.find_element(*self.USERNAME_INPUT).send_keys(username)

    def enter_password(self, password):
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)

    def click_login_button(self):
        self.driver.find_element(*self.LOGIN_BUTTON).click()