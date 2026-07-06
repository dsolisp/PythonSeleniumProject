"""
Practice App — Iframes (ADV-E3, ADV-E4).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.iframes_page import IframesPage
from tests.helpers import soft_assert


@pytest.mark.practice
@pytest.mark.usefixtures("shared_driver")
class TestIframes:
    """ADV-E3, ADV-E4 — Simple and nested iframe interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, shared_driver):
        self.page = IframesPage(shared_driver)
        self.page.open()

    def test_simple_iframe_editor(self):
        """ADV-E3: Verify contenteditable editor inside a simple iframe."""
        with soft_assert() as s:
            s.check(
                self.page.is_parent_frame_visible(), "parent iframe should be visible"
            )

            self.page.type_in_editor("Hello from Python!")
            s.contains(self.page.get_editor_text(), "Hello from Python!")

            self.page.clear_editor()
            self.page.type_in_editor("Replaced text")
            s.contains(self.page.get_editor_text(), "Replaced text")

    def test_nested_iframes_form(self):
        """ADV-E4: Verify form submission inside nested iframes."""
        with soft_assert() as s:
            s.check(
                self.page.is_outer_frame_visible(), "outer iframe should be visible"
            )

            self.page.submit_inner_form("Alice", "alice@example.com")
            result = self.page.get_inner_result()
            s.contains(result, "Alice")
            s.contains(result, "alice@example.com")

            self.page.submit_inner_form("", "test@example.com")
            s.contains(self.page.get_inner_result(), "(no name)")
