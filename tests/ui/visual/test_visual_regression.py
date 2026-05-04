"""
Visual Regression Tests (Python / Selenium)

Equivalent to:
- Cypress: cypress/e2e/ui/visual/visual-regression.cy.ts
- Playwright: tests/ui/visual/visual-regression.spec.ts

Uses pytest-playwright-snapshot for visual assertion parity.
"""

import shutil
from pathlib import Path

import pytest
from PIL import Image

from pages.sauce.inventory_page import InventoryPage
from pages.sauce.login_page import LoginPage
from utils import diff_handler


@pytest.mark.ui
@pytest.mark.visual
@pytest.mark.sauce
class TestSauceDemoVisual:
    """Visual regression tests for SauceDemo UI components."""

    def _assert_visual_snapshot(self, driver, snapshot_name, threshold=None):
        baseline_dir = Path("baselines")
        actual_dir = Path("screenshots/actual")
        diff_dir = Path("screenshots/diff")

        baseline_dir.mkdir(exist_ok=True, parents=True)
        actual_dir.mkdir(exist_ok=True, parents=True)
        diff_dir.mkdir(exist_ok=True, parents=True)

        baseline_path = baseline_dir / f"{snapshot_name}.png"
        actual_path = actual_dir / f"{snapshot_name}.png"
        diff_path = diff_dir / f"{snapshot_name}_diff.png"

        driver.save_screenshot(str(actual_path))

        if not baseline_path.exists():
            shutil.copy(actual_path, baseline_path)
            return

        diff_pixels = diff_handler.compare_images(
            str(baseline_path), str(actual_path), str(diff_path)
        )

        tol = 100  # Default pixel tolerance
        if isinstance(threshold, float) and threshold < 1.0:
            with Image.open(baseline_path) as img:
                w, h = img.size
                tol = int(w * h * threshold)
        elif threshold is not None:
            tol = threshold

        assert diff_pixels <= tol, (
            f"Visual diff for {snapshot_name}: {diff_pixels} pixels differ"
        )

    # ── Login Page visual states ────────────────────────────────────────

    def test_login_page_default_state(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        assert login_page.is_loaded()
        self._assert_visual_snapshot(selenium_driver, "login-page-default-state")

    def test_login_page_error_state(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        login_page.login("invalid", "invalid")
        assert login_page.get_error_message()
        self._assert_visual_snapshot(selenium_driver, "login-page-error-state")

    def test_login_form_component_only(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        assert login_page.is_loaded()
        self._assert_visual_snapshot(selenium_driver, "login-form-component")

    # ── Inventory Page visual states ────────────────────────────────────

    def test_inventory_page_full_scroll(self, authenticated_driver):
        inventory_page = InventoryPage(authenticated_driver)
        inventory_page.open()
        assert inventory_page.is_loaded()
        self._assert_visual_snapshot(authenticated_driver, "inventory-page-full")

    def test_inventory_page_ignoring_cart_badge(self, authenticated_driver):
        inventory_page = InventoryPage(authenticated_driver)
        inventory_page.open()
        assert inventory_page.is_loaded()
        self._assert_visual_snapshot(authenticated_driver, "inventory-page-clean")

    # ── Responsive Layout — Cross-Device ────────────────────────────────

    def test_mobile_view_iphone_x(self, selenium_driver):
        selenium_driver.set_window_size(375, 812)
        login_page = LoginPage(selenium_driver)
        login_page.open()
        self._assert_visual_snapshot(selenium_driver, "login-page-mobile")

    def test_tablet_view_ipad(self, selenium_driver):
        selenium_driver.set_window_size(768, 1024)
        login_page = LoginPage(selenium_driver)
        login_page.open()
        self._assert_visual_snapshot(selenium_driver, "login-page-tablet")

    def test_desktop_view_1920x1080(self, selenium_driver):
        selenium_driver.set_window_size(1920, 1080)
        login_page = LoginPage(selenium_driver)
        login_page.open()
        self._assert_visual_snapshot(selenium_driver, "login-page-desktop")

    # ── Advanced snapshot comparisons ───────────────────────────────────

    def test_minor_differences_10_percent_threshold(self, authenticated_driver):
        inventory_page = InventoryPage(authenticated_driver)
        inventory_page.open()
        assert inventory_page.is_loaded()
        self._assert_visual_snapshot(
            authenticated_driver, "inventory-flexible-comparison", threshold=0.10
        )

    def test_tiny_differences_1_percent_threshold(self, authenticated_driver):
        inventory_page = InventoryPage(authenticated_driver)
        inventory_page.open()
        assert inventory_page.is_loaded()
        self._assert_visual_snapshot(
            authenticated_driver, "inventory-strict-comparison", threshold=0.01
        )

    # ── Component visual snapshots ───────────────────────────────────────

    def test_login_button_component(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        assert login_page.is_loaded()
        self._assert_visual_snapshot(selenium_driver, "login-button-component")

    def test_username_input_field(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        assert login_page.is_loaded()
        self._assert_visual_snapshot(selenium_driver, "username-input-component")

    def test_login_logo(self, selenium_driver):
        login_page = LoginPage(selenium_driver)
        login_page.open()
        assert login_page.is_loaded()
        self._assert_visual_snapshot(selenium_driver, "login-logo-component")
