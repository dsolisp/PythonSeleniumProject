"""
Practice App — Selector Playground (all 10 selector strategies).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.selectors_page import SelectorsPage
from tests.helpers import soft_assert


@pytest.mark.practice
@pytest.mark.advanced
@pytest.mark.selectors
@pytest.mark.usefixtures("shared_driver")
class TestSelectors:
    """Demonstrates all 10 selector strategies via the /selectors.html page."""

    @pytest.fixture(autouse=True)
    def open_page(self, shared_driver):
        self.page = SelectorsPage(shared_driver)
        self.page.open()

    def test_basic_selectors(self):
        """S1-S3: Basic selectors (ID, Name, Class, Link Text, Aria-Label)."""
        with soft_assert() as s:
            # S1: ID and Name
            s.equal(self.page.get_username_input_attribute("id"), "username-field")
            s.equal(self.page.get_password_input_attribute("name"), "password")

            # S2: CSS Classes
            s.contains(self.page.get_primary_button_class(), "btn-primary")
            s.contains(self.page.get_secondary_button_class(), "btn-secondary")
            s.equal(self.page.get_success_badge_text(), "Active")
            s.equal(self.page.get_warning_badge_text(), "Pending")
            s.equal(self.page.get_error_badge_text(), "Inactive")

            # S3: Link Text and Aria-Label
            s.contains(self.page.get_exact_link_text(), "Download Report")
            s.contains(self.page.get_partial_link_text(), "Annual Summary")
            s.equal(
                self.page.get_aria_link_attribute("aria-label"),
                "Download the PDF document",
            )

    def test_accessibility_selectors(self):
        """S4: Accessibility selectors (Role, Aria-Label, Live Region)."""
        with soft_assert() as s:
            # S4: Role and Aria-Label
            s.equal(self.page.get_email_input_attribute("role"), "textbox")
            s.equal(
                self.page.get_email_input_attribute("aria-label"), "Work email address"
            )

            # S4: Live Region
            self.page.trigger_live_region()
            s.contains(self.page.get_live_region_text(), "Updated at")

    def test_form_element_selectors(self):
        """S5: Form element states (Disabled, Radios, Dropdown)."""
        with soft_assert() as s:
            # S5: States
            s.check(self.page.is_input_disabled(), "input should be disabled")
            s.check(self.page.is_radio_pro_checked(), "radio Pro should be checked")
            s.check(
                not self.page.is_radio_basic_checked(),
                "radio Basic should NOT be checked",
            )

            # S5: Dropdown interaction
            self.page.select_country("us")
            s.check(self.page.is_input_disabled(), "input remains disabled")

    def test_attribute_selectors(self):
        """S6-S8: Attribute selectors (Data-*, Images, Titles)."""
        with soft_assert() as s:
            # S6: Data Attributes
            s.equal(self.page.get_product_items_count(), 3)
            s.equal(self.page.get_electronics_items_count(), 2)

            # S7: Image attributes
            s.equal(self.page.get_logo_attribute("alt"), "QA Practice Lab logo")
            s.equal(self.page.get_logo_attribute("title"), "QA Practice Lab")

            # S8: Title attributes
            s.equal(self.page.get_save_button_title(), "Save your current progress")
            s.equal(
                self.page.get_delete_button_title(), "Delete this record permanently"
            )
            s.equal(self.page.get_abbr_qa_title(), "Quality Assurance")

    def test_structural_selectors(self):
        """S9-S10: Structural selectors (Tables, Lists, XPath Text)."""
        with soft_assert() as s:
            # S9: Tables
            s.equal(self.page.get_table_rows_count(), 3)
            s.equal(self.page.get_table_row_name_cell_text(2), "Bob")

            # S10: Lists and Text Content
            s.equal(self.page.get_fruit_items_count(), 3)
            s.equal(self.page.get_fruit_item_text(1), "Banana")
            s.contains(self.page.get_xpath_text(), "quick brown fox")
            s.contains(self.page.get_xpath_partial_text(), "partial text")
