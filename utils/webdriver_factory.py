from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import utils.sql_connection as sql_util


def get_driver(browser='chrome'):
    if browser.lower() == 'chrome':
        chrome_driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        chrome_driver.maximize_window()
        chrome_driver.implicitly_wait(10)
        chrome_driver.get('https://www.google.com/')
        return chrome_driver, connect_to_db()
    elif browser.lower() == 'firefox':
        return webdriver.Firefox(), connect_to_db()
    else:
        raise ValueError(f"Unsupported browser: {browser}")


def connect_to_db():
    db_file = 'resources/chinook.db'
    return sql_util.get_connection(db_file)
