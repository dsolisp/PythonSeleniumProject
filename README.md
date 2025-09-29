# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.16-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-8.4-orange.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A clean, professional, and maintainable test automation framework built with Python, featuring both traditional Selenium WebDriver and modern Playwright capabilities. Following SOLID principles and DRY methodology for scalable test automation with 2025-ready features.

## 🚀 Features

### Core Testing Capabilities
- **Clean Architecture**: SOLID principles with specialized action handlers
- **Dual Browser Automation**: Traditional Selenium + Modern Playwright support
- **Environment Configuration**: Flexible environment variable support
- **Multiple Test Types**: UI, API, Database, and Visual testing
- **Professional Logging**: Structured logging with file and console output
- **Page Object Pattern**: Maintainable and reusable page objects
- **Centralized Locators**: Clean separation of test logic and element locators
- **Screenshot Support**: Automatic failure screenshots and visual comparison
- **Database Integration**: SQLite database testing capabilities
- **CI/CD Ready**: Environment-based configuration for different deployment stages

### Modern Playwright Features (Priority 1 - ✅ COMPLETED)
- **Async Browser Automation**: Modern async/await patterns for faster execution
- **Network Interception**: Monitor and mock network requests during tests
- **Mobile Device Emulation**: Test responsive designs with real device simulation
- **Multi-Browser Testing**: Run tests concurrently across Chromium, Firefox, and WebKit
- **Performance Monitoring**: Built-in metrics collection and analysis
- **Advanced Selectors**: Robust element selection with auto-wait capabilities
- **Screenshot & Video**: Enhanced media capture for test evidence
- **Headless & Headed Modes**: Flexible execution modes for debugging and CI/CD

## 📁 Project Structure

```
├── config/
│   └── settings.py              # Environment configuration
├── locators/
│   ├── google_result_locators.py
│   └── google_search_locators.py
├── pages/
│   ├── base_page.py                    # Selenium base page with action handlers
│   ├── playwright_base_page.py         # Modern async Playwright base page
│   ├── google_result_page.py           # Selenium Google results page
│   ├── google_search_page.py           # Selenium Google search page
│   └── playwright_google_search_page.py # Modern async Google search with advanced features
├── resources/
│   └── chinook.db              # SQLite database for testing
├── tests/
│   ├── unit/                           # Comprehensive unit test suite (93 tests)
│   ├── test_api.py                     # API testing
│   ├── test_framework_core.py          # Framework functionality tests
│   ├── test_google_search.py           # Traditional Selenium UI tests
│   ├── test_playwright_google_search.py # Modern Playwright tests with advanced features
│   ├── test_playwright_simple.py       # Basic Playwright examples
│   └── test_image_diff.py              # Visual comparison tests
├── utils/
│   ├── diff_handler.py         # Image comparison utilities
│   ├── logger.py               # Simple logging utility
│   ├── sql_connection.py       # Database connection utilities
│   ├── webdriver_factory.py    # Traditional Selenium WebDriver factory
│   └── playwright_factory.py   # Modern async Playwright browser factory
├── .env                        # Environment configuration
├── requirements.txt            # Project dependencies
└── pytest.ini                 # Pytest configuration
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+ 
- Chrome browser (for default setup)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dsolisp/PythonSeleniumProject.git
   cd PythonSeleniumProject
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   
   **Standard installation (includes local dev tools):**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Full CI/CD environment (optional advanced features):**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env file with your specific configuration
   ```

### Requirements Files

- **`requirements.txt`**: Core dependencies + local development tools (black, flake8, bandit, etc.)
- **`requirements-dev.txt`**: Additional CI/CD tools for advanced workflows and documentation

## ⚙️ Environment Configuration

The framework uses environment variables for flexible configuration across different environments.

### Setup Environment Variables

**Copy and customize:**
```bash
cp .env.template .env
# Edit .env with your configuration
```

### Environment Variables Reference

#### Browser & Testing
- `BROWSER`: Browser to use (chrome, firefox, edge)
- `HEADLESS`: Run browser in headless mode (true/false)
- `TIMEOUT`: Default timeout in seconds
- `SCREENSHOT_ON_FAILURE`: Capture screenshots on test failures

#### URLs & Endpoints
- `BASE_URL`: Main application URL (default: https://www.google.com)
- `API_BASE_URL`: API endpoint base URL (default: https://jsonplaceholder.typicode.com)

#### Database & Storage
- `DB_PATH`: Path to SQLite database file (default: resources/chinook.db)

#### Visual Testing
- `VISUAL_THRESHOLD`: Pixel difference threshold for image comparison
- `SAVE_DIFF_IMAGES`: Save difference images when visual tests fail

#### Environment Settings
- `ENVIRONMENT`: Current environment (local, dev, qa, prod)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Environment Examples

**Local Development:**
```bash
HEADLESS=false
TIMEOUT=10
LOG_LEVEL=DEBUG
```

**CI/CD Pipeline:**
```bash
HEADLESS=true
TIMEOUT=30
LOG_LEVEL=INFO
```

**QA Environment:**
```bash
BASE_URL=https://qa.myapp.com
API_BASE_URL=https://api-qa.myapp.com
ENVIRONMENT=qa
```

## 🏃‍♂️ Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with HTML report
pytest --html=reports/report.html

# Run tests with coverage
pytest --cov=pages --cov=utils --cov=locators

# Run specific test file
pytest tests/test_google_search.py


# Run regression protection tests (recommended before refactoring)
pytest tests/unit/test_regression_protection.py -v

# Run unit tests for specific modules
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run tests in headless mode
pytest --headless

# Use test runner script (recommended)
python run_tests.py --type regression
python run_tests.py --type all --verbose
```

### Playwright Tests (Modern Async Browser Automation)

**Install Playwright browsers (one-time setup):**
```bash
playwright install
```

**Run Playwright tests:**
```bash
# Run basic Playwright functionality tests
pytest tests/test_playwright_simple.py -v

# Run advanced Playwright Google search tests
pytest tests/test_playwright_google_search.py -v

# Run specific Playwright test scenarios
pytest tests/test_playwright_google_search.py::test_playwright_google_search_basic
pytest tests/test_playwright_google_search.py::test_playwright_multi_browser
pytest tests/test_playwright_google_search.py::test_playwright_mobile_emulation

# Run Playwright tests in headed mode (see browser)
pytest tests/test_playwright_google_search.py --headed

# Run Playwright tests with network interception
pytest tests/test_playwright_google_search.py::test_playwright_network_interception -s

# Run performance monitoring tests
pytest tests/test_playwright_google_search.py::test_playwright_performance_monitoring -s
```

**Playwright Test Features:**
- ✅ **Async Browser Automation**: Modern async/await patterns
- ✅ **Network Interception**: Monitor and mock network requests
- ✅ **Mobile Device Emulation**: iPhone, Android device simulation
- ✅ **Multi-Browser Support**: Chromium, Firefox, WebKit
- ✅ **Performance Metrics**: Core Web Vitals, load times
- ✅ **Advanced Selectors**: Auto-wait, robust element selection
- ✅ **CAPTCHA Detection**: Smart handling of anti-bot measures

### Test Categories
```bash
# Run API tests only
pytest -m api

# Run UI tests only  
pytest -m smoke

# Run Playwright tests only
pytest -m playwright

# Run traditional Selenium tests only
pytest -m selenium

# Run database tests
pytest -m database

# Run visual comparison tests
pytest -m visual

# Run performance tests
pytest -m performance
```

## 🛠️ Local Development Tools

The framework includes essential development tools for code quality and security:

### Code Quality & Formatting
```bash
# Auto-format code (fixes issues)
black .

# Sort imports automatically
isort .

# Check code quality and style
flake8 . --max-line-length=88

# Type checking
mypy . --ignore-missing-imports
```

### Security & Safety
```bash
# Scan for security vulnerabilities in code
bandit -r . --exclude venv/

# Check dependencies for known vulnerabilities
safety check
```

### Pre-commit Workflow
```bash
# Run all quality checks before committing
black . && isort . && flake8 . && mypy . --ignore-missing-imports && bandit -r . --exclude venv/ && pytest -v
```

### IDE Integration
Most IDEs can be configured to run these tools automatically:
- **Format on save** with Black
- **Auto-sort imports** with isort
- **Real-time linting** with flake8
- **Type hints** with mypy

## 🔧 Framework Architecture

### Core Components

#### BasePage
Central coordinator that manages specialized action handlers:
- **ElementActions**: Element interactions and operations
- **NavigationActions**: URL navigation and page management  
- **ScreenshotActions**: Screenshot capture and management
- **DatabaseActions**: Database query operations

#### Locator Classes
Centralized locator management:
```python
class GoogleSearchLocators:
    SEARCH_INPUT = (By.NAME, "q")
    SEARCH_BUTTON = (By.NAME, "btnK")
    RESULTS_CONTAINER = (By.ID, "search")
```

#### Factory Pattern
Consistent object creation:
```python
# WebDriver creation
driver = WebDriverFactory.create_chrome_driver(headless=True)

# Database connection
db = DatabaseFactory.create_database_connection()
```

### Page Object Example
```python
from pages.base_page import BasePage
from locators.google_search_locators import GoogleSearchLocators

class GoogleSearchPage(BasePage):
    def search_for(self, term):
        self.send_keys(GoogleSearchLocators.SEARCH_INPUT, term)
        self.click(GoogleSearchLocators.SEARCH_BUTTON)
        return self.has_results()
```

## 📊 Logging

The framework includes structured logging with both console and file output:

```python
from utils.logger import logger

# Test lifecycle logging
logger.test_start("test_login")
logger.step("Navigate to login page")
logger.screenshot("/path/to/screenshot.png")
logger.test_end("test_login", "PASSED", 2.34)
```

## 🗄️ Database Testing

Integration with SQLite database for data-driven testing:

```python
# Execute database queries
results = base_page.execute_query("SELECT * FROM tracks LIMIT 5")

# Use database data in tests
track_name = base_page.execute_query("SELECT Name FROM tracks WHERE TrackId = ?", (1,))
```

## 📸 Visual Testing

Automated visual comparison with pixel-level accuracy:

```python
# Capture and compare screenshots
expected_screenshot = "expected.png"
actual_screenshot = "actual.png"
diff_result = compare_images(expected_screenshot, actual_screenshot)
```

## 🧪 Unit Testing & Regression Protection

The framework includes comprehensive unit tests designed to protect against regression during refactoring. These tests focus on core functionality that could break when code is moved or renamed.

### Running Unit Tests

```bash
# Run all regression protection tests (recommended before refactoring)
pytest tests/unit/test_regression_protection.py -v

# Run using the test runner script
python run_tests.py --type regression

# Run all unit tests
python run_tests.py --type unit --verbose

# Run with coverage
python run_tests.py --type regression --coverage
```

### Test Coverage Areas

The unit test suite protects the following core areas:

#### **Core Configuration**
- Settings module imports and functionality
- Logger module imports and basic operations
- WebDriver factory imports and driver creation
- Database connection functions

#### **Page Object Architecture** 
- BasePage instantiation and required attributes
- Page object inheritance structure
- Driver parameter handling and tuple unpacking
- Action handler coordination

#### **Database Functionality**
- Database connection creation and management
- Query execution and result handling
- Error handling and connection cleanup

#### **Module Integration**
- Cross-module compatibility
- Import dependencies and circular import prevention
- Error handling that doesn't break basic functionality

#### **File Structure Integrity**
- Required files exist in expected locations
- Package structure is importable
- Module dependencies are satisfied

### Test Runner Features

The `run_tests.py` script provides:

```bash
# Test type options
python run_tests.py --type unit        # Unit tests only
python run_tests.py --type integration # Integration tests only  
python run_tests.py --type regression  # Regression protection tests
python run_tests.py --type all         # All test suites

# Additional options
python run_tests.py --verbose          # Detailed test output
python run_tests.py --coverage         # Generate coverage reports
```

### Refactoring Workflow

**Before making structural changes:**
```bash
# 1. Run regression protection tests
python run_tests.py --type regression

# 2. Ensure all tests pass before refactoring
# ✅ Framework is protected against regression during refactoring

# 3. Make your changes (rename, move, refactor)

# 4. Run tests again to catch any breaks
python run_tests.py --type regression

# 5. Fix any failing tests before committing
```

The unit tests are specifically designed to catch common refactoring issues:
- **Module imports breaking** when files are moved
- **Function signatures changing** when methods are refactored  
- **Class initialization breaking** when constructors are modified
- **Dependency injection failing** when parameter order changes
- **Package structure issues** when directories are reorganized

This comprehensive test coverage ensures that refactoring activities maintain framework stability and functionality.

## 📈 Best Practices

### Code Organization
- ✅ **SOLID Principles**: Single responsibility, dependency inversion
- ✅ **DRY Methodology**: No code duplication
- ✅ **Clean Naming**: Self-explanatory variable and function names
- ✅ **Separation of Concerns**: Locators, pages, tests, and utilities separated

### Test Design
- ✅ **Page Object Pattern**: Maintainable and reusable page interactions
- ✅ **Data-Driven Testing**: Database integration for dynamic test data
- ✅ **Independent Tests**: Each test can run in isolation
- ✅ **Proper Assertions**: Clear and meaningful test validations

### Environment Management
- ✅ **Environment Variables**: No hardcoded values
- ✅ **Flexible Configuration**: Easy environment switching
- ✅ **CI/CD Ready**: Pipeline-friendly configuration

## 🔄 CI/CD Pipeline

The project includes a comprehensive GitHub Actions pipeline with:

### Pipeline Stages
- **Security Scanning**: Bandit and Safety checks for vulnerabilities
- **Code Quality**: Black, isort, flake8, and mypy validation
- **Unit Tests**: Multi-version Python testing with coverage reports
- **Integration Tests**: Cross-browser testing with Selenium Grid
- **Visual Tests**: Automated visual regression testing
- **Performance Tests**: Benchmark performance monitoring
- **Reporting**: Allure reports with GitHub Pages deployment

### Pipeline Triggers
- Push to main/develop branches
- Pull requests
- Daily scheduled runs (2 AM UTC)
- Manual dispatch with configurable parameters

### Artifacts Generated
- HTML and JSON test reports
- Code coverage reports
- Allure test reports
- Security scan results
- Performance benchmarks
- Screenshot evidence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (`pip install -r requirements.txt`)
4. Make your changes
5. Run quality checks:
   ```bash
   # Format and organize code
   black . && isort .
   
   # Check for issues
   flake8 . && mypy . --ignore-missing-imports
   
   # Security check
   bandit -r . --exclude venv/
   
   # Run tests
   pytest -v
   ```
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🛟 Support

For questions, issues, or contributions:
- Create an issue in the [GitHub repository](https://github.com/dsolisp/PythonSeleniumProject/issues)

---

**Built with ❤️ for reliable test automation**
