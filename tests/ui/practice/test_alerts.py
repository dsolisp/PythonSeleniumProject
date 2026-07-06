"""
Practice App — JS Alerts (ADV-E7, ADV-E8, ADV-E9).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.alerts_page import AlertsPage
from tests.helpers import soft_assert


@pytest.mark.practice
@pytest.mark.smoke
@pytest.mark.usefixtures("shared_driver")
class TestAlerts:
    """ADV-E7, ADV-E8, ADV-E9 — JS dialog interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, shared_driver):
        self.page = AlertsPage(shared_driver)
        self.page.open()

    def test_all_js_alerts(self):
        """ADV-E7 to ADV-E9: Verify simple alert, confirm, and prompt dialogs."""
        with soft_assert() as s:
            # ADV-E7: Simple alert
            self.page.trigger_alert()
            alert_text = self.page.accept_alert()
            s.equal(alert_text, "This is a simple alert!")
            s.equal(self.page.get_result_text(), "Alert accepted.")

            # ADV-E8: Confirm dialog (Accept)
            self.page.trigger_confirm()
            self.page.accept_alert()
            s.equal(self.page.get_result_text(), "Confirm accepted.")

            # ADV-E8: Confirm dialog (Dismiss)
            self.page.trigger_confirm()
            self.page.dismiss_alert()
            s.equal(self.page.get_result_text(), "Confirm dismissed.")

            # ADV-E9: Prompt dialog (Respond)
            self.page.trigger_prompt()
            self.page.respond_to_prompt("Daniel")
            s.contains(self.page.get_result_text(), "Daniel")

            # ADV-E9: Prompt dialog (Dismiss)
            self.page.trigger_prompt()
            self.page.dismiss_alert()
            s.equal(self.page.get_result_text(), "Prompt dismissed.")
