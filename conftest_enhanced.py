"""
Enhanced conftest.py with comprehensive fixtures and modern pytest practices.
"""

import pytest
import os
import time
from typing import Dict, Any, Generator, Optional
from pathlib import Path
import allure

from config.settings import settings, BrowserType
from utils.webdriver_factory_enhanced import webdriver_factory, get_driver
from utils.logger import test_logger, log_test_start, log_test_end
from utils.test_data_manager import test_data_manager
from utils.sql_connection_enhanced import db_manager


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--browser", 
        action="store", 
        default="chrome",
        help="Browser to use for testing"
    )
    parser.addoption(
        "--headless", 
        action="store_true", 
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--environment", 
        action="store", 
        default="local",
        help="Environment to run tests against"
    )


@pytest.fixture(scope="session")
def test_config(request) -> Dict[str, Any]:
    """Session-scoped test configuration."""
    return {
        "browser": request.config.getoption("--browser"),
        "headless": request.config.getoption("--headless"),
        "environment": request.config.getoption("--environment"),
    }


@pytest.fixture(scope="function")
def driver(request, test_config):
    """Enhanced driver fixture with comprehensive setup and teardown."""
    test_name = request.node.name
    test_id = f"test_{int(time.time())}"
    
    # Log test start
    log_test_start(test_name, test_id)
    start_time = time.time()
    
    try:
        # Create driver with enhanced factory
        browser = BrowserType(test_config["browser"])
        driver_tuple = get_driver(browser=browser)
        
        # Add test metadata to driver
        if hasattr(driver_tuple[0], 'test_metadata'):
            driver_tuple[0].test_metadata = {
                "test_name": test_name,
                "test_id": test_id,
                "start_time": start_time
            }
        
        yield driver_tuple
        
    except Exception as e:
        test_logger.log_error(e, {"test_name": test_name, "phase": "driver_setup"})
        raise
    
    finally:
        # Cleanup and logging
        try:
            duration = time.time() - start_time
            
            # Take screenshot on failure
            if request.node.rep_call.failed and settings.screenshot_on_failure:
                screenshot_path = settings.screenshots_dir / f"{test_name}_failure.png"
                try:
                    driver_tuple[0].save_screenshot(str(screenshot_path))
                    allure.attach.file(str(screenshot_path), name="Failure Screenshot", attachment_type=allure.attachment_type.PNG)
                except:
                    pass
            
            # Quit driver
            webdriver_factory.quit_all_drivers()
            
            # Log test end
            status = "PASSED" if not request.node.rep_call.failed else "FAILED"
            log_test_end(test_name, status, duration, test_id)
            
        except Exception as e:
            test_logger.log_error(e, {"test_name": test_name, "phase": "driver_teardown"})


@pytest.fixture(scope="session")
def database_setup():
    """Session-scoped database setup."""
    # Setup test database if needed
    yield db_manager
    # Cleanup
    db_manager.close_all_connections()


@pytest.fixture(scope="function") 
def test_data():
    """Function-scoped test data fixture."""
    return test_data_manager


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for reporting."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)