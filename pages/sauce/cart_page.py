"""Cart page object for SauceDemo."""

from locators.sauce.cart_locators import CartLocators
from pages.base_page import BasePage


class CartPage(BasePage):
    """SauceDemo Cart page.

    Responsibilities: read cart state, remove items, navigate to checkout.
    No assertions (Law 2). Inherits BasePage only (Law 4).
    """

    def open(self) -> None:
        """Click the cart icon to navigate to the cart page."""
        self.click(CartLocators.CART_LINK)
        self.wait_for_element(CartLocators.CHECKOUT_BUTTON)

    def get_cart_badge_count(self) -> str:
        """Return the cart badge text (item count). Empty string if badge absent."""
        badge = self.wait_for_element(CartLocators.CART_BADGE)
        return badge.text if badge else ""

    def get_cart_badge_element(self):
        """Return the cart badge WebElement (for attribute assertions)."""
        return self.wait_for_element(CartLocators.CART_BADGE)

    def get_items(self) -> list:
        """Return list of cart item WebElements."""
        return self.find_elements(CartLocators.CART_ITEM)

    def remove_backpack(self) -> None:
        """Remove Sauce Labs Backpack from the cart."""
        self.click(CartLocators.REMOVE_BACKPACK_BUTTON)

    def proceed_to_checkout(self) -> None:
        """Click the Checkout button."""
        self.click(CartLocators.CHECKOUT_BUTTON)

    def continue_shopping(self) -> None:
        """Click Continue Shopping to return to inventory."""
        self.click(CartLocators.CONTINUE_SHOPPING_BUTTON)
