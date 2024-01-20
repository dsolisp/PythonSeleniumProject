from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def get_driver(browser='chrome'):
    if browser.lower() == 'chrome':
        chrome_driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        chrome_driver.maximize_window()
        return chrome_driver
    elif browser.lower() == 'firefox':
        return webdriver.Firefox()
    else:
        raise ValueError(f"Unsupported browser: {browser}")
