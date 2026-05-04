"""Locators for the SauceDemo Header component (burger menu + cart icon)."""

from selenium.webdriver.common.by import By


class HeaderLocators:
    """Locators mirroring HeaderComponent 1:1 (Law 1)."""

    MENU_BUTTON = (By.XPATH, '//button[@id="react-burger-menu-btn"]')
    MENU_CLOSE_BUTTON = (By.XPATH, '//button[@id="react-burger-cross-btn"]')
    LOGOUT_LINK = (By.XPATH, "//a[@id='logout_sidebar_link']")
    CART_LINK = (By.XPATH, '//a[@class="shopping_cart_link"]')
    CART_BADGE = (By.XPATH, '//span[@data-test="shopping-cart-badge"]')
