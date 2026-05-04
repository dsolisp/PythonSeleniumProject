"""Locators for the Practice App Selector Playground (/selectors.html)."""

from selenium.webdriver.common.by import By


class SelectorsLocators:
    """Locators mirroring SelectorsPage 1:1 (Law 1).
    Pure selector definitions — zero logic, zero assertions (Law 2).
    """

    # ── 1 · id & name ──────────────────────────────────────────────────────
    INPUT_USERNAME = (By.CSS_SELECTOR, '[data-test="input-username"]')
    INPUT_PASSWORD = (By.CSS_SELECTOR, '[data-test="input-password"]')

    # ── 2 · CSS class & attribute ──────────────────────────────────────────
    BTN_PRIMARY = (By.CSS_SELECTOR, '[data-test="btn-primary"]')
    BTN_SECONDARY = (By.CSS_SELECTOR, '[data-test="btn-secondary"]')
    BADGE_SUCCESS = (By.CSS_SELECTOR, '[data-test="badge-success"]')
    BADGE_WARNING = (By.CSS_SELECTOR, '[data-test="badge-warning"]')
    BADGE_ERROR = (By.CSS_SELECTOR, '[data-test="badge-error"]')

    # ── 3 · link text ──────────────────────────────────────────────────────
    LINK_EXACT = (By.CSS_SELECTOR, '[data-test="link-exact"]')
    LINK_PARTIAL = (By.CSS_SELECTOR, '[data-test="link-partial"]')
    LINK_ARIA = (By.CSS_SELECTOR, '[data-test="link-aria"]')

    # ── 4 · ARIA ───────────────────────────────────────────────────────────
    INPUT_EMAIL = (By.CSS_SELECTOR, '[data-test="input-email"]')
    LIVE_REGION = (By.CSS_SELECTOR, '[data-test="live-region"]')
    BTN_TRIGGER_LIVE = (By.CSS_SELECTOR, '[data-test="btn-trigger-live"]')

    # ── 5 · form attributes ────────────────────────────────────────────────
    INPUT_DISABLED = (By.CSS_SELECTOR, '[data-test="input-disabled"]')
    SELECT_COUNTRY = (By.CSS_SELECTOR, '[data-test="select-country"]')
    CHECKBOX_AGREE = (By.CSS_SELECTOR, '[data-test="checkbox-agree"]')
    RADIO_BASIC = (By.CSS_SELECTOR, '[data-test="radio-basic"]')
    RADIO_PRO = (By.CSS_SELECTOR, '[data-test="radio-pro"]')

    # ── 6 · data attributes ────────────────────────────────────────────────
    PRODUCT_LIST = (By.CSS_SELECTOR, '[data-test="product-list"]')
    PRODUCT_ITEM = (By.CSS_SELECTOR, '[data-test="product-item"]')
    PRODUCT_ELECTRONICS = (By.CSS_SELECTOR, '[data-category="electronics"]')

    # ── 7 · image ──────────────────────────────────────────────────────────
    IMG_LOGO = (By.CSS_SELECTOR, '[data-test="img-logo"]')

    # ── 8 · title attribute ────────────────────────────────────────────────
    BTN_SAVE = (By.CSS_SELECTOR, '[data-test="btn-save"]')
    BTN_DELETE = (By.CSS_SELECTOR, '[data-test="btn-delete"]')
    ABBR_QA = (By.CSS_SELECTOR, '[data-test="abbr-qa"]')

    # ── 9 · table ──────────────────────────────────────────────────────────
    DATA_TABLE = (By.CSS_SELECTOR, '[data-test="data-table"]')
    TABLE_ROW = (By.CSS_SELECTOR, '[data-test="table-row"]')

    @staticmethod
    def table_row_name_cell(row_id: int | str) -> tuple:
        return (By.CSS_SELECTOR, f'[data-row-id="{row_id}"] [headers="col-name"]')

    # ── 10 · XPath targets ─────────────────────────────────────────────────
    FRUIT_LIST = (By.CSS_SELECTOR, '[data-test="fruit-list"]')
    FRUIT_ITEM = (By.CSS_SELECTOR, '[data-test="fruit-item"]')
    XPATH_TEXT = (By.CSS_SELECTOR, '[data-test="xpath-text"]')
    XPATH_PARTIAL = (By.CSS_SELECTOR, '[data-test="xpath-partial"]')
