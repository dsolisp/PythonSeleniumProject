# API testing guide

> **Scope:** This repo’s **canonical REST API examples** live in `tests/backend/test_api.py` (SWAPI, `requests`, **PyHamcrest**). Paths like `tests/api/` appear only in older notes—use `tests/backend/` as the source of truth. **Allure** is supported at the framework level (`settings.ENABLE_ALLURE`, `conftest.py`) but the checked-in API suite does not decorate every call with `allure.step`; add reporting where you need it.

## Overview

- **Integration-style HTTP tests** with `requests.Session`
- **Readable assertions** via PyHamcrest (`assert_that`, `has_key`, `equal_to`, …)
- **Markers**: `@pytest.mark.api` (see `pytest.ini`)
- **Base URL** from `config.constants.URLS` (`SWAPI`), not a hard-coded `api.example.com`

## When to use

- Contract / schema checks on JSON payloads  
- Negative paths (404, empty search) and simple SLA timing  
- Patterns you can copy for other public APIs (swap `BASE_URL`)

## Source of truth (`tests/backend/test_api.py`)

```python
import pytest
import requests
import urllib3
from hamcrest import assert_that, equal_to, greater_than, has_key, is_not

from config.constants import URLS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = URLS.SWAPI


@pytest.mark.api
class TestSwapiAPI:
    def setup_method(self):
        self.session = requests.Session()
        self.session.verify = False

    def teardown_method(self):
        self.session.close()

    def test_example_1_fetches_specific_person(self):
        res = self.session.get(f"{BASE_URL}/people/1")
        assert_that(res.status_code, equal_to(200))
        body = res.json()
        assert_that(body, has_key("name"))
        assert_that(body["name"], equal_to("Luke Skywalker"))
```

See the same file for pagination, search, schema key lists, response-time bounds, and 404 cases.

## Running API tests

```bash
# Marker (matches pytest.ini)
pytest tests/backend/test_api.py -m api -v

# Single class
pytest tests/backend/test_api.py::TestSwapiAPI -v

# Via runner (after run_tests.py points at this path)
python scripts/run_tests.py --type api
```

### Allure (optional)

When `ENABLE_ALLURE=true` (default in `config/settings.py`), UI and other suites attach rich steps. For API-only runs you can still collect Allure results if you add decorators/steps to your tests:

```bash
pytest tests/backend/test_api.py -m api -v --alluredir=var/allure-results --clean-alluredir
allure serve var/allure-results
```

Fast console-only runs (no Allure steps in the SWAPI file today—this only affects suites that branch on `settings.ENABLE_ALLURE`):

```bash
ENABLE_ALLURE=false pytest tests/backend/test_api.py -m api -v
```

## PyHamcrest essentials

```python
from hamcrest import assert_that, equal_to, greater_than, has_key, is_not

assert_that(res.status_code, equal_to(200))
assert_that(body["count"], greater_than(0))
assert_that(body["next"], is_not(None))
```

See [PyHamcrest](https://pyhamcrest.readthedocs.io/) for `has_entries`, `contains_string`, etc.

## Settings touchpoints

- `config/settings.py` — `ENABLE_ALLURE`, `SWAPI_BASE_URL` (env override), other URL defaults  
- `config/constants.py` — `URLS.SWAPI` used by the sample suite  

## Related docs

- [Test analytics](TEST_ANALYTICS.md) — flaky history (`pytest-history`)  
- [Analytics & reporting](ANALYTICS_AND_REPORTING.md) — HTML / JSON reports  
- [Error recovery](ERROR_RECOVERY_AND_MONITORING.md) — retries for flaky network (stdlib helper)  

## File locations

| Item        | Path |
| ----------- | ---- |
| API tests   | `tests/backend/test_api.py` |
| Settings    | `config/settings.py` |
| URL constants | `config/constants.py` |
| Structured logging (other suites) | `utils/structured_logger.py` |

---

**Summary:** Copy the SWAPI suite’s shape—session per test method, Hamcrest assertions, explicit markers—and extend with Allure or logging only where it pays for your team.
