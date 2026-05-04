"""Sauce Demo page objects — one class per page."""

from pages.sauce.cart_page import CartPage
from pages.sauce.checkout_page import CheckoutPage
from pages.sauce.inventory_page import InventoryPage
from pages.sauce.login_page import LoginPage

__all__ = ["CartPage", "CheckoutPage", "InventoryPage", "LoginPage"]
