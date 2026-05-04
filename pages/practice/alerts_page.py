"""Alerts page object for the Practice App (/alerts.html)."""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from locators.practice.alerts_locators import AlertsLocators
from pages.base_page import BasePage


class AlertsPage(BasePage):
    """Practice App Alerts page (ADV-E7, ADV-E8, ADV-E9).

    Responsibilities: navigate, trigger dialogs, surface result text.
    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).
    """

    def open(self) -> "AlertsPage":
        """Navigate to the alerts page and return self for chaining."""
        self.navigate_to(f"{settings.PRACTICE_BASE_URL}/alerts.html")
        return self

    # ── Actions ───────────────────────────────────────────────────────────

    def trigger_alert(self) -> "AlertsPage":
        """Click the simple alert trigger button."""
        self.click(AlertsLocators.TRIGGER_ALERT)
        return self

    def trigger_confirm(self) -> "AlertsPage":
        """Click the confirm dialog trigger button."""
        self.click(AlertsLocators.TRIGGER_CONFIRM)
        return self

    def trigger_prompt(self) -> "AlertsPage":
        """Click the prompt dialog trigger button."""
        self.click(AlertsLocators.TRIGGER_PROMPT)
        return self

    def accept_alert(self) -> str:
        """Wait for an alert, capture its text, then accept it. Returns the alert text."""
        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        text = alert.text
        alert.accept()
        return text

    def dismiss_alert(self) -> str:
        """Wait for an alert/confirm/prompt, capture its text, then dismiss it."""
        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        text = alert.text
        alert.dismiss()
        return text

    def respond_to_prompt(self, response: str) -> str:
        """Wait for a prompt, send a response, and accept. Returns original prompt text."""
        alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        text = alert.text
        alert.send_keys(response)
        alert.accept()
        return text

    # ── Getters ───────────────────────────────────────────────────────────

    def get_result_text(self) -> str:
        """Return the text of the result element."""
        return self.get_text(AlertsLocators.RESULT_TEXT)
