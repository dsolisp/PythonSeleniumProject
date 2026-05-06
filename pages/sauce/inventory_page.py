"""Inventory page object for SauceDemo."""

from __future__ import annotations

from selenium.webdriver.support.ui import Select

from config.constants import URLS
from locators.sauce.inventory_locators import InventoryLocators
from pages.base_page import BasePage


class InventoryPage(BasePage):
    """SauceDemo Inventory page.

    Responsibilities: read product list, sort, add items to cart.
    No assertions (Law 2). Inherits BasePage only (Law 4).
    """

    def open(self) -> InventoryPage:
        """Navigate to the inventory page and return self for chaining."""
        self.navigate_to(f"{URLS.SAUCE_DEMO}/inventory.html")
        return self

    def is_loaded(self) -> bool:
        """Return True when the inventory list is visible."""
        return self.wait_for_element(InventoryLocators.INVENTORY_LIST) is not None

    def get_items(self) -> list:
        """Return list of inventory item WebElements."""
        self.wait_for_element(InventoryLocators.INVENTORY_ITEM)
        return self.find_elements(InventoryLocators.INVENTORY_ITEM)

    def get_item_names(self) -> list[str]:
        """Return list of visible product name strings."""
        self.wait_for_element(InventoryLocators.INVENTORY_ITEM)
        return [
            el.text for el in self.find_elements(InventoryLocators.INVENTORY_ITEM_NAME)
        ]

    def get_item_prices(self) -> list[str]:
        """Return list of visible price strings (e.g. '$29.99')."""
        self.wait_for_element(InventoryLocators.INVENTORY_ITEM_PRICE)
        return [
            el.text for el in self.find_elements(InventoryLocators.INVENTORY_ITEM_PRICE)
        ]

    def sort_by(self, value: str) -> None:
        """Select sort option by value (e.g. 'lohi', 'hilo', 'az', 'za')."""
        dropdown = self.wait_for_element(InventoryLocators.SORT_DROPDOWN)
        if dropdown:
            Select(dropdown).select_by_value(value)

    def add_backpack(self) -> None:
        """Add Sauce Labs Backpack to cart."""
        self.click(InventoryLocators.ADD_BACKPACK_BUTTON)

    def add_bike_light(self) -> None:
        """Add Sauce Labs Bike Light to cart."""
        self.click(InventoryLocators.ADD_BIKELIGHT_BUTTON)

    def add_bolt_shirt(self) -> None:
        """Add Sauce Labs Bolt T-Shirt to cart."""
        self.click(InventoryLocators.ADD_SHIRT_BUTTON)

    def add_default_items(self) -> None:
        """Add the three default items used across most cart/checkout tests."""
        self.add_backpack()
        self.add_bike_light()
        self.add_bolt_shirt()
