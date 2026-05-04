"""Locators for the Practice App Dropdown page (/dropdown.html)."""

from selenium.webdriver.common.by import By


class DropdownLocators:
    """Locators mirroring DropdownPage 1:1 (Law 1).
    Pure selector definitions — zero logic, zero assertions (Law 2).
    """

    STATIC_DROPDOWN  = (By.CSS_SELECTOR, '[data-test="static-dropdown"]')
    STATIC_STATUS    = (By.CSS_SELECTOR, '[data-test="static-status"]')
    DYNAMIC_DROPDOWN = (By.CSS_SELECTOR, '[data-test="dynamic-dropdown"]')
    DYNAMIC_STATUS   = (By.CSS_SELECTOR, '[data-test="dynamic-status"]')
