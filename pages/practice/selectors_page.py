"""Selector Playground page object for the Practice App (/selectors.html)."""

from selenium.webdriver.support.ui import Select

from config.settings import settings
from locators.practice.selectors_locators import SelectorsLocators
from pages.base_page import BasePage


class SelectorsPage(BasePage):
    """Practice App Selector Playground — all 10 selector strategy sections.

    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).
    """

    def open(self) -> "SelectorsPage":
        """Navigate to the selectors page and return self for chaining."""
        self.navigate_to(f"{settings.PRACTICE_BASE_URL}/selectors.html")
        return self

    # ── Section 1 ─────────────────────────────────────────────────────────
    def get_username_input_attribute(self, attr: str) -> str:
        return self.get_attribute(SelectorsLocators.INPUT_USERNAME, attr)

    def get_password_input_attribute(self, attr: str) -> str:
        return self.get_attribute(SelectorsLocators.INPUT_PASSWORD, attr)

    # ── Section 2 ─────────────────────────────────────────────────────────
    def get_primary_button_class(self) -> str:
        return self.get_attribute(SelectorsLocators.BTN_PRIMARY, "class")

    def get_secondary_button_class(self) -> str:
        return self.get_attribute(SelectorsLocators.BTN_SECONDARY, "class")

    def get_success_badge_text(self) -> str:
        return self.get_text(SelectorsLocators.BADGE_SUCCESS)

    def get_warning_badge_text(self) -> str:
        return self.get_text(SelectorsLocators.BADGE_WARNING)

    def get_error_badge_text(self) -> str:
        return self.get_text(SelectorsLocators.BADGE_ERROR)

    # ── Section 3 ─────────────────────────────────────────────────────────
    def get_exact_link_text(self) -> str:
        return self.get_text(SelectorsLocators.LINK_EXACT)

    def get_partial_link_text(self) -> str:
        return self.get_text(SelectorsLocators.LINK_PARTIAL)

    def get_aria_link_attribute(self, attr: str) -> str:
        return self.get_attribute(SelectorsLocators.LINK_ARIA, attr)

    # ── Section 4 ─────────────────────────────────────────────────────────
    def get_email_input_attribute(self, attr: str) -> str:
        return self.get_attribute(SelectorsLocators.INPUT_EMAIL, attr)

    def get_live_region_text(self) -> str:
        return self.get_text(SelectorsLocators.LIVE_REGION)

    def trigger_live_region(self) -> "SelectorsPage":
        self.click(SelectorsLocators.BTN_TRIGGER_LIVE)
        return self

    # ── Section 5 ─────────────────────────────────────────────────────────
    def is_input_disabled(self) -> bool:
        el = self.wait_for_element(SelectorsLocators.INPUT_DISABLED)
        return not el.is_enabled() if el else True

    def is_radio_pro_checked(self) -> bool:
        el = self.wait_for_element(SelectorsLocators.RADIO_PRO)
        return el.is_selected() if el else False

    def is_radio_basic_checked(self) -> bool:
        el = self.wait_for_element(SelectorsLocators.RADIO_BASIC)
        return el.is_selected() if el else False

    def select_country(self, value: str) -> "SelectorsPage":
        el = self.wait_for_element(SelectorsLocators.SELECT_COUNTRY)
        if el:
            Select(el).select_by_value(value)
        return self

    # ── Section 6 ─────────────────────────────────────────────────────────
    def get_product_items_count(self) -> int:
        return len(self.find_elements(SelectorsLocators.PRODUCT_ITEM))

    def get_electronics_items_count(self) -> int:
        return len(self.find_elements(SelectorsLocators.PRODUCT_ELECTRONICS))

    # ── Section 7 ─────────────────────────────────────────────────────────
    def get_logo_attribute(self, attr: str) -> str:
        return self.get_attribute(SelectorsLocators.IMG_LOGO, attr)

    # ── Section 8 ─────────────────────────────────────────────────────────
    def get_save_button_title(self) -> str:
        return self.get_attribute(SelectorsLocators.BTN_SAVE, "title")

    def get_delete_button_title(self) -> str:
        return self.get_attribute(SelectorsLocators.BTN_DELETE, "title")

    def get_abbr_qa_title(self) -> str:
        return self.get_attribute(SelectorsLocators.ABBR_QA, "title")

    # ── Section 9 ─────────────────────────────────────────────────────────
    def get_table_rows_count(self) -> int:
        return len(self.find_elements(SelectorsLocators.TABLE_ROW))

    def get_table_row_name_cell_text(self, row_id: int | str) -> str:
        return self.get_text(SelectorsLocators.table_row_name_cell(row_id))

    # ── Section 10 ────────────────────────────────────────────────────────
    def get_fruit_items_count(self) -> int:
        return len(self.find_elements(SelectorsLocators.FRUIT_ITEM))

    def get_fruit_item_text(self, index: int) -> str:
        items = self.find_elements(SelectorsLocators.FRUIT_ITEM)
        return items[index].text if index < len(items) else ""

    def get_xpath_text(self) -> str:
        return self.get_text(SelectorsLocators.XPATH_TEXT)

    def get_xpath_partial_text(self) -> str:
        return self.get_text(SelectorsLocators.XPATH_PARTIAL)
