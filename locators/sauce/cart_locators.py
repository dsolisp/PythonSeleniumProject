"""Locators for the SauceDemo Cart page."""

from selenium.webdriver.common.by import By


class CartLocators:
    """Locators mirroring CartPage 1:1 (Law 1)."""

    CART_BADGE = (By.XPATH, '//span[@data-test="shopping-cart-badge"]')
    CART_LINK = (By.XPATH, '//a[@class="shopping_cart_link"]')
    CART_ITEM = (By.XPATH, '//div[@class="cart_item"]')
    CART_ITEM_NAME = (By.XPATH, '//div[@class="inventory_item_name"]')
    REMOVE_BACKPACK_BUTTON = (
        By.XPATH,
        '//button[@data-test="remove-sauce-labs-backpack"]',
    )
    CONTINUE_SHOPPING_BUTTON = (By.XPATH, '//button[@data-test="continue-shopping"]')
    CHECKOUT_BUTTON = (By.XPATH, '//button[@data-test="checkout"]')
