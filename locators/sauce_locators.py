"""
SauceDemo page locators - centralized locator management.
Locators for SauceDemo.com test site.
"""

from selenium.webdriver.common.by import By


class SauceLocators:
    """All locators for SauceDemo page in one place."""

    # Login page elements
    USERNAME_INPUT = (By.XPATH, '//input[@data-test="username"]')
    PASSWORD_INPUT = (By.XPATH, '//input[@data-test="password"]')
    LOGIN_BUTTON = (By.XPATH, '//input[@data-test="login-button"]')

    # Inventory page elements
    INVENTORY_LIST = (By.XPATH, '//div[@class="inventory_list"]')

    # Navigation elements
    LOGOUT_BUTTON = (By.XPATH, "//a[@id='logout_sidebar_link']")

    # Product buttons
    ADD_BACKPACK_BUTTON = (
        By.XPATH,
        '//button[@data-test="add-to-cart-sauce-labs-backpack"]',
    )
    ADD_BIKELIGHT_BUTTON = (
        By.XPATH,
        '//button[@data-test="add-to-cart-sauce-labs-bike-light"]',
    )
    ADD_SHIRT_BUTTON = (
        By.XPATH,
        '//button[@data-test="add-to-cart-sauce-labs-bolt-t-shirt"]',
    )

    # Cart elements
    CART_BADGE = (By.XPATH, '//span[@data-test="shopping-cart-badge"]')
