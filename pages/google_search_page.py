from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from locators.google_search_locators import GoogleSearchLocators
from locators.google_result_locators import GoogleResultLocators


class GoogleSearchPage(BasePage):

    def capture_main_input_screenshot(self, output_path):
        element = self.wait_for_element(GoogleSearchLocators.main_search_input_screenshot)
        element.screenshot(output_path)

    def get_search_input(self):
        return self.driver.find_element(*GoogleSearchLocators.search_input)
