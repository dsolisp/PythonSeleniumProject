"""BaseComponent — root for all reusable UI components (ADR-005)."""

import logging

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.constants import TIMEOUTS

class BaseComponent:
    """Thin wrapper around a shared WebDriver instance.

    Components are *composed into* pages, never inherited from.
    They own their own locators and expose only domain-level methods.
    """

    def __init__(self, driver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUTS.DEFAULT / 1000)
        self.logger = logging.getLogger(self.__class__.__name__)

    # ── Minimal interaction helpers (keep components self-contained) ──────────

    def _click(self, locator) -> None:
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def _find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _is_visible(self, locator, timeout: int = 2) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except Exception:
            return False
