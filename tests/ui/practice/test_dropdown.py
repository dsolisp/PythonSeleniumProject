"""
Practice App — Dropdown (ADV-E1, ADV-E2).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.dropdown_page import DropdownPage


@pytest.mark.practice
@pytest.mark.smoke
class TestDropdown:
    """ADV-E1, ADV-E2 — Static and dynamic dropdown interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, selenium_driver):
        self.page = DropdownPage(selenium_driver)
        self.page.open()

    # ── ADV-E1: Static dropdown ───────────────────────────────────────────

    def test_static_dropdown_is_visible(self):
        """ADV-E1: static dropdown is present on page load."""
        assert self.page.is_static_dropdown_visible()

    def test_select_option_1_updates_status(self):
        """ADV-E1: selecting Option 1 shows it in the status."""
        self.page.select_static("1")
        assert "Option 1" in self.page.get_static_status()

    def test_select_option_2_updates_status(self):
        """ADV-E1: selecting Option 2 shows it in the status."""
        self.page.select_static("2")
        assert "Option 2" in self.page.get_static_status()

    def test_select_option_3_updates_status(self):
        """ADV-E1: selecting Option 3 shows it in the status."""
        self.page.select_static("3")
        assert "Option 3" in self.page.get_static_status()

    # ── ADV-E2: Dynamic dropdown ──────────────────────────────────────────

    def test_dynamic_dropdown_starts_disabled(self):
        """ADV-E2: the dynamic dropdown is disabled while options load."""
        assert self.page.is_dynamic_dropdown_disabled()
        assert "Fetching" in self.page.get_dynamic_status()

    def test_dynamic_dropdown_becomes_enabled(self):
        """ADV-E2: the dynamic dropdown becomes enabled after ~1.5 s."""
        assert self.page.is_dynamic_dropdown_enabled()
        assert "loaded" in self.page.get_dynamic_status()

    def test_dynamic_dropdown_selection(self):
        """ADV-E2: selecting a dynamic option updates the status."""
        assert self.page.is_dynamic_dropdown_enabled()
        self.page.select_dynamic("1")
        assert "Fetching" not in self.page.get_dynamic_status()
