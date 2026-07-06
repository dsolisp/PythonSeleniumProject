"""
Practice App — Dropdown (ADV-E1, ADV-E2).
Law 3: all selectors accessed via POM methods — no raw By. in specs.

Uses the class-scoped `shared_driver` fixture (one browser per class) and the
`soft_assert` helper so multi-condition checks report every failure together.
"""

import pytest

from pages.practice.dropdown_page import DropdownPage
from tests.helpers import soft_assert


@pytest.mark.practice
@pytest.mark.smoke
class TestDropdown:
    """ADV-E1, ADV-E2 — Static and dynamic dropdown interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, shared_driver):
        self.page = DropdownPage(shared_driver)
        self.page.open()

    # ── ADV-E1: Static dropdown ───────────────────────────────────────────

    def test_static_dropdown(self):
        """ADV-E1: static dropdown visibility and selections."""
        with soft_assert() as s:
            s.check(
                self.page.is_static_dropdown_visible(), "dropdown should be visible"
            )

            self.page.select_static("1")
            s.contains(self.page.get_static_status(), "Option 1")

            self.page.select_static("2")
            s.contains(self.page.get_static_status(), "Option 2")

            self.page.select_static("3")
            s.contains(self.page.get_static_status(), "Option 3")

    # ── ADV-E2: Dynamic dropdown ──────────────────────────────────────────

    def test_dynamic_dropdown_loading_state(self):
        """ADV-E2: the dynamic dropdown state while options load."""
        with soft_assert() as check:
            check.check(
                self.page.is_dynamic_dropdown_disabled(),
                "dynamic dropdown should be disabled while options load",
            )
            check.contains(
                self.page.get_dynamic_status(),
                "Fetching",
                "status should show 'Fetching' while loading",
            )

    def test_dynamic_dropdown_ready_state(self):
        """ADV-E2: the dynamic dropdown state after options load."""
        with soft_assert() as check:
            check.check(
                self.page.is_dynamic_dropdown_enabled(),
                "dynamic dropdown should become enabled after load",
            )
            check.contains(
                self.page.get_dynamic_status(),
                "loaded",
                "status should show 'loaded' after options arrive",
            )

    def test_dynamic_dropdown_selection(self):
        """ADV-E2: selecting a dynamic option updates the status."""
        # Wait for enabled state first
        assert self.page.is_dynamic_dropdown_enabled()
        # API returns option values: selenium, playwright, cypress, appium
        self.page.select_dynamic("selenium")
        assert "Fetching" not in self.page.get_dynamic_status()
