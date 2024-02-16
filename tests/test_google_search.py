from time import sleep
from hamcrest import assert_that, contains_string
from pages.google_search_page import GoogleSearchPage
from pages.google_result_page import GoogleResultPage
from pages.base_page import BasePage
import utils.sql_connection as sql_util


def test_simple_google_search(driver):  # 'driver' argument is automatically provided by the fixture within root conftest
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)
    name = "Naruto"

    element = google_search_page.get_search_input()
    element.send_keys(name)
    element.submit()

    # result page
    result_link = google_result_page.get_result_by_name("Naruto - Wikipedia, la enciclopedia libre")
    result_link.click()
    # result page
    assert_that(base_page.get_title(), contains_string(name))


def test_sql_google_search(driver):
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)
    # driver[1] has the established connection to the .db file
    name = get_track_name_from_db(driver[1])

    element = google_search_page.get_search_input()
    element.send_keys(name)
    element.submit()

    # result page
    result_link = google_result_page.get_result_by_index("1")
    result_link.click()
    # result page
    assert_that(base_page.get_title().lower(), contains_string(name[:20].lower()))


def get_track_name_from_db(sql_conn):
    query = "SELECT Name FROM tracks WHERE TrackId = '1'"

    # Execute a query on the given connection
    cursor = sql_util.execute_query(sql_conn, query)

    # Fetch and return a single result from the cursor
    return sql_util.fetch_one(cursor)[0]
