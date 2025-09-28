"""
Enhanced conftest.py with comprehensive fixtures and modern pytest practices.
"""

import pytest
import os
import time
from typing import Dict, Any, Generator, Optional
from pathlib import Path

from config.simple_settings import settings
from utils.webdriver_factory import get_driver
from utils.sql_connection import close_connection


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


@pytest.fixture(scope="session")
def test_config(request) -> Dict[str, Any]:
    """Session-scoped test configuration."""
    return {
        "browser": request.config.getoption("--browser"),
        "headless": request.config.getoption("--headless"),
    }


@pytest.fixture
def driver(request, test_config):
    """Enhanced driver fixture with better error handling and cleanup."""
    test_name = request.node.name
    start_time = time.time()
    
    try:
        # Setup, opens the browser and opens the sql connection
        driver = get_driver()
        yield driver
        
    except Exception as e:
        print(f"Error in driver setup for {test_name}: {e}")
        raise
    
    finally:
        # Enhanced teardown with better error handling
        try:
            duration = time.time() - start_time
            print(f"Test {test_name} completed in {duration:.2f}s")
            
            # Take screenshot on failure if configured
            if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
                if settings.SCREENSHOT_ON_FAILURE:
                    try:
                        screenshot_path = settings.SCREENSHOTS_DIR / f"{test_name}_failure.png"
                        driver[0].save_screenshot(str(screenshot_path))
                        print(f"Failure screenshot saved: {screenshot_path}")
                    except Exception as screenshot_error:
                        print(f"Could not save screenshot: {screenshot_error}")
            
            # Teardown, closes the browser and closes the sql connection
            driver[0].quit()
            close_connection(driver[1])
            
        except Exception as e:
            print(f"Error in driver teardown for {test_name}: {e}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for reporting."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
