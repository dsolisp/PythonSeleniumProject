"""Locators for the Practice App Alerts page (/alerts.html)."""

from selenium.webdriver.common.by import By


class AlertsLocators:
    """Locators mirroring AlertsPage 1:1 (Law 1).
    Pure selector definitions — zero logic, zero assertions (Law 2).
    """

    TRIGGER_ALERT = (By.CSS_SELECTOR, '[data-test="trigger-alert"]')
    TRIGGER_CONFIRM = (By.CSS_SELECTOR, '[data-test="trigger-confirm"]')
    TRIGGER_PROMPT = (By.CSS_SELECTOR, '[data-test="trigger-prompt"]')
    RESULT_TEXT = (By.CSS_SELECTOR, '[data-test="result-text"]')
