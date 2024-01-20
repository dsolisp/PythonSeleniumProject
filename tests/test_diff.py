
import pytest
from hamcrest import assert_that, contains_string, equal_to
from pages.home_page import HomePage
import utils.diff_handler as diff_handler


@pytest.mark.parametrize("tc_id", ["tc_1234"])
def test_visual_comparison(tc_id, driver):  # 'driver' argument is automatically provided by the fixture within conftest
    print(f"Custom mark for : {tc_id}")
    expected_image = f'screenshots_diff/{tc_id}_expected_screenshot.png'
    actual_image = f'screenshots_diff/{tc_id}actual_screenshot.png'
    diff_output_path = f'screenshots_diff/{tc_id}_diff.png'

    login_page = HomePage(driver)
    login_page.open_url('https://google.com')

    # Capture the actual screenshot
    login_page.capture_element_screenshot(expected_image)
    # (You may perform some actions here before taking the screenshot)
    # then Refresh the page to check if the screenshot is the same
    # login_page.refresh_page()
    element = login_page.get_search_input()
    element.send_keys("Some Text")
    login_page.capture_element_screenshot(actual_image)

    # Use pixelmatch to compare the images and save the diff image
    visual_difference = diff_handler.compare_images(expected_image, actual_image, diff_output_path)

    # pixelmatch returns the number of pixels that are different, 0 means all pixels are the same
    assert_that(visual_difference, equal_to(0), "Visual differences found!")