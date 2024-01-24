# locators/example_locator.py
from selenium.webdriver.common.by import By


class GoogleResultLocators:
    result_h3_title = (By.XPATH, "//h3[.='Naruto - Wikipedia, la enciclopedia libre']")



