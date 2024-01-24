import pytest
from hamcrest import assert_that, contains_string, equal_to
from pages.google_search_page import GoogleSearchPage
import utils.diff_handler as diff_handler
from pages.base_page import BasePage


@pytest.mark.parametrize("tc_id", ["tc_1234"])
def test_visual_comparison(tc_id, driver):  # 'driver' argument is automatically provided by the fixture within conftest
    base_page = BasePage(driver)
    google_search_page = GoogleSearchPage(driver)

    print(f"Custom mark for : {tc_id}")
    expected_image = f'screenshots_diff/{tc_id}_expected_screenshot.png'
    actual_image = f'screenshots_diff/{tc_id}_actual_screenshot.png'
    diff_output_path = f'screenshots_diff/{tc_id}_diff.png'

    # Capture the actual screenshot
    google_search_page.capture_main_input_screenshot(expected_image)
    # (You may perform some actions here before taking the screenshot)
    # then Refresh the page to check if the screenshot is the same
    # base_page.refresh_page()
    element = google_search_page.get_search_input()
    element.send_keys("Some Text")
    google_search_page.capture_main_input_screenshot(actual_image)

    # Use pixelmatch to compare the images and save the diff image
    visual_difference = diff_handler.compare_images(expected_image, actual_image, diff_output_path)

    # pixelmatch returns the number of pixels that are different, 0 means all pixels are the same
    assert_that(visual_difference, equal_to(0), "Visual differences found!")