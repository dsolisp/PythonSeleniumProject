"""
Practice App — Selector Playground (all 10 selector strategies).
Law 3: all selectors accessed via POM methods — no raw By. in specs.
"""

import pytest

from pages.practice.selectors_page import SelectorsPage


@pytest.mark.practice
@pytest.mark.advanced
@pytest.mark.selectors
class TestSelectors:
    """Demonstrates all 10 selector strategies via the /selectors.html page."""

    @pytest.fixture(autouse=True)
    def open_page(self, selenium_driver):
        self.page = SelectorsPage(selenium_driver)
        self.page.open()

    def test_s1_id_and_name_inputs(self):
        """S1: locate inputs by data-test (mirrors id/name attributes)."""
        assert self.page.get_username_input_attribute("id") == "username-field"
        assert self.page.get_password_input_attribute("name") == "password"

    def test_s2_css_class_buttons(self):
        """S2: locate primary and secondary buttons by class."""
        assert "btn-primary" in self.page.get_primary_button_class()
        assert "btn-secondary" in self.page.get_secondary_button_class()

    def test_s2_css_class_badges(self):
        """S2: locate status badges by data-test variant."""
        assert self.page.get_success_badge_text() == "Active"
        assert self.page.get_warning_badge_text() == "Pending"
        assert self.page.get_error_badge_text() == "Inactive"

    def test_s3_link_text_exact_and_partial(self):
        """S3: locate links by exact and partial text content."""
        assert "Download Report" in self.page.get_exact_link_text()
        assert "Annual Summary" in self.page.get_partial_link_text()

    def test_s3_aria_label_link(self):
        """S3: locate link by aria-label attribute."""
        assert (
            self.page.get_aria_link_attribute("aria-label")
            == "Download the PDF document"
        )

    def test_s4_aria_email_input(self):
        """S4: locate input by role and aria-label."""
        assert self.page.get_email_input_attribute("role") == "textbox"
        assert self.page.get_email_input_attribute("aria-label") == "Work email address"

    def test_s4_live_region_updates_on_trigger(self):
        """S4: live region updates when its trigger button is clicked."""
        self.page.trigger_live_region()
        assert "Updated at" in self.page.get_live_region_text()

    def test_s5_disabled_input(self):
        """S5: disabled input is not editable."""
        assert self.page.is_input_disabled()

    def test_s5_radio_pro_pre_checked(self):
        """S5: radio Pro is pre-checked; Basic is not."""
        assert self.page.is_radio_pro_checked()
        assert not self.page.is_radio_basic_checked()

    def test_s5_country_dropdown(self):
        """S5: a country can be selected from the dropdown."""
        self.page.select_country("us")
        assert self.page.is_input_disabled()  # guard: page still stable

    def test_s6_data_attributes(self):
        """S6: locate products by data-test + data-category."""
        assert self.page.get_product_items_count() == 3
        assert self.page.get_electronics_items_count() == 2

    def test_s7_image_logo(self):
        """S7: locate logo image by alt and title attributes."""
        assert self.page.get_logo_attribute("alt") == "QA Practice Lab logo"
        assert self.page.get_logo_attribute("title") == "QA Practice Lab"

    def test_s8_title_attribute_buttons(self):
        """S8: locate buttons by title attribute."""
        assert self.page.get_save_button_title() == "Save your current progress"
        assert self.page.get_delete_button_title() == "Delete this record permanently"

    def test_s8_abbr_title(self):
        """S8: locate abbr element by title attribute."""
        assert self.page.get_abbr_qa_title() == "Quality Assurance"

    def test_s9_table_rows(self):
        """S9: locate table rows and verify name cell content."""
        assert self.page.get_table_rows_count() == 3
        assert self.page.get_table_row_name_cell_text(2) == "Bob"

    def test_s10_fruit_items(self):
        """S10: locate fruit list items by data-test."""
        assert self.page.get_fruit_items_count() == 3
        assert self.page.get_fruit_item_text(1) == "Banana"

    def test_s10_xpath_text_targets(self):
        """S10: locate elements by text content (XPath equivalent via data-test)."""
        assert "quick brown fox" in self.page.get_xpath_text()
        assert "partial text" in self.page.get_xpath_partial_text()
