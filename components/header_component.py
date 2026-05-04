"""HeaderComponent — SauceDemo persistent header (burger menu + cart icon)."""

from components.base_component import BaseComponent
from locators.components.header_locators import HeaderLocators


class HeaderComponent(BaseComponent):
    """Models the SauceDemo app header present on all post-login pages.

    Composed into pages that need header interactions; never inherited.
    """

    def open_menu(self) -> None:
        """Open the burger side-menu."""
        self._click(HeaderLocators.MENU_BUTTON)

    def close_menu(self) -> None:
        """Close the burger side-menu."""
        self._click(HeaderLocators.MENU_CLOSE_BUTTON)

    def logout(self) -> None:
        """Open menu and click Logout link."""
        self.open_menu()
        self._click(HeaderLocators.LOGOUT_LINK)

    def go_to_cart(self) -> None:
        """Click the shopping cart icon."""
        self._click(HeaderLocators.CART_LINK)

    def get_cart_badge_count(self) -> str:
        """Return the cart badge text (item count); empty string when absent."""
        if not self._is_visible(HeaderLocators.CART_BADGE):
            return ""
        badge = self._find(HeaderLocators.CART_BADGE)
        return badge.text
