"""Locators for the Practice App Iframes page (/iframes.html)."""

from selenium.webdriver.common.by import By


class IframesLocators:
    """Locators mirroring IframesPage 1:1 (Law 1).
    Pure selector definitions — zero logic, zero assertions (Law 2).

    The iframe *element* locators target the host-page <iframe> tags.
    Inner-document locators are used after switching driver context into the frame.
    """

    # ── /iframes.html host-page iframe elements ───────────────────────────
    PARENT_FRAME = (By.CSS_SELECTOR, '[data-test="parent-frame"]')
    OUTER_FRAME = (By.CSS_SELECTOR, '[data-test="outer-frame"]')

    # ── Inside parentFrame (editor.html) ──────────────────────────────────
    EDITOR = (By.CSS_SELECTOR, '[data-test="editor"]')

    # ── Inside outerFrame → childFrame (inner-form.html) ──────────────────
    CHILD_FRAME = (By.CSS_SELECTOR, '[data-test="child-frame"]')
    INNER_NAME = (By.CSS_SELECTOR, '[data-test="inner-name"]')
    INNER_EMAIL = (By.CSS_SELECTOR, '[data-test="inner-email"]')
    INNER_SUBMIT = (By.CSS_SELECTOR, '[data-test="inner-submit"]')
    INNER_RESULT = (By.CSS_SELECTOR, '[data-test="inner-result"]')
