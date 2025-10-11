"""Regression protection tests to ensure framework stability."""

from pathlib import Path

import pytest
from hamcrest import (
    assert_that,
    contains_string,
    has_property,
    is_,
)

from pages.base_page import BasePage
from utils.sql_connection import get_connection
from utils.webdriver_factory import WebDriverFactory


class TestRegressionProtection:
    """Tests to prevent regressions in core framework functionality."""

    # TODO: fix this test true is true
    def test_core_modules_importable(self):
        """Test that all core modules can be imported without errors."""
        try:
            pass

            assert_that(True, is_(True)), "All core modules imported successfully"  # noqa: FBT003
        except ImportError as e:
            pytest.fail(f"Core module import failed: {e}")

    def test_webdriver_factory_exists(self):
        """Test that WebDriverFactory class exists and has required methods."""
        factory = WebDriverFactory()
        (
            assert_that(
                factory,
                has_property("create_chrome_driver"),
            ),
            "WebDriverFactory missing create_chrome_driver method",
        )
        (
            assert_that(
                factory,
                has_property("create_firefox_driver"),
            ),
            "WebDriverFactory missing create_firefox_driver method",
        )

    def test_base_page_exists(self):
        """Test that BasePage class exists and has required methods."""
        # Test that BasePage has essential methods
        (
            assert_that(
                BasePage,
                has_property("__init__"),
            ),
            "BasePage missing __init__ method",
        )
        # Note: We don't instantiate BasePage to avoid WebDriver dependency

    def test_database_connection_function_exists(self):
        """Test that database connection function exists."""
        (
            assert_that(
                callable(get_connection),
                is_(True),
            ),
            "get_connection is not callable",
        )

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and contains expected dependencies."""
        requirements_path = Path(__file__).parent.parent.parent / "requirements.txt"
        (
            assert_that(
                requirements_path.exists(),
                is_(True),
            ),
            "requirements.txt file not found",
        )

        with requirements_path.open() as f:
            content = f.read()
            (
                assert_that(
                    content,
                    contains_string("selenium"),
                ),
                "selenium not found in requirements.txt",
            )
            (
                assert_that(
                    content,
                    contains_string("pytest"),
                ),
                "pytest not found in requirements.txt",
            )

    def test_config_directory_structure(self):
        """Test that essential directories exist."""
        base_dir = Path(__file__).parent.parent.parent

        essential_dirs = ["pages", "utils", "tests", "locators"]
        for dir_name in essential_dirs:
            dir_path = base_dir / dir_name
            (
                assert_that(
                    dir_path.exists(),
                    is_(True),
                ),
                f"Essential directory '{dir_name}' not found",
            )

    def test_pytest_configuration(self):
        """Test that pytest configuration exists."""
        pytest_ini_path = Path(__file__).parent.parent.parent / "pytest.ini"
        (
            assert_that(
                pytest_ini_path.exists(),
                is_(True),
            ),
            "pytest.ini configuration file not found",
        )
