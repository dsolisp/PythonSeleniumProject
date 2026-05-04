"""
Practice App — Windows / Tabs (ADV-E5, ADV-E6).
Law 3: all selectors accessed via POM methods — no raw By. in specs.

Strategy (Selenium):
  E5 — click target="_blank" link; Selenium opens a new window handle.
  E6 — click JS window.open() button; Selenium captures the new handle.
"""

import pytest

from pages.practice.windows_page import WindowsPage


@pytest.mark.practice
@pytest.mark.smoke
class TestWindows:
    """ADV-E5, ADV-E6 — New window / tab interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, selenium_driver):
        self.page = WindowsPage(selenium_driver)
        self.page.open()

    # ── ADV-E5: target="_blank" link ──────────────────────────────────────

    def test_tab_link_has_correct_href(self):
        """ADV-E5: the new-tab link href points to /windows/new."""
        href = self.page.get_tab_link_href()
        assert "/windows/new" in href

    def test_tab_link_opens_new_window_with_correct_content(self):
        """ADV-E5: clicking the link opens a new window with the expected heading."""
        original = self.page.click_tab_link()
        self.page.switch_to_new_window(original)
        assert self.page.get_new_window_heading() == "New Window"
        assert "opened in a new tab" in self.page.get_new_window_body()
        self.page.close_current_window()
        self.page.switch_to_window(original)

    # ── ADV-E6: window.open() ─────────────────────────────────────────────

    def test_tab_button_is_visible(self):
        """ADV-E6: the JS open button is visible with correct text."""
        assert self.page.is_tab_button_visible()
        assert "Open a New Window" in self.page.get_tab_button_text()

    def test_tab_button_opens_new_window(self):
        """ADV-E6: clicking the JS button opens a new window."""
        original = self.page.click_tab_button()
        self.page.switch_to_new_window(original)
        assert self.page.get_new_window_heading() == "New Window"
        self.page.close_current_window()
        self.page.switch_to_window(original)
