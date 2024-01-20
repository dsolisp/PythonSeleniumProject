from time import sleep
from  hamcrest import assert_that, contains_string
from pages.home_page import HomePage


def test_login(driver):  # 'driver' argument is automatically provided by the fixture within conftest
    login_page = HomePage(driver)
    login_page.open_url('https://google.com')
    name = "Naruto"

    element = login_page.get_search_input()
    element.send_keys(name)
    element.submit()

    link = login_page.get_first_result()
    link.click()
    sleep(5)
    assert_that(login_page.get_title(), contains_string(name))
    #assert_that(driver.title, contains_string(name))

    # Perform login

    #login_page.enter_username('your_username')
    #login_page.enter_password('your_password')
    #login_page.click_login_button()

    # Assertion (replace with appropriate assertions)
    #assert driver.title == 'Expected Title'