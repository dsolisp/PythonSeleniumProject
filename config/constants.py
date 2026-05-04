"""
Constants for the test automation framework.

This file centralizes commonly used values to maintain DRY principles.
"""

import os
from pathlib import Path


class TIMEOUTS:
    DEFAULT = 30000
    NAVIGATION = 30000
    ACTION = 10000
    EXPECT = 5000
    API = 10000
    SHORT = 3000
    LONG = 60000
    ANIMATION = 500


class URLS:
    SAUCE_DEMO = "https://www.saucedemo.com"
    JSON_PLACEHOLDER = "https://jsonplaceholder.typicode.com"
    SWAPI = "https://swapi.dev/api"
    PRACTICE_APP = os.getenv("PRACTICE_BASE_URL", "http://localhost:8080")


class HTTP_STATUS:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500


class BROWSERS:
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"


class USER_AGENTS:
    CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    FIREFOX = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    EDGE = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    DEFAULT = CHROME


class VIEWPORTS:
    DESKTOP = {"width": 1920, "height": 1080}
    LAPTOP = {"width": 1366, "height": 768}
    TABLET = {"width": 768, "height": 1024}
    MOBILE = {"width": 375, "height": 667}


class PATHS:
    DB = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "app.db",
    )
