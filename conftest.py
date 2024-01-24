import pytest
from utils.webdriver_factory import get_driver
from utils.sql_connection import close_connection


@pytest.fixture
def driver():
    # Setup, opens the browser and opens the sql connection
    driver = get_driver()
    yield driver
    # Teardown, closes the browser and closes the sql connection
    driver[0].quit()
    close_connection(driver[1])
