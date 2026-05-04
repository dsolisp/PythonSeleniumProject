"""Locators for the Practice App Windows page (/windows.html)."""

from selenium.webdriver.common.by import By


class WindowsLocators:
    """Locators mirroring WindowsPage 1:1 (Law 1).
    Pure selector definitions — zero logic, zero assertions (Law 2).
    """

    # ── /windows.html ──────────────────────────────────────────────────────
    OPEN_TAB_LINK = (By.CSS_SELECTOR, '[data-test="open-new-tab-link"]')
    OPEN_TAB_JS   = (By.CSS_SELECTOR, '[data-test="open-new-tab-js"]')

    # ── /windows/new.html (in new window/tab) ─────────────────────────────
    NEW_WINDOW_HEADING = (By.CSS_SELECTOR, '[data-test="new-window-heading"]')
    NEW_WINDOW_BODY    = (By.CSS_SELECTOR, '[data-test="new-window-body"]')
