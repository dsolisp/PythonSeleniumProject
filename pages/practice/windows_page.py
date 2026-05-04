"""Windows/tabs page object for the Practice App (/windows.html)."""

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings
from locators.practice.windows_locators import WindowsLocators
from pages.base_page import BasePage


class WindowsPage(BasePage):
    """Practice App Windows page (ADV-E5, ADV-E6).

    Responsibilities: navigate, open new tabs, switch window handles.
    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).

    Strategy:
      E5 — click target="_blank" link; switch to new window handle.
      E6 — click JS window.open() button; switch to new window handle.
    """

    def open(self) -> "WindowsPage":
        """Navigate to the windows page and return self for chaining."""
        self.navigate_to(f"{settings.PRACTICE_BASE_URL}/windows.html")
        return self

    # ── ADV-E5: target="_blank" link ──────────────────────────────────────

    def get_tab_link_href(self) -> str:
        """Return the href attribute of the new-tab link."""
        return self.get_attribute(WindowsLocators.OPEN_TAB_LINK, "href")

    def click_tab_link(self) -> str:
        """Click the new-tab link and return the handle of the original window."""
        original_handle = self.driver.current_window_handle
        self.click(WindowsLocators.OPEN_TAB_LINK)
        return original_handle

    # ── ADV-E6: window.open() ─────────────────────────────────────────────

    def is_tab_button_visible(self) -> bool:
        """Return True when the JS open button is visible."""
        return self.is_element_visible(WindowsLocators.OPEN_TAB_JS)

    def get_tab_button_text(self) -> str:
        """Return the text of the JS open button."""
        return self.get_text(WindowsLocators.OPEN_TAB_JS)

    def click_tab_button(self) -> str:
        """Click the JS window.open() button and return the original window handle."""
        original_handle = self.driver.current_window_handle
        self.click(WindowsLocators.OPEN_TAB_JS)
        return original_handle

    # ── Window handle helpers ─────────────────────────────────────────────

    def switch_to_new_window(self, original_handle: str) -> "WindowsPage":
        """Wait for a new window and switch to it."""
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
        for handle in self.driver.window_handles:
            if handle != original_handle:
                self.driver.switch_to.window(handle)
                break
        return self

    def switch_to_window(self, handle: str) -> "WindowsPage":
        """Switch back to a known window handle."""
        self.driver.switch_to.window(handle)
        return self

    def close_current_window(self) -> "WindowsPage":
        """Close the current window."""
        self.driver.close()
        return self

    # ── /windows/new.html getters (used after switching) ──────────────────

    def get_new_window_heading(self) -> str:
        """Return the heading text on the new window page."""
        return self.get_text(WindowsLocators.NEW_WINDOW_HEADING)

    def get_new_window_body(self) -> str:
        """Return the body text on the new window page."""
        return self.get_text(WindowsLocators.NEW_WINDOW_BODY)
