# locators/example_locator.py
from selenium.webdriver.common.by import By


class GoogleSearchLocators:
    main_search_input_screenshot = (By.XPATH, "//textarea[@name='q']/../../../../..")
    search_input = (By.NAME, 'q')