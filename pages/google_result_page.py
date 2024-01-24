from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from locators.google_result_locators import GoogleResultLocators


class GoogleResultPage(BasePage):
    # Locators

    def get_first_result(self):
        return self.driver.find_element(*GoogleResultLocators.result_h3_title)