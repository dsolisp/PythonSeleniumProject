"""Checkout page object for SauceDemo (step-one and step-two)."""

from __future__ import annotations

from dataclasses import dataclass

from locators.sauce.checkout_locators import CheckoutLocators
from pages.base_page import BasePage


@dataclass
class CheckoutInfo:
    """Value object holding checkout form data (built by CheckoutBuilder)."""

    first_name: str
    last_name: str
    postal_code: str


class CheckoutPage(BasePage):
    """SauceDemo Checkout pages (step-one & step-two).

    Responsibilities: fill form, submit, read summary, confirm completion.
    No assertions (Law 2). Inherits BasePage only (Law 4).
    """

    def fill_info(self, info: CheckoutInfo) -> None:
        """Fill the step-one checkout form and click Continue."""
        self.send_keys(CheckoutLocators.FIRST_NAME_INPUT, info.first_name)
        self.send_keys(CheckoutLocators.LAST_NAME_INPUT, info.last_name)
        self.send_keys(CheckoutLocators.POSTAL_CODE_INPUT, info.postal_code)
        self.click(CheckoutLocators.CONTINUE_BUTTON)

    def get_order_total(self) -> str:
        """Return the order total label text from step-two summary."""
        total = self.wait_for_element(CheckoutLocators.SUMMARY_TOTAL)
        return total.text if total else ""

    def finish(self) -> None:
        """Click Finish to place the order."""
        self.click(CheckoutLocators.FINISH_BUTTON)

    def is_complete(self) -> bool:
        """Return True when the 'Thank you' confirmation header is visible."""
        header = self.wait_for_element(CheckoutLocators.CHECKOUT_COMPLETE_HEADER)
        return header is not None and "Thank you" in header.text

    def back_to_products(self) -> None:
        """Click Back Home after order confirmation."""
        self.click(CheckoutLocators.BACK_HOME_BUTTON)
