"""
Practice App — Windows / Tabs (ADV-E5, ADV-E6).
Law 3: all selectors accessed via POM methods — no raw By. in specs.

Strategy (Selenium):
  E5 — click target="_blank" link; Selenium opens a new window handle.
  E6 — click JS window.open() button; Selenium captures the new handle.
"""

import pytest

from pages.practice.windows_page import WindowsPage
from tests.helpers import soft_assert


@pytest.mark.practice
@pytest.mark.smoke
@pytest.mark.usefixtures("shared_driver")
class TestWindows:
    """ADV-E5, ADV-E6 — New window / tab interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, shared_driver):
        self.page = WindowsPage(shared_driver)
        self.page.open()

    # ── ADV-E5: target="_blank" link ──────────────────────────────────────

    def test_tab_link_opens_new_window(self):
        """ADV-E5: link href and clicking it opens a new window with correct content."""
        href = self.page.get_tab_link_href()

        original = self.page.click_tab_link()
        self.page.switch_to_new_window(original)

        with soft_assert() as s:
            s.contains(href, "/windows/new", "link href should point to /windows/new")
            s.equal(self.page.get_new_window_heading(), "New Window")
            s.contains(self.page.get_new_window_body(), "opened in a new tab")

        self.page.close_current_window()
        self.page.switch_to_window(original)

    # ── ADV-E6: window.open() ─────────────────────────────────────────────

    def test_tab_button_opens_new_window(self):
        """ADV-E6: JS button visibility and clicking it opens a new window."""
        is_visible = self.page.is_tab_button_visible()
        button_text = self.page.get_tab_button_text()

        original = self.page.click_tab_button()
        self.page.switch_to_new_window(original)

        with soft_assert() as s:
            s.check(is_visible, "JS open button should be visible")
            s.contains(button_text, "Open a New Window")
            s.equal(self.page.get_new_window_heading(), "New Window")

        self.page.close_current_window()
        self.page.switch_to_window(original)
