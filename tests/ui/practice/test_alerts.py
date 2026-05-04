"""
Practice App — JS Alerts (ADV-E7, ADV-E8, ADV-E9).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.alerts_page import AlertsPage


@pytest.mark.practice
@pytest.mark.smoke
class TestAlerts:
    """ADV-E7, ADV-E8, ADV-E9 — JS dialog interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, selenium_driver):
        self.page = AlertsPage(selenium_driver)
        self.page.open()

    # ── ADV-E7: Simple alert ──────────────────────────────────────────────

    def test_simple_alert_text_and_result(self):
        """ADV-E7: clicking trigger fires an alert with the expected message."""
        self.page.trigger_alert()
        alert_text = self.page.accept_alert()
        assert alert_text == "This is a simple alert!"
        assert self.page.get_result_text() == "Alert accepted."

    # ── ADV-E8: Confirm dialog ────────────────────────────────────────────

    def test_confirm_accepted_updates_result(self):
        """ADV-E8: accepting a confirm dialog sets the expected result text."""
        self.page.trigger_confirm()
        self.page.accept_alert()
        assert self.page.get_result_text() == "Confirm accepted."

    def test_confirm_dismissed_updates_result(self):
        """ADV-E8: dismissing a confirm dialog sets the expected result text."""
        self.page.trigger_confirm()
        self.page.dismiss_alert()
        assert self.page.get_result_text() == "Confirm dismissed."

    # ── ADV-E9: Prompt dialog ─────────────────────────────────────────────

    def test_prompt_echoes_entered_text(self):
        """ADV-E9: responding to a prompt echoes the input in the result."""
        self.page.trigger_prompt()
        self.page.respond_to_prompt("Daniel")
        assert "Daniel" in self.page.get_result_text()

    def test_prompt_dismissed_shows_dismissed_message(self):
        """ADV-E9: dismissing a prompt shows the dismissed message."""
        self.page.trigger_prompt()
        self.page.dismiss_alert()
        assert self.page.get_result_text() == "Prompt dismissed."
