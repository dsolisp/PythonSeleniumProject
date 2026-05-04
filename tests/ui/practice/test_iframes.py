"""
Practice App — Iframes (ADV-E3, ADV-E4).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.iframes_page import IframesPage


@pytest.mark.practice
class TestIframes:
    """ADV-E3, ADV-E4 — Simple and nested iframe interactions."""

    @pytest.fixture(autouse=True)
    def open_page(self, selenium_driver):
        self.page = IframesPage(selenium_driver)
        self.page.open()

    # ── ADV-E3: Simple iframe (contenteditable editor) ────────────────────

    def test_parent_frame_is_visible(self):
        """ADV-E3: the parent iframe element is visible on the host page."""
        assert self.page.is_parent_frame_visible()

    def test_type_in_editor(self):
        """ADV-E3: text typed into the editor is persisted in the iframe."""
        self.page.type_in_editor("Hello from Python!")
        assert "Hello from Python!" in self.page.get_editor_text()

    def test_clear_and_retype_editor(self):
        """ADV-E3: the editor can be cleared and accept new text."""
        self.page.type_in_editor("First text")
        self.page.clear_editor()
        self.page.type_in_editor("Replaced text")
        assert "Replaced text" in self.page.get_editor_text()

    # ── ADV-E4: Nested iframes ─────────────────────────────────────────────

    def test_outer_frame_is_visible(self):
        """ADV-E4: the outer iframe element is visible on the host page."""
        assert self.page.is_outer_frame_visible()

    def test_submit_inner_form_shows_result(self):
        """ADV-E4: submitting the inner form shows the submitted values."""
        self.page.submit_inner_form("Alice", "alice@example.com")
        result = self.page.get_inner_result()
        assert "Alice" in result
        assert "alice@example.com" in result

    def test_submit_without_name_shows_no_name(self):
        """ADV-E4: submitting without a name shows '(no name)' in result."""
        self.page.submit_inner_form("", "test@example.com")
        assert "(no name)" in self.page.get_inner_result()
