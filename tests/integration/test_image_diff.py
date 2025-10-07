"""
Visual regression tests with image comparison capabilities.
"""

import os

import pytest
from hamcrest import assert_that, greater_than, has_property, is_, less_than, not_none

import utils.diff_handler as diff_handler
from config.settings import settings
from pages.base_page import BasePage
from pages.search_engine_page import SearchEnginePage


@pytest.mark.visual
@pytest.mark.parametrize("tc_id", ["tc_1234"])
def test_visual_comparison(tc_id, driver):
    base_page = BasePage(driver)
    search_page = SearchEnginePage(driver)

    print(f"🔍 Running visual comparison test for: {tc_id}")

    expected_image = f"screenshots_diff/{tc_id}_expected_screenshot.png"
    actual_image = f"screenshots_diff/{tc_id}_actual_screenshot.png"
    diff_output_path = f"screenshots_diff/{tc_id}_diff.png"

    try:
        os.makedirs("screenshots_diff", exist_ok=True)

        if "google.com" not in base_page.driver.current_url:
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

        assert_that(
            os.path.exists(expected_image),
            is_(True),
            f"Expected screenshot not found: {expected_image}",
        )
        assert_that(
            os.path.exists(actual_image),
            is_(True),
            f"Actual screenshot not found: {actual_image}",
        )

        print("🔄 Comparing images...")
        visual_difference = diff_handler.compare_images(
            expected_image, actual_image, diff_output_path
        )

        if visual_difference == 0:
            print("✅ Perfect match - no visual differences detected")
        else:
            tolerance = 50000

            if visual_difference <= tolerance:
                print(
                    f"⚠️ Minor visual differences detected: {visual_difference} pixels "
                    f"(within tolerance)"
                )
            else:
                error_msg = (
                    f"Significant visual differences found: {visual_difference} pixels "
                    f"(tolerance: {tolerance})"
                )
                if os.path.exists(diff_output_path):
                    error_msg += f"\nDifference image saved: {diff_output_path}"

                print(f"❌ {error_msg}")
                pytest.fail(error_msg)

        assert_that(
            visual_difference,
            less_than(50001),
            f"Visual differences exceeded tolerance: {visual_difference} pixels",
        )

        print("✅ Visual comparison test completed successfully")

    except Exception as e:
        error_msg = f"Visual comparison test failed: {str(e)}"
        print(f"❌ {error_msg}")

        if os.path.exists(expected_image):
            print(f"Expected image exists: {expected_image}")
        if os.path.exists(actual_image):
            print(f"Actual image exists: {actual_image}")
        if os.path.exists(diff_output_path):
            print(f"Diff image exists: {diff_output_path}")

        pytest.fail(error_msg)


@pytest.mark.visual
@pytest.mark.smoke
def test_screenshot_functionality():
    driver_tuple = None
    try:
        from conftest import get_driver

        driver_tuple = get_driver()

        base_page = BasePage(driver_tuple)
        SearchEnginePage(driver_tuple)

        base_page.driver.get(settings.BASE_URL)
        base_page.wait_for_page_load()

        test_screenshot_name = "test_functionality.png"
        screenshot_path = base_page.take_screenshot(test_screenshot_name)

        assert_that(screenshot_path, is_(not_none()),
                    "Screenshot method should return a path")
        assert_that(
            os.path.exists(screenshot_path),
            is_(True),
            f"Test screenshot not created: {screenshot_path}",
        )
        assert_that(
            os.path.getsize(screenshot_path),
            greater_than(0),
            "Screenshot file should not be empty",
        )

        print("✅ Screenshot functionality test passed")

        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

    except Exception as e:
        pytest.fail(f"Screenshot functionality test failed: {str(e)}")
    finally:
        if driver_tuple:
            if isinstance(driver_tuple, tuple):
                driver_tuple[0].quit()
                try:
                    driver_tuple[1].close()
                except Exception:
                    pass
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
    except Exception as e:
        pytest.fail(f"Diff handler availability test failed: {e}")
