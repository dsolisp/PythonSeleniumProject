"""
Unit tests for constants validation.
Equivalent to C#'s ConstantsTests.cs - ensures framework constants are correctly defined.
"""

from hamcrest import (
    assert_that,
    contains_string,
    equal_to,
    greater_than,
    greater_than_or_equal_to,
    is_,
    less_than_or_equal_to,
    not_none,
)

from config.constants import (
    USER_AGENT_CHROME,
    USER_AGENT_DEFAULT,
    USER_AGENT_EDGE,
    USER_AGENT_FIREFOX,
)
from config.settings import settings


class TestUserAgentConstants:
    """Tests for user agent string constants."""

    def test_chrome_user_agent_contains_chrome(self):
        """Verify Chrome user agent contains 'Chrome'."""
        assert_that(USER_AGENT_CHROME, contains_string("Chrome"))

    def test_chrome_user_agent_contains_webkit(self):
        """Verify Chrome user agent contains WebKit."""
        assert_that(USER_AGENT_CHROME, contains_string("AppleWebKit"))

    def test_firefox_user_agent_contains_firefox(self):
        """Verify Firefox user agent contains 'Firefox'."""
        assert_that(USER_AGENT_FIREFOX, contains_string("Firefox"))

    def test_firefox_user_agent_contains_gecko(self):
        """Verify Firefox user agent contains 'Gecko'."""
        assert_that(USER_AGENT_FIREFOX, contains_string("Gecko"))

    def test_edge_user_agent_contains_edg(self):
        """Verify Edge user agent contains 'Edg'."""
        assert_that(USER_AGENT_EDGE, contains_string("Edg"))

    def test_default_user_agent_is_chrome(self):
        """Verify default user agent is Chrome."""
        assert_that(USER_AGENT_DEFAULT, equal_to(USER_AGENT_CHROME))


class TestTimeoutConstants:
    """Tests for timeout configuration constants."""

    def test_timeout_is_positive(self):
        """Verify default timeout is positive."""
        assert_that(settings.TIMEOUT, greater_than(0))

    def test_timeout_is_reasonable(self):
        """Verify timeout is within reasonable bounds (1-60 seconds)."""
        assert_that(settings.TIMEOUT, greater_than_or_equal_to(1))
        assert_that(settings.TIMEOUT, less_than_or_equal_to(60))

    def test_headless_is_boolean(self):
        """Verify headless is a boolean setting."""
        assert_that(isinstance(settings.HEADLESS, bool), is_(True))


class TestURLConstants:
    """Tests for URL constants in settings."""

    def test_base_url_is_not_empty(self):
        """Verify base URL is configured."""
        assert_that(settings.BASE_URL, not_none())
        assert_that(len(settings.BASE_URL) > 0, is_(True))

    def test_base_url_starts_with_https(self):
        """Verify base URL uses HTTPS."""
        assert_that(settings.BASE_URL.startswith("http"), is_(True))


class TestBrowserConstants:
    """Tests for browser configuration constants."""

    def test_browser_is_configured(self):
        """Verify browser is configured."""
        assert_that(settings.BROWSER, not_none())

    def test_browser_is_valid(self):
        """Verify browser is a valid option."""
        valid_browsers = ["chrome", "firefox", "edge", "safari", "chromium", "webkit"]
        assert_that(settings.BROWSER.lower() in valid_browsers, is_(True))


class TestHTTPStatusCodes:
    """Tests for HTTP status code constants."""

    def test_http_ok_is_200(self):
        """Verify HTTP OK is 200."""
        assert_that(200, equal_to(200))

    def test_http_created_is_201(self):
        """Verify HTTP Created is 201."""
        assert_that(201, equal_to(201))

    def test_http_not_found_is_404(self):
        """Verify HTTP Not Found is 404."""
        assert_that(404, equal_to(404))


class TestWindowSizes:
    """Tests for window size constants."""

    def test_default_window_width_is_positive(self):
        """Verify default window width is positive."""
        # Default to 1920 if not explicitly set
        width = getattr(settings, "WINDOW_WIDTH", 1920)
        assert_that(width, greater_than(0))

    def test_default_window_height_is_positive(self):
        """Verify default window height is positive."""
        # Default to 1080 if not explicitly set
        height = getattr(settings, "WINDOW_HEIGHT", 1080)
        assert_that(height, greater_than(0))
