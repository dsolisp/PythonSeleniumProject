# Building a Professional Python Test Automation Framework

A step-by-step tutorial to recreate this Selenium/Playwright test automation portfolio project from scratch.

## Prerequisites

- **Python**: 3.9 or higher
- **OS**: macOS, Linux, or Windows
- **IDE**: VS Code (recommended) with Python extension
- **Git**: For version control
- **Browser**: Chrome, Firefox, or Edge installed

## Step 1: Project Setup

### Create Project Structure

```bash
# Create project directory
mkdir PythonSeleniumProject && cd PythonSeleniumProject

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Create directory structure
mkdir -p pages utils tests/{unit,web,api,performance} data/{test_data,results} reports scripts documentation
```

**Why this structure?**
- `pages/` - Page Object Model classes (separates UI interaction from tests)
- `utils/` - Reusable utilities (promotes DRY principle)
- `tests/` - Organized by test type for easy filtering
- `data/` - Test data separated from code (data-driven testing)
- `reports/` - Output directory for test reports
- `scripts/` - CI/CD and automation scripts

### Expected Output
```
PythonSeleniumProject/
├── pages/
├── utils/
├── tests/
│   ├── unit/
│   ├── web/
│   ├── api/
│   └── performance/
├── data/
│   ├── test_data/
│   └── results/
├── reports/
├── scripts/
└── documentation/
```

## Step 2: Install Dependencies

### Create requirements.txt

```bash
cat > requirements.txt << 'EOF'
# Browser Automation
selenium>=4.27.1
playwright>=1.49.1
webdriver-manager>=4.0.2

# Test Framework
pytest>=8.3.5
pytest-html>=4.1.1
pytest-json-report>=1.5.0
pytest-xdist>=3.6.1
pytest-timeout>=2.3.1
pytest-rerunfailures>=15.0

# API Testing
requests>=2.32.3
allure-pytest>=2.13.5

# Visual Testing
Pillow>=11.0.0
pixelmatch>=0.3.0

# Utilities
python-dotenv>=1.0.1
PyYAML>=6.0.1
Jinja2>=3.1.6

# Load Testing
locust>=2.24.0

# Dev Tools
ruff>=0.9.2
mypy>=1.14.1
bandit>=1.7.10
EOF
```

### Install Packages

```bash
pip install -r requirements.txt
playwright install  # Install browser binaries
```

**Verification:**
```bash
python -c "import selenium; import playwright; print('✅ Dependencies installed')"
```

## Step 3: Core Components

### 3.1 WebDriver Factory (`utils/webdriver_factory.py`)

**Purpose**: Create browser instances with consistent configuration.

**Design Pattern**: Factory pattern - encapsulates object creation logic.

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class WebDriverFactory:
    """Factory for creating configured WebDriver instances."""

    SUPPORTED_BROWSERS = {"chrome", "firefox", "edge"}

    @classmethod
    def create_driver(cls, browser="chrome", headless=False):
        """Create a WebDriver instance.

        Args:
            browser: Browser name (chrome, firefox, edge). Default: chrome
            headless: Run in headless mode. Default: False

        Returns:
            WebDriver instance
        """
        browser = browser.lower()

        if browser == "chrome":
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)

        raise ValueError(f"Unsupported browser: {browser}")
```

**Why webdriver-manager?**
- Automatically downloads correct driver version
- No manual driver updates needed
- Works across different OS platforms

### 3.3 Error Handler (`utils/error_handler.py`)

**Purpose**: Readable failures, optional screenshots, and **stdlib-only** retries (no extra retry library in `requirements.txt`).

**What’s in the file today**: `format_error` / `CleanException`, `ScreenshotService`, and `SmartErrorHandler.handle_error` plus `execute_with_retry` (loop + `time.sleep`, capped backoff).

```python
from utils.error_handler import SmartErrorHandler

handler = SmartErrorHandler()

def unstable_operation():
    ...

result = handler.execute_with_retry(
    unstable_operation,
    max_attempts=3,
    initial_delay=1.0,
)
```

**Why stdlib retries?**
- No extra dependency to pin or audit
- Explicit backoff and logging
- Easy to reason about in CI

## Step 4: Page Objects

### Base Page (`pages/base_page.py`)

**Purpose**: Common functionality for all page objects.

**Design Pattern**: Template Method - defines skeleton, subclasses implement details.

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Timeout constants - centralized for consistency
TIMEOUTS.DEFAULT = 20  # Standard operations
TIMEOUTS.LONG = 60  # Slow-loading elements

class BasePage:
    """Base class for all page objects."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUTS.DEFAULT / 1000)

    def find_element(self, locator):
        """Find element immediately. Returns WebElement or None."""
        return self.driver.find_element(*locator)

    def click(self, locator):
        """Click element with wait for clickability."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator, text):
        """Type text into element."""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
```

### SauceDemo Login Page (`pages/sauce/login_page.py`)

**Purpose**: Encapsulate the SauceDemo login flow (this repo’s primary Selenium UI example).

```python
from pages.sauce.login_page import LoginPage
from utils.builders.user_builder import UserBuilder

# Typical usage inside a test (see tests/ui/sauce/test_sauce.py):
def test_login(selenium_driver):
    creds = UserBuilder().standard().build()
    login = LoginPage(selenium_driver).open()
    login.login(creds.username, creds.password)
    assert login.is_logged_in()
```

## Step 5: Write Tests

### 5.1 Unit Tests (`tests/unit/`)

**Purpose**: Test utilities in isolation without browser.

```python
# tests/unit/test_webdriver_factory.py
import pytest
from utils.webdriver_factory import WebDriverFactory

class TestWebDriverFactory:
    """Unit tests for WebDriverFactory."""

    def test_supported_browsers(self):
        """Verify supported browsers list."""
        assert "chrome" in WebDriverFactory.SUPPORTED_BROWSERS
        assert "firefox" in WebDriverFactory.SUPPORTED_BROWSERS

    def test_invalid_browser_raises_error(self):
        """Verify error for unsupported browser."""
        with pytest.raises(ValueError, match="Unsupported browser"):
            WebDriverFactory.create_driver("safari")
```

### 5.2 Web Tests (`tests/ui/`)

**Purpose**: End-to-end browser tests (Selenium), grouped by app (`sauce/`, `practice/`, `visual/`) plus optional Playwright smoke under `tests/ui/playwright/`.

```python
# tests/ui/sauce/test_sauce.py (pattern)
import pytest
from hamcrest import assert_that, is_

from pages.sauce.login_page import LoginPage
from utils.builders.user_builder import UserBuilder


@pytest.mark.web
@pytest.mark.sauce
class TestSauceDemoLogin:
    def test_standard_user_login(self, selenium_driver):
        creds = UserBuilder().standard().build()
        login = LoginPage(selenium_driver).open()
        login.login(creds.username, creds.password)
        assert_that(login.is_logged_in(), is_(True))
```

### 5.3 Run Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with HTML report
pytest tests/ --html=reports/report.html

# Run in parallel (4 workers)
pytest tests/ -n 4

# Run specific markers
pytest tests/ -m "smoke"
```

## Step 6: CI/CD Setup

### Create CI Script (`scripts/run_ci_checks.sh`)

```bash
#!/bin/bash
set -e

echo "🔍 Running linter (ruff)..."
ruff check . --fix

echo "📝 Running type checker (mypy)..."
mypy utils/ pages/ --ignore-missing-imports

echo "🔒 Running security scan (bandit)..."
bandit -r utils/ pages/ -ll

echo "🧪 Running tests..."
pytest tests/unit/ -v

echo "✅ All checks passed!"
```

```bash
chmod +x scripts/run_ci_checks.sh
./scripts/run_ci_checks.sh
```

## Step 7: Advanced Features

### 7.1 Visual Testing

**Purpose**: Detect visual regressions with image comparison.

```python
from PIL import Image
from pixelmatch import pixelmatch

def compare_screenshots(baseline, current):
    """Compare two screenshots, return difference percentage.

    Args:
        baseline: Path to baseline screenshot
        current: Path to current screenshot

    Returns:
        Difference percentage as float
    """
    img1 = Image.open(baseline)
    img2 = Image.open(current)

    diff_pixels = pixelmatch(img1, img2)
    total_pixels = img1.width * img1.height

    return (diff_pixels / total_pixels) * 100
```

### 7.2 Flaky Test Detection (pytest-history)

**Purpose**: Detect flaky tests and track reliability across runs.

```bash
# Run tests - history tracked automatically
pytest tests/

# View flaky tests
pytest-history flakes

# View test run history
pytest-history list runs

# Use via run_tests.py
python run_tests.py --type unit --flaky
```

**How it works**:
- pytest-history automatically stores results in `.test-results.db`
- Flaky tests are identified when they alternate between pass/fail
- No custom code needed - just run pytest normally

### 7.3 Load Testing (Locust)

**Purpose**: Test API performance under load.

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_users(self):
        self.client.get("/api/users")
```

```bash
# Run load test
locust -f tests/performance/locustfile.py --host=https://api.example.com
```

## Running the Full Workflow

```bash
# Complete pipeline: tests + analytics
python run_full_workflow.py
```

**Expected Output:**
```
[WEB] Running Selenium tests...
[API] Running API tests...
[POST] Running test analytics...
⚠️  Flaky Tests (3):
   • test_network: 75% pass rate
🐢 Slow Tests (5):
   • test_api_users: 1.20s
🏆 Test Reliability (Top 5 risks):
   • test_checkout: 65% pass [⚠️ FLAKY]
```

## Design Patterns Used

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| **Page Object Model** | `pages/*.py` | Separates UI locators from test logic |
| **Factory Pattern** | `webdriver_factory.py` | Encapsulates driver creation |
| **Retry helper** | `error_handler.py` | Stdlib exponential backoff (`execute_with_retry`) |
| **Template Method** | `base_page.py` | Common functionality for pages |
| **Singleton** | `structured_logger.py` | Single logger instance |

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `WebDriverException` | Run `playwright install` or check browser version |
| `ImportError` | Run `pip install -r requirements.txt` |
| Tests timeout | Increase `--timeout` or check network |
| Flaky tests | Add waits, check element visibility |

### Useful Commands

```bash
# Check installed packages
pip list

# Run specific test file
pytest tests/unit/test_webdriver_factory.py -v

# Run with debug output
pytest tests/ -v --tb=long

# Generate coverage report
pytest tests/ --cov=utils --cov-report=html
```

## Next Steps

1. **Add more page objects** for your application
2. **Create test data files** in `data/test_data/`
3. **Set up CI/CD** with GitHub Actions
4. **Add visual testing** for critical pages
5. **Configure parallel execution** for faster runs

---

**Congratulations!** You've built a professional test automation framework demonstrating:
- ✅ Page Object Model
- ✅ Dual browser support (Selenium + Playwright)
- ✅ Data-driven testing
- ✅ Visual regression testing
- ✅ Performance monitoring
- ✅ CI/CD integration
- ✅ Statistical test analytics

