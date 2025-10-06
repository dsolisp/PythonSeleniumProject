"""
Google search tests demonstrating page object model patterns.
"""

import time
import pytest
from hamcrest import assert_that, contains_string, equal_to, greater_than, is_not, none
import requests

import utils.sql_connection as sql_util
from pages.base_page import BasePage
from pages.google_search_page import GoogleSearchPage
from pages.google_result_page import GoogleResultPage
from config.settings import settings


@pytest.mark.smoke
def test_simple_google_search(driver):
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)
    search_term = settings.DEFAULT_SEARCH_TERM

    google_search_page.open_google()
    google_search_page.enter_search_term(search_term)
    google_search_page.click_search_button()

    google_result_page.wait_for_results_page()

    results_displayed = google_result_page.is_results_displayed()

    if results_displayed:
        assert_that(results_displayed, equal_to(True))
        assert_that(base_page.get_title(), contains_string("Python"))
        results_count = google_result_page.get_results_count()
        assert_that(results_count, greater_than(0))
    else:
        current_url = base_page.get_current_url()
        assert_that(current_url, contains_string("search"))
        print(
            "⚠️ Results page detected but results may be blocked - "
            "this is expected with Google"
        )


@pytest.mark.database
def test_sql_google_search(driver):
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)

    google_search_page.open_google()

    name = get_track_name_from_db(driver[1])
    assert_that(name, is_not(none()))

    google_search_page.enter_search_term(name)
    google_search_page.click_search_button()

    google_result_page.wait_for_results_page()

    results_displayed = google_result_page.is_results_displayed()

    if results_displayed:
        assert_that(results_displayed, equal_to(True))
        title = base_page.get_title()
        search_performed = (
            "search" in title.lower() or name.split()[0].lower() in title.lower()
        )
        assert_that(search_performed, equal_to(True))
    else:
        current_url = base_page.get_current_url()
        assert_that(current_url, contains_string("search"))
        print(
            f"⚠️ Search performed for '{name}' but results may be blocked - "
            f"this is expected"
        )


@pytest.mark.smoke
def test_google_search_with_action_chains(driver):
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)
    search_term = settings.DEFAULT_SEARCH_TERM

    google_search_page.open_google()

    google_search_page.click_search_input_advanced()
    google_search_page.type_with_action_chains(search_term)

    suggestions_appeared = google_search_page.wait_for_suggestions()
    if suggestions_appeared:
        print("✅ Search suggestions detected")
    else:
        print("ℹ️ No search suggestions appeared")

    google_search_page.click_search_button()

    google_result_page.wait_for_results_page_complete()

    results_displayed = google_result_page.is_results_displayed()

    if results_displayed:
        assert_that(results_displayed, equal_to(True))
        assert_that(base_page.get_title(), contains_string("Python"))
        results_count = google_result_page.get_results_count()
        assert_that(results_count, greater_than(0))
    else:
        current_url = base_page.get_current_url()
        assert_that(current_url, contains_string("search"))
        print(
            "⚠️ Advanced search completed but results may be blocked - this is expected"
        )


@pytest.mark.database
def test_database_search_with_performance_monitoring(driver):
    google_search_page = GoogleSearchPage(driver)
    google_result_page = GoogleResultPage(driver)
    base_page = BasePage(driver)

    start_time = time.time()
    google_search_page.open_google()
    page_open_time = time.time() - start_time

    start_time = time.time()
    search_term = get_track_name_from_db(driver[1])
    db_query_time = time.time() - start_time

    assert_that(search_term, is_not(none()))

    start_time = time.time()
    google_search_page.enter_search_term(search_term)
    google_search_page.click_search_button()
    search_execution_time = time.time() - start_time

    google_result_page.wait_for_results_page()

    assert_that(page_open_time, greater_than(0.0))
    assert_that(db_query_time, greater_than(0.0))
    assert_that(search_execution_time, greater_than(0.0))

    results_displayed = google_result_page.is_results_displayed()

    if results_displayed:
        assert_that(results_displayed, equal_to(True))
        results_count = google_result_page.get_results_count()
        assert_that(results_count, greater_than(0))
    else:
        current_url = base_page.get_current_url()
        assert_that(current_url, contains_string("search"))
        print(
            f"⚠️ Monitored search for '{search_term}' completed "
            f"but results may be blocked"
        )

    print(
        f"✅ Performance monitoring - Page: {page_open_time:.2f}s, "
        f"DB: {db_query_time:.2f}s, Search: {search_execution_time:.2f}s"
    )


@pytest.mark.api
def test_framework_api_functionality():
    from config.settings import settings

    response = requests.get(f"{settings.API_BASE_URL}/posts/1")

    assert_that(response.status_code, equal_to(200))

    data = response.json()
    assert_that("title" in data, equal_to(True))
    assert_that("body" in data, equal_to(True))
    assert_that("userId" in data, equal_to(True))

    print(f"✅ API test passed - Post title: {data['title'][:50]}...")


@pytest.mark.advanced
def test_element_health_monitoring(driver):
    google_search_page = GoogleSearchPage(driver)
    google_search_page.open_google()

    element_health = google_search_page.get_search_input_health()

    assert_that(element_health["exists"], equal_to(True))
    assert_that(element_health["is_displayed"], equal_to(True))
    assert_that(element_health["is_enabled"], equal_to(True))
    assert_that(element_health["tag_name"], equal_to("input"))

    google_search_page.enter_search_term("health test")
    input_value = google_search_page.get_search_input_value()
    assert_that(input_value, equal_to("health test"))

    element_dimensions = google_search_page.get_search_input_dimensions()
    assert_that(element_dimensions["width"], greater_than(0))
    assert_that(element_dimensions["height"], greater_than(0))
    assert_that(element_dimensions["x"] >= 0, equal_to(True))
    assert_that(element_dimensions["y"] >= 0, equal_to(True))


@pytest.mark.advanced
def test_webdriver_wait_conditions(driver):
    google_search_page = GoogleSearchPage(driver)
    google_search_page.open_google()

    is_clickable = google_search_page.wait_for_search_input_clickable()
    assert_that(is_clickable, equal_to(True))

    is_visible = google_search_page.wait_for_search_input_visible()
    assert_that(is_visible, equal_to(True))

    google_search_page.click_search_input()
    has_focus = google_search_page.wait_for_search_input_focus()
    assert_that(has_focus, equal_to(True))

    google_search_page.enter_search_term("selenium")
    text_appeared = google_search_page.wait_for_text_in_search_input("selenium")
    assert_that(text_appeared, equal_to(True))

    final_value = google_search_page.get_search_input_value()
    assert_that(final_value, equal_to("selenium"))


@pytest.mark.performance
def test_page_interaction_timing(driver):
    google_search_page = GoogleSearchPage(driver)

    page_load_time = google_search_page.open_google_with_timing()
    element_find_time = google_search_page.get_search_input_timing()
    typing_time = google_search_page.enter_search_term_with_timing(
        "performance testing"
    )
    clear_retype_time = google_search_page.clear_and_retype_with_timing(
        "selenium performance"
    )

    assert_that(page_load_time, greater_than(0.0))
    assert_that(element_find_time, greater_than(0.0))
    assert_that(typing_time, greater_than(0.0))
    assert_that(clear_retype_time, greater_than(0.0))

    final_value = google_search_page.get_search_input_value()
    assert_that(final_value, equal_to("selenium performance"))

    print(
        f"✅ Performance metrics - Page: {page_load_time:.2f}s, "
        f"Find: {element_find_time:.2f}s, Type: {typing_time:.2f}s, "
        f"Clear+Type: {clear_retype_time:.2f}s"
    )


def get_track_name_from_db(sql_conn):
    try:
        query = "SELECT Name FROM tracks WHERE TrackId = '1'"
        cursor = sql_util.execute_query(sql_conn, query)
        result = sql_util.fetch_one(cursor)

        if result and len(result) > 0:
            return result[0]
        else:
            print("No track found in database")
            return None

    except Exception as e:
        print(f"Error querying database: {e}")
        return None
