from time import sleep
from hamcrest import assert_that, contains_string
from pages.google_search_page import GoogleSearchPage
from pages.google_result_page import GoogleResultPage
from pages.base_page import BasePage


def test_basic_google_search(driver):  # 'driver' argument is automatically provided by the fixture within root conftest
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)
    name = "Naruto"

    element = google_search_page.get_search_input()
    element.send_keys(name)
    element.submit()

    # result page
    result_link = google_result_page.get_first_result()
    result_link.click()
    # result page
    assert_that(base_page.get_title(), contains_string(name))

