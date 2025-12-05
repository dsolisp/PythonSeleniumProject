# Python Test Automation Cheat Sheet

> Quick reference for pytest, Selenium, Playwright, and automation tools.

---

## 📋 Table of Contents

- [pytest Commands](#pytest-commands)
- [pytest-history (Flaky Detection)](#pytest-history-flaky-detection)
- [Selenium WebDriver](#selenium-webdriver)
- [Playwright](#playwright)
- [Test Data](#test-data)
- [Assertions](#assertions)
- [Debugging](#debugging)
- [Performance Testing](#performance-testing)
- [CI/CD](#cicd)
- [Code Quality](#code-quality)

---

## pytest Commands

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific directory
pytest tests/unit/

# Run specific file
pytest tests/unit/test_example.py

# Run specific test function
pytest tests/unit/test_example.py::test_function_name

# Run specific test class
pytest tests/unit/test_example.py::TestClassName

# Run specific test in class
pytest tests/unit/test_example.py::TestClassName::test_method
```

### Output & Verbosity

```bash
# Verbose output (show test names)
pytest -v

# Extra verbose (show captured stdout)
pytest -vv

# Show print statements
pytest -s

# Short traceback on failure
pytest --tb=short

# One-line per test
pytest --tb=line

# No traceback
pytest --tb=no
```

### Filtering Tests

```bash
# Run tests matching keyword
pytest -k "search"

# Run tests with marker
pytest -m "smoke"

# Exclude marker
pytest -m "not slow"

# Combine markers
pytest -m "smoke and not flaky"

# Run only failed tests from last run
pytest --lf

# Run failed first, then passing
pytest --ff
```

### Reports

```bash
# HTML report
pytest --html=reports/report.html --self-contained-html

# JSON report
pytest --json-report --json-report-file=reports/results.json

# Coverage report
pytest --cov=pages --cov=utils --cov-report=html

# JUnit XML (for CI)
pytest --junitxml=reports/junit.xml

# Combined example
pytest tests/ -v --html=report.html --json-report --cov=pages
```

### Parallel Execution

```bash
# Run with 4 workers
pytest -n 4

# Auto-detect CPU cores
pytest -n auto

# Distribute by test file
pytest -n 4 --dist=loadfile
```

### Useful Options

```bash
# Stop on first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Run N times (for flaky detection)
pytest --count=5

# Rerun failed tests
pytest --reruns 3 --reruns-delay 1

# Headless mode (custom option)
pytest --headless
```

---

## pytest-history (Flaky Detection)

```bash
# View all test runs
pytest-history list runs

# View flaky tests (inconsistent pass/fail)
pytest-history flakes

# View results for specific run
pytest-history list results 1

# Use via run_tests.py
python run_tests.py --type unit --flaky
```

**How it works**: Every `pytest` run automatically stores results in `.test-results.db`.

---

## Selenium WebDriver

### Driver Setup

```python
from utils.webdriver_factory import WebDriverFactory

# Chrome
driver = WebDriverFactory.create_chrome_driver(headless=True)

# Firefox
driver = WebDriverFactory.create_firefox_driver(headless=True)

# Always quit when done
driver.quit()
```

### Finding Elements

```python
from selenium.webdriver.common.by import By

# By ID
element = driver.find_element(By.ID, "username")

# By CSS selector
element = driver.find_element(By.CSS_SELECTOR, "input.login-field")

# By XPath
element = driver.find_element(By.XPATH, "//button[@type='submit']")

# By class name
element = driver.find_element(By.CLASS_NAME, "btn-primary")

# By link text
element = driver.find_element(By.LINK_TEXT, "Sign Up")

# Find multiple
elements = driver.find_elements(By.CSS_SELECTOR, ".result-item")
```

### Element Interactions

```python
# Click
element.click()

# Type text
element.send_keys("hello world")

# Clear and type
element.clear()
element.send_keys("new text")

# Get text
text = element.text

# Get attribute
href = element.get_attribute("href")
value = element.get_attribute("value")

# Check state
element.is_displayed()
element.is_enabled()
element.is_selected()

# Submit form
element.submit()
```

### Waits

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)

# Wait for element visible
element = wait.until(EC.visibility_of_element_located((By.ID, "result")))

# Wait for element clickable
element = wait.until(EC.element_to_be_clickable((By.ID, "submit")))

# Wait for element present (in DOM)
element = wait.until(EC.presence_of_element_located((By.ID, "loading")))

# Wait for element to disappear
wait.until(EC.invisibility_of_element((By.ID, "spinner")))

# Wait for text in element
wait.until(EC.text_to_be_present_in_element((By.ID, "status"), "Complete"))

# Wait for page title
wait.until(EC.title_contains("Dashboard"))
```

### Navigation

```python
# Open URL
driver.get("https://example.com")

# Refresh
driver.refresh()

# Back/Forward
driver.back()
driver.forward()

# Get current URL
url = driver.current_url

# Get page title
title = driver.title

# Get page source
html = driver.page_source
```

### Screenshots

```python
# Full page
driver.save_screenshot("screenshot.png")

# Element only
element.screenshot("element.png")

# As base64 (for reports)
base64_img = driver.get_screenshot_as_base64()
```

### Frames & Windows

```python
# Switch to frame
driver.switch_to.frame("frame_name")
driver.switch_to.frame(0)  # by index

# Back to main content
driver.switch_to.default_content()

# Switch to window
driver.switch_to.window(driver.window_handles[-1])

# Close current window
driver.close()
```

---

## Playwright

### Basic Usage

```python
from playwright.sync_api import sync_playwright, Page, expect

# Setup
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Navigate
    page.goto("https://example.com")

    # Interact
    page.fill("#username", "testuser")
    page.click("button[type='submit']")

    browser.close()
```

### With pytest

```python
# conftest.py provides 'page' fixture automatically
def test_example(page: Page):
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
```

### Locators

```python
# By role (recommended)
page.get_by_role("button", name="Submit")
page.get_by_role("link", name="Sign Up")

# By text
page.get_by_text("Welcome")

# By label
page.get_by_label("Email")

# By placeholder
page.get_by_placeholder("Enter email")

# By CSS/XPath
page.locator("css=.btn-primary")
page.locator("xpath=//button[@type='submit']")
```

### Actions

```python
# Click
page.click("#submit")

# Fill input
page.fill("#email", "test@example.com")

# Type with delay
page.type("#search", "query", delay=100)

# Select dropdown
page.select_option("#country", "USA")

# Check/uncheck
page.check("#agree")
page.uncheck("#newsletter")

# Hover
page.hover(".menu-item")

# Press key
page.press("#input", "Enter")
```

### Assertions (expect)

```python
from playwright.sync_api import expect

# Element visible
expect(page.locator("#result")).to_be_visible()

# Text content
expect(page.locator("h1")).to_have_text("Welcome")
expect(page.locator("p")).to_contain_text("success")

# Attribute
expect(page.locator("input")).to_have_attribute("type", "email")

# Count
expect(page.locator(".item")).to_have_count(5)

# Page title
expect(page).to_have_title("Dashboard")

# URL
expect(page).to_have_url("https://example.com/dashboard")
```

### Screenshots

```python
# Full page
page.screenshot(path="screenshot.png")

# Element only
page.locator("#chart").screenshot(path="chart.png")

# Full page with scrolling
page.screenshot(path="full.png", full_page=True)
```

---

## Test Data

### Loading Data

```python
from utils.test_data_manager import DataManager

manager = DataManager()

# Load JSON/YAML/CSV
data = manager.load_test_data('test_data')

# Access nested data
username = data['users']['admin']['username']
scenarios = data['search_scenarios']
```

### Data Files

```json
// data/test_data.json
{
    "users": {
        "admin": {"username": "admin", "password": "secret"}
    },
    "search_scenarios": [
        {"query": "python", "expected": "Python"}
    ]
}
```

```yaml
# data/test_data.yaml
users:
  admin:
    username: admin
    password: secret
```

### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize("username,password,expected", [
    ("admin", "secret", True),
    ("user", "wrong", False),
])
def test_login(page, username, password, expected):
    # Test runs once per parameter set
    pass
```

### Faker (Dynamic Data)

```python
from faker import Faker

fake = Faker()

email = fake.email()           # random@example.com
name = fake.name()             # John Smith
address = fake.address()       # 123 Main St
phone = fake.phone_number()    # 555-123-4567
```

---

## Assertions

### pytest Assertions

```python
# Equality
assert result == expected
assert result != unexpected

# Truthiness
assert condition
assert not condition

# Containment
assert "error" in message
assert item in collection

# Type checking
assert isinstance(result, dict)

# None checking
assert result is None
assert result is not None

# Approximate equality (floats)
assert result == pytest.approx(3.14, rel=0.01)
```

### PyHamcrest Assertions

```python
from hamcrest import assert_that, equal_to, contains_string, has_length

assert_that(result, equal_to(expected))
assert_that(text, contains_string("success"))
assert_that(items, has_length(5))

# Collections
from hamcrest import has_item, has_items, contains_exactly

assert_that(results, has_item("Python"))
assert_that(results, has_items("Python", "Java"))
```

---

## Debugging

### Print Debugging

```python
# Show print output
pytest -s

# Add prints
print(f"DEBUG: value = {value}")
```

### Breakpoints

```python
# Built-in debugger
import pdb; pdb.set_trace()

# With pytest
pytest --pdb  # Drop into debugger on failure

# VS Code - just set breakpoints in editor
```

### Screenshots on Failure

```python
# In conftest.py (already configured)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    if rep.failed:
        driver.save_screenshot(f"failure_{item.name}.png")
```

### Verbose Logging

```bash
# See all log output
pytest --log-cli-level=DEBUG

# Log to file
pytest --log-file=test.log --log-file-level=DEBUG
```

---

## Performance Testing

### pytest-benchmark

```python
def test_function_speed(benchmark):
    result = benchmark(my_function, arg1, arg2)
    assert result == expected

# Run benchmarks
pytest tests/performance/ --benchmark-only
```

### Locust (Load Testing)

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class WebUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def load_homepage(self):
        self.client.get("/")

    @task(3)  # 3x more likely
    def search(self):
        self.client.get("/search?q=test")
```

```bash
# Run Locust
locust -f tests/performance/locustfile.py --host=https://example.com

# Headless mode
locust -f locustfile.py --headless -u 100 -r 10 -t 60s
```

---

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/unit/ -v --cov
      - run: pytest-history flakes || true
```

### Environment Variables

```bash
# In CI
export HEADLESS=true
export ENVIRONMENT=staging

# In tests
import os
headless = os.getenv("HEADLESS", "false").lower() == "true"
```

---

## Code Quality

### Ruff (Linting & Formatting)

```bash
# Check for issues
ruff check .

# Fix automatically
ruff check --fix .

# Format code
ruff format .

# Check formatting
ruff format --check .
```

### mypy (Type Checking)

```bash
# Check types
mypy .

# Ignore missing imports
mypy . --ignore-missing-imports
```

### bandit (Security)

```bash
# Security scan
bandit -r . -f json -o security.json

# Skip specific checks
bandit -r . -s B101,B105
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║                 ESSENTIAL COMMANDS                         ║
╠═══════════════════════════════════════════════════════════╣
║ pytest tests/ -v              # Run all tests             ║
║ pytest -k "search"            # Filter by keyword         ║
║ pytest -m smoke               # Run smoke tests           ║
║ pytest --html=report.html     # HTML report               ║
║ pytest-history flakes         # Check flaky tests         ║
║ python run_tests.py --flaky   # Run with flaky summary    ║
║ ruff check . && ruff format . # Lint & format             ║
╚═══════════════════════════════════════════════════════════╝
```

---

## Related Documentation

- [Zero-to-Hero Tutorial](ZERO_TO_HERO_TUTORIAL.md) - Learn from scratch
- [Test Analytics](TEST_ANALYTICS.md) - Flaky detection deep dive
- [Playwright Integration](PLAYWRIGHT_INTEGRATION.md) - Playwright details
- [Error Recovery](ERROR_RECOVERY_AND_MONITORING.md) - Retry logic
