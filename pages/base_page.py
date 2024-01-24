from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def refresh_page(self):
        self.driver.refresh()

    def get_title(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: driver.title != "")
            return self.driver.title  # Title exists within timeout
        except TimeoutException:
            return False