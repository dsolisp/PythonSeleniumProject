
import contextlib
import os
from pathlib import Path

import pytest
from applitools.selenium import Eyes, Target
from hamcrest import assert_that, greater_than, has_property, is_, not_none
from selenium.common.exceptions import WebDriverException

from config.settings import settings
from conftest import get_driver
from pages.base_page import BasePage
from pages.search_engine_page import SearchEnginePage
from utils import diff_handler


# --- APPLITOOLS VISUAL REGRESSION TEST ---
@pytest.mark.visual
def test_visual_comparison_applitools(driver):
    """Applitools visual regression test using project driver and page objects."""
    pytest.skip(
        "Skipping Applitools test: API key not configured or test disabled by user request."
    )
    # --- original test body preserved below ---
    driver, _ = driver  # Unpack driver fixture
    eyes = Eyes()
    eyes.api_key = os.environ.get("APPLITOOLS_API_KEY", "YOUR_API_KEY_HERE")
    try:
        driver.get(settings.BASE_URL)
        search_page = SearchEnginePage(driver)
        element = search_page.get_search_input()
        eyes.open(
            driver,
            "DuckDuckGo Visual Test",
            "Search Input Visual Test",
            {"width": 1200, "height": 800},
        )
        if element:
            eyes.check("Search Input", Target.region(element))
        else:
            eyes.check("Full Page", Target.window())
        eyes.close()
    finally:
        eyes.abort_if_not_closed()

"""
Visual regression tests with image comparison capabilities.
"""


@pytest.mark.visual
@pytest.mark.parametrize("tc_id", ["tc_1234"])
def test_visual_comparison(tc_id: str, driver: tuple) -> None:
    """
    Visual regression test using pixelmatch and page objects.
    Compares expected and actual screenshots, fails if difference exceeds tolerance.
    """
    driver, _ = driver  # Unpack driver fixture
    base_page = BasePage(driver)
    search_page = SearchEnginePage(driver)

    print(f"🔍 Running visual comparison test for: {tc_id}")

    expected_image = f"screenshots_diff/{tc_id}_expected_screenshot.png"
    actual_image = f"screenshots_diff/{tc_id}_actual_screenshot.png"
    diff_output_path = f"screenshots_diff/{tc_id}_diff.png"

    try:
        Path("screenshots_diff").mkdir(parents=True, exist_ok=True)

        if "duckduckgo.com" not in base_page.driver.current_url:
            base_page.driver.get(settings.BASE_URL)
            base_page.wait_for_page_load()

        print(f"📸 Capturing expected screenshot: {expected_image}")
        search_page.capture_search_input_screenshot(expected_image)

        element = search_page.get_search_input()
        if element:
            element.send_keys("Visual Test Query")
            print("✍️ Added text to search input")

        print(f"📸 Capturing actual screenshot: {actual_image}")
        search_page.capture_search_input_screenshot(actual_image)

        assert Path(expected_image).exists(), (
            f"Expected screenshot not found: {expected_image}"
        )
        assert Path(actual_image).exists(), (
            f"Actual screenshot not found: {actual_image}"
        )

        print("🔄 Comparing images...")
        visual_difference = diff_handler.compare_images(
            expected_image,
            actual_image,
            diff_output_path,
        )

        tolerance = 50000
        if visual_difference == 0:
            print("✅ Perfect match - no visual differences detected")
        elif visual_difference <= tolerance:
            print(
                f"⚠️ Minor visual differences detected: {visual_difference} "
                f"pixels (within tolerance)",
            )
        else:
            error_msg = (
                f"Significant visual differences found: {visual_difference} pixels "
                f"(tolerance: {tolerance})"
            )
            if Path(diff_output_path).exists():
                error_msg += f"\nDifference image saved: {diff_output_path}"
            print(f"❌ {error_msg}")
            pytest.fail(error_msg)

        assert visual_difference < 1001, (
            f"Visual differences exceeded tolerance: {visual_difference} pixels"
        )
        print("✅ Visual comparison test completed successfully")

    except (OSError, ValueError, RuntimeError) as e:
        error_msg = f"Visual comparison test failed: {e!s}"
        print(f"❌ {error_msg}")
        if Path(expected_image).exists():
            print(f"Expected image exists: {expected_image}")
        if Path(actual_image).exists():
            print(f"Actual image exists: {actual_image}")
        if Path(diff_output_path).exists():
            print(f"Diff image exists: {diff_output_path}")
        pytest.fail(error_msg)


@pytest.mark.visual
@pytest.mark.smoke
def test_screenshot_functionality():
    driver_tuple = None
    try:
        driver_tuple = get_driver()
        driver = driver_tuple[0] if isinstance(driver_tuple, tuple) else driver_tuple
        base_page = BasePage(driver)
        SearchEnginePage(driver)

        base_page.driver.get(settings.BASE_URL)
        base_page.wait_for_page_load()

        test_screenshot_name = "test_functionality.png"
        screenshot_dir = "screenshots"
        screenshot_path = Path(screenshot_dir) / test_screenshot_name

        # Remove any pre-existing screenshot file
        if screenshot_path.exists():
            screenshot_path.unlink()

        # Take screenshot in the correct directory
        screenshot_filepath = base_page.take_screenshot(str(screenshot_path))
        print(f"[DEBUG] Screenshot attempted at: {screenshot_filepath}")
        file_exists = Path(screenshot_filepath).exists()
        print(f"[DEBUG] File exists after take_screenshot: {file_exists}")

        # Assert screenshot file was created and is non-empty
        assert_that(
            screenshot_filepath,
            is_(not_none()),
            "Screenshot method should return a path",
        )
        assert_that(
            Path(screenshot_filepath).exists(),
            is_(True),
            f"Test screenshot not created: {screenshot_filepath}",
        )
        assert_that(
            Path(screenshot_filepath).stat().st_size,
            greater_than(0),
            "Screenshot file should not be empty",
        )

        print("✅ Screenshot functionality test passed")

        # Do not remove the screenshot file so it can be inspected after the test

    except (WebDriverException, OSError, AssertionError) as e:
        pytest.fail(f"Screenshot functionality test failed: {e!s}")
    finally:
        if driver_tuple:
            if isinstance(driver_tuple, tuple):
                driver_tuple[0].quit()
                with contextlib.suppress(Exception):
                    driver_tuple[1].close()
            else:
                driver_tuple.quit()


@pytest.mark.visual
def test_diff_handler_availability():
    try:
        assert_that(
            diff_handler,
            has_property("compare_images"),
            "diff_handler should have compare_images function",
        )

        print("✅ Diff handler module is properly imported and accessible")

    except ImportError as e:
        pytest.fail(f"Failed to import diff_handler: {e}")
    except AttributeError as e:
        pytest.fail(f"diff_handler missing required functions: {e}")
    except RuntimeError as e:
        pytest.fail(f"Diff handler availability test failed: {e}")
