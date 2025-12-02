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
    CART_LINK = (By.XPATH, '//a[@class="shopping_cart_link"]')
    CART_ITEM = (By.XPATH, '//div[@class="cart_item"]')
    CART_ITEM_NAME = (By.XPATH, '//div[@class="inventory_item_name"]')
    REMOVE_BACKPACK_BUTTON = (By.XPATH, '//button[@data-test="remove-sauce-labs-backpack"]')

    # Checkout elements
    CHECKOUT_BUTTON = (By.XPATH, '//button[@data-test="checkout"]')
    CONTINUE_SHOPPING_BUTTON = (By.XPATH, '//button[@data-test="continue-shopping"]')
    FIRST_NAME_INPUT = (By.XPATH, '//input[@data-test="firstName"]')
    LAST_NAME_INPUT = (By.XPATH, '//input[@data-test="lastName"]')
    POSTAL_CODE_INPUT = (By.XPATH, '//input[@data-test="postalCode"]')
    CONTINUE_BUTTON = (By.XPATH, '//input[@data-test="continue"]')
    FINISH_BUTTON = (By.XPATH, '//button[@data-test="finish"]')
    BACK_HOME_BUTTON = (By.XPATH, '//button[@data-test="back-to-products"]')

    # Checkout confirmation
    CHECKOUT_COMPLETE_HEADER = (By.XPATH, '//h2[@class="complete-header"]')
    SUMMARY_TOTAL = (By.XPATH, '//div[@class="summary_total_label"]')

    # Inventory page
    INVENTORY_ITEM = (By.XPATH, '//div[@class="inventory_item"]')
    INVENTORY_ITEM_NAME = (By.XPATH, '//div[@data-test="inventory-item-name"]')
    INVENTORY_ITEM_PRICE = (By.XPATH, '//div[@data-test="inventory-item-price"]')
    SORT_DROPDOWN = (By.XPATH, '//select[@data-test="product-sort-container"]')

    # Menu elements
    MENU_BUTTON = (By.XPATH, '//button[@id="react-burgerMenu-btn"]')
    MENU_CLOSE_BUTTON = (By.XPATH, '//button[@id="react-burger-cross-btn"]')

    # Error messages
    ERROR_MESSAGE = (By.XPATH, '//h3[@data-test="error"]')
