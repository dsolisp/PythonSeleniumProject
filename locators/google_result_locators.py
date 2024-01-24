# locators/example_locator.py
from selenium.webdriver.common.by import By


class GoogleResultLocators:
    resultByName = "//h3[.='{}']"
    resultByIndex = "(//h3)[{}]"

    def get_result_by_index(self, index):
        return By.XPATH, self.resultByIndex.format(index)

    def get_result_by_name(self, name):
        return By.XPATH, self.resultByName.format(name)
