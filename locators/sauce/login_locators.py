"""Locators for the SauceDemo Login page."""

from selenium.webdriver.common.by import By


class LoginLocators:
    """Locators mirroring LoginPage 1:1 (Law 1)."""

    USERNAME_INPUT = (By.XPATH, '//input[@data-test="username"]')
    PASSWORD_INPUT = (By.XPATH, '//input[@data-test="password"]')
    LOGIN_BUTTON = (By.XPATH, '//input[@data-test="login-button"]')
    ERROR_MESSAGE = (By.XPATH, '//h3[@data-test="error"]')
