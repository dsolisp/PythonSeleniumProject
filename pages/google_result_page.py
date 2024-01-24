from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from locators.google_result_locators import GoogleResultLocators


class GoogleResultPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        self.google_result_locators = GoogleResultLocators()
    # Locators

    def get_result_by_name(self, name):
        return self.driver.find_element(*self.google_result_locators.get_result_by_name(name))

    def get_result_by_index(self, index):
        return self.driver.find_element(*self.google_result_locators.get_result_by_index(index))