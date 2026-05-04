"""Iframes page object for the Practice App (/iframes.html)."""

from config.settings import settings
from locators.practice.iframes_locators import IframesLocators
from pages.base_page import BasePage


class IframesPage(BasePage):
    """Practice App Iframes page (ADV-E3, ADV-E4).

    Responsibilities: navigate, switch frame context, interact with frame content.
    No assertions — callers decide what to assert (Law 2).
    Inherits BasePage only (max 1 level — Law 4).
    """

    def open(self) -> "IframesPage":
        """Navigate to the iframes page and return self for chaining."""
        self.navigate_to(f"{settings.PRACTICE_BASE_URL}/iframes.html")
        return self

    # ── ADV-E3: Simple iframe (contenteditable editor) ────────────────────

    def is_parent_frame_visible(self) -> bool:
        """Return True when the parent iframe element is visible."""
        return self.is_element_visible(IframesLocators.PARENT_FRAME)

    def type_in_editor(self, text: str) -> "IframesPage":
        """Switch into the editor iframe, type text, then switch back to default."""
        frame_el = self.wait_for_element(IframesLocators.PARENT_FRAME)
        if frame_el:
            self.driver.switch_to.frame(frame_el)
            editor = self.wait_for_element(IframesLocators.EDITOR)
            if editor:
                editor.click()
                editor.send_keys(text)
            self.driver.switch_to.default_content()
        return self

    def get_editor_text(self) -> str:
        """Return the text inside the contenteditable editor."""
        frame_el = self.wait_for_element(IframesLocators.PARENT_FRAME)
        text = ""
        if frame_el:
            self.driver.switch_to.frame(frame_el)
            editor = self.wait_for_element(IframesLocators.EDITOR)
            if editor:
                text = editor.text
            self.driver.switch_to.default_content()
        return text

    def clear_editor(self) -> "IframesPage":
        """Clear the contenteditable editor content."""
        frame_el = self.wait_for_element(IframesLocators.PARENT_FRAME)
        if frame_el:
            self.driver.switch_to.frame(frame_el)
            editor = self.wait_for_element(IframesLocators.EDITOR)
            if editor:
                self.driver.execute_script("arguments[0].innerHTML = '';", editor)
            self.driver.switch_to.default_content()
        return self

    # ── ADV-E4: Nested iframes ─────────────────────────────────────────────

    def is_outer_frame_visible(self) -> bool:
        """Return True when the outer iframe element is visible."""
        return self.is_element_visible(IframesLocators.OUTER_FRAME)

    def submit_inner_form(self, name: str, email: str) -> "IframesPage":
        """Navigate into nested iframes, fill and submit the inner form."""
        outer_el = self.wait_for_element(IframesLocators.OUTER_FRAME)
        if outer_el:
            self.driver.switch_to.frame(outer_el)
            child_el = self.wait_for_element(IframesLocators.CHILD_FRAME)
            if child_el:
                self.driver.switch_to.frame(child_el)
                name_input = self.wait_for_element(IframesLocators.INNER_NAME)
                email_input = self.wait_for_element(IframesLocators.INNER_EMAIL)
                submit_btn = self.wait_for_element(IframesLocators.INNER_SUBMIT)
                if name_input:
                    name_input.clear()
                    name_input.send_keys(name)
                if email_input:
                    email_input.clear()
                    email_input.send_keys(email)
                if submit_btn:
                    submit_btn.click()
        self.driver.switch_to.default_content()
        return self

    def get_inner_result(self) -> str:
        """Return the result text from the inner form after submission."""
        outer_el = self.wait_for_element(IframesLocators.OUTER_FRAME)
        text = ""
        if outer_el:
            self.driver.switch_to.frame(outer_el)
            child_el = self.wait_for_element(IframesLocators.CHILD_FRAME)
            if child_el:
                self.driver.switch_to.frame(child_el)
                result = self.wait_for_element(IframesLocators.INNER_RESULT)
                if result:
                    text = result.text
        self.driver.switch_to.default_content()
        return text
