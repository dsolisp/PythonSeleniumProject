"""
Constants for the test automation framework.

This file centralizes commonly used values to maintain DRY principles.
User agent strings are defined here to avoid duplication across factory classes.
"""

# User agent strings for different browsers
# These mimic real browser user agents to avoid bot detection
USER_AGENT_CHROME = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/119.0.0.0 Safari/537.36"
)

USER_AGENT_FIREFOX = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:119.0) "
    "Gecko/20100101 Firefox/119.0"
)

USER_AGENT_EDGE = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
)

# Default user agent (Chrome) for general use
USER_AGENT_DEFAULT = USER_AGENT_CHROME
