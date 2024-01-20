import pytest
from utils.webdriver_factory import get_driver


@pytest.fixture
def driver():
    # Setup
    driver = get_driver()
    yield driver
    # Teardown
    driver.quit()
