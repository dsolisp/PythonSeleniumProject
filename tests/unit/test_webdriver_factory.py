from unittest.mock import Mock, patch

import pytest
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    none,
)

from utils.webdriver_factory import (
    DatabaseFactory,
    WebDriverFactory,
    cleanup_driver_and_database,
    get_driver,
)

"""
Real Unit Tests for WebDriver Factory Functions
Testing actual factory logic and configuration.
"""


class TestWebDriverFactory:
    """Test WebDriverFactory methods."""

    @patch("utils.webdriver_factory.ChromeDriverManager")
    @patch("utils.webdriver_factory.webdriver.Chrome")
    def test_create_chrome_driver_basic(self, mock_chrome, mock_manager):
        """Test Chrome driver creation with basic options."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"

        result = WebDriverFactory.create_chrome_driver()

        assert_that(result, equal_to(mock_driver))
        mock_chrome.assert_called_once()
        # Verify anti-detection script was executed
        mock_driver.execute_script.assert_called_once()
        mock_driver.maximize_window.assert_called_once()

    @patch("utils.webdriver_factory.ChromeDriverManager")
    @patch("utils.webdriver_factory.webdriver.Chrome")
    def test_create_chrome_driver_headless(self, mock_chrome, mock_manager):
        """Test Chrome driver creation in headless mode."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"

        result = WebDriverFactory.create_chrome_driver(headless=True)

        assert_that(result, equal_to(mock_driver))
        # Should not maximize window in headless mode
        mock_driver.maximize_window.assert_not_called()

    @patch("utils.webdriver_factory.ChromeDriverManager")
    @patch("utils.webdriver_factory.webdriver.Chrome")
    def test_create_chrome_driver_window_size(self, mock_chrome, mock_manager):
        """Test Chrome driver creation with custom window size."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/chromedriver"

        result = WebDriverFactory.create_chrome_driver(window_size=(1024, 768))

        assert_that(result, equal_to(mock_driver))
        # Should not maximize window when size is specified
        mock_driver.maximize_window.assert_not_called()

    @patch("utils.webdriver_factory.GeckoDriverManager")
    @patch("utils.webdriver_factory.webdriver.Firefox")
    def test_create_firefox_driver_basic(self, mock_firefox, mock_manager):
        """Test Firefox driver creation with basic options."""
        mock_driver = Mock()
        mock_firefox.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/geckodriver"

        result = WebDriverFactory.create_firefox_driver()

        assert_that(result, equal_to(mock_driver))
        mock_firefox.assert_called_once()
        mock_driver.maximize_window.assert_called_once()

    @patch("utils.webdriver_factory.EdgeChromiumDriverManager")
    @patch("utils.webdriver_factory.webdriver.Edge")
    def test_create_edge_driver_basic(self, mock_edge, mock_manager):
        """Test Edge driver creation with basic options."""
        mock_driver = Mock()
        mock_edge.return_value = mock_driver
        mock_manager.return_value.install.return_value = "/path/to/edgedriver"

        result = WebDriverFactory.create_edge_driver()

        assert_that(result, equal_to(mock_driver))
        mock_edge.assert_called_once()
        mock_driver.execute_script.assert_called_once()
        mock_driver.maximize_window.assert_called_once()


class TestDatabaseFactory:
    """Test DatabaseFactory methods."""

    @patch("utils.webdriver_factory.os.path.exists")
    @patch("utils.webdriver_factory.sqlite3.connect")
    def test_create_database_connection_default_path(self, mock_connect, mock_exists):
        """Test database connection with default path."""
        mock_exists.return_value = True
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        result = DatabaseFactory.create_database_connection()

        assert_that(result, equal_to(mock_conn))
        assert_that(
            mock_conn.row_factory,
            equal_to(mock_connect.return_value.row_factory),
        )

    @patch("utils.webdriver_factory.os.path.exists")
    def test_create_database_connection_file_not_found(self, mock_exists):
        """Test database connection when file doesn't exist."""
        mock_exists.return_value = False

        result = DatabaseFactory.create_database_connection()

        assert_that(result, is_(none()))

    @patch("utils.webdriver_factory.sqlite3.connect")
    def test_create_database_connection_custom_path(self, mock_connect):
        """Test database connection with custom path."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        result = DatabaseFactory.create_database_connection("/custom/path.db")

        assert_that(result, equal_to(mock_conn))
        mock_connect.assert_called_with("/custom/path.db")

    @patch("utils.webdriver_factory.sqlite3.connect")
    def test_create_database_connection_sqlite_error(self, mock_connect):
        """Test database connection handles sqlite3.Error."""
        mock_connect.side_effect = Exception("Connection failed")

        result = DatabaseFactory.create_database_connection("/custom/path.db")

        assert_that(result, is_(none()))


class TestGetDriverFunction:
    """Test get_driver function."""

    @patch("utils.webdriver_factory.WebDriverFactory.create_chrome_driver")
    @patch("utils.webdriver_factory.DatabaseFactory.create_database_connection")
    def test_get_driver_chrome(self, mock_db, mock_chrome):
        """Test get_driver creates Chrome driver."""
        mock_driver = Mock()
        mock_database = Mock()
        mock_chrome.return_value = mock_driver
        mock_db.return_value = mock_database

        driver, database = get_driver("chrome")

        assert_that(driver, equal_to(mock_driver))
        assert_that(database, equal_to(mock_database))
        mock_chrome.assert_called_once_with(headless=False)
        mock_driver.implicitly_wait.assert_called_once()

    @patch("utils.webdriver_factory.WebDriverFactory.create_firefox_driver")
    @patch("utils.webdriver_factory.DatabaseFactory.create_database_connection")
    def test_get_driver_firefox(self, mock_db, mock_firefox):
        """Test get_driver creates Firefox driver."""
        mock_driver = Mock()
        mock_database = Mock()
        mock_firefox.return_value = mock_driver
        mock_db.return_value = mock_database

        driver, database = get_driver("firefox", headless=True)

        assert_that(driver, equal_to(mock_driver))
        assert_that(database, equal_to(mock_database))
        mock_firefox.assert_called_once_with(headless=True)

    @patch("utils.webdriver_factory.WebDriverFactory.create_edge_driver")
    @patch("utils.webdriver_factory.DatabaseFactory.create_database_connection")
    def test_get_driver_edge(self, mock_db, mock_edge):
        """Test get_driver creates Edge driver."""
        mock_driver = Mock()
        mock_database = Mock()
        mock_edge.return_value = mock_driver
        mock_db.return_value = mock_database

        driver, database = get_driver("edge", window_size=(800, 600))

        assert_that(driver, equal_to(mock_driver))
        assert_that(database, equal_to(mock_database))
        mock_edge.assert_called_once_with(headless=False, window_size=(800, 600))

    def test_get_driver_unsupported_browser(self):
        """Test get_driver raises error for unsupported browser."""
        with pytest.raises(ValueError, match="Unsupported browser: safari"):
            get_driver("safari")

    @patch("utils.webdriver_factory.os.getenv")
    @patch("utils.webdriver_factory.WebDriverFactory.create_chrome_driver")
    @patch("utils.webdriver_factory.DatabaseFactory.create_database_connection")
    def test_get_driver_implicit_wait_from_env(self, mock_db, mock_chrome, mock_getenv):
        """Test get_driver uses implicit wait from environment."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_db.return_value = None
        mock_getenv.return_value = "15"  # Custom timeout

        _driver, _database = get_driver("chrome")

        mock_driver.implicitly_wait.assert_called_once_with(15)


class TestCleanupFunction:
    """Test cleanup_driver_and_database function."""

    def test_cleanup_driver_and_database_success(self):
        """Test successful cleanup of driver and database."""
        mock_driver = Mock()
        mock_database = Mock()

        cleanup_driver_and_database(mock_driver, mock_database)

        mock_driver.quit.assert_called_once()
        mock_database.close.assert_called_once()

    def test_cleanup_driver_exception(self):
        """Test cleanup handles driver exceptions."""
        mock_driver = Mock()
        mock_driver.quit.side_effect = Exception("Driver quit failed")
        mock_database = Mock()

        # Should not raise exception
        cleanup_driver_and_database(mock_driver, mock_database)

        mock_database.close.assert_called_once()

    def test_cleanup_database_exception(self):
        """Test cleanup handles database exceptions."""
        mock_driver = Mock()
        mock_database = Mock()
        mock_database.close.side_effect = Exception("Database close failed")

        # Should not raise exception
        cleanup_driver_and_database(mock_driver, mock_database)

        mock_driver.quit.assert_called_once()

    def test_cleanup_none_values(self):
        """Test cleanup handles None values."""
        # Should not raise exception
        cleanup_driver_and_database(None, None)

    def test_cleanup_database_no_close_method(self):
        """Test cleanup handles database without close method."""
        mock_driver = Mock()
        mock_database = object()  # Object without close method

        # Should not raise exception
        cleanup_driver_and_database(mock_driver, mock_database)

        mock_driver.quit.assert_called_once()
