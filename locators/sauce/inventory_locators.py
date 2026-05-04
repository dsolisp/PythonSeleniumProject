"""Locators for the SauceDemo Inventory page."""

from selenium.webdriver.common.by import By


class InventoryLocators:
    """Locators mirroring InventoryPage 1:1 (Law 1)."""

    INVENTORY_LIST = (By.XPATH, '//div[@class="inventory_list"]')
    INVENTORY_ITEM = (By.XPATH, '//div[@class="inventory_item"]')
    INVENTORY_ITEM_NAME = (By.XPATH, '//div[@data-test="inventory-item-name"]')
    INVENTORY_ITEM_PRICE = (By.XPATH, '//div[@data-test="inventory-item-price"]')
    SORT_DROPDOWN = (By.XPATH, '//select[@data-test="product-sort-container"]')

    # Add-to-cart buttons
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
