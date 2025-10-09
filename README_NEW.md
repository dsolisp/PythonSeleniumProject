# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.16-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-8.4-orange.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, enterprise-grade test automation framework with advanced analytics, ML-powered intelligence, and modern testing capabilities.

## 🚦 Unified Workflow (Recommended)

> **Run the entire QA process, including tests, analytics, ML, and retention, with a single command:**
>
> ```bash
> python run_full_workflow.py
> ```
>
> This script orchestrates the full pipeline:
> - Pre-checks and environment validation
> - Runs all web and API tests
> - Exports and archives results
> - Runs analytics and generates dashboards
> - Runs ML analysis and predictions
> - Enforces retention (keeps only the 30 most recent results)
>
> **All feature modules are now integrated and automated.**

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (for Playwright tests)
playwright install

# 3. Run your first test
pytest tests/web/test_search_engine.py -v

# 4. View results
ls -la reports/
```

## ✨ Key Features

### 🧪 Testing Capabilities
- **[Selenium Web Testing](documentation/WEB_UI_TESTING.md)** - Traditional browser automation with Page Object Model
- **[Playwright Integration](documentation/PLAYWRIGHT_INTEGRATION.md)** - Modern async automation with mobile emulation
- **[API Testing](documentation/API_TESTING.md)** - REST API validation with conditional Allure reporting

### 📊 Analytics & Intelligence
- **[Analytics & Reporting](documentation/ANALYTICS_AND_REPORTING.md)** - Pandas-powered analytics, statistical analysis, HTML dashboards
- **[ML Integration](documentation/ML_INTEGRATION.md)** - AI-powered flaky test detection, failure prediction, reliability scoring

### 🔧 Infrastructure
- **[Test Data Management](documentation/TEST_DATA_MANAGEMENT.md)** - Multi-format data support (JSON/YAML/CSV), environment configs
- **[Error Recovery](documentation/ERROR_RECOVERY_AND_MONITORING.md)** - Tenacity retry mechanisms, Psutil system monitoring
- **[Performance Testing](documentation/PERFORMANCE_MONITORING.md)** - Real-time monitoring, Locust load testing, benchmarking

## 📋 Prerequisites

```bash
# Python 3.13+ required
python --version

# Install all dependencies
pip install -r requirements.txt

# For Playwright tests
playwright install
```

## 🏗️ Project Structure

```
PythonSeleniumProject/
├── documentation/          # 📚 Feature-specific documentation
│   ├── INDEX.md           # Complete documentation index
│   ├── ANALYTICS_AND_REPORTING.md
│   ├── ML_INTEGRATION.md
│   ├── TEST_DATA_MANAGEMENT.md
│   ├── ERROR_RECOVERY_AND_MONITORING.md
│   ├── PERFORMANCE_MONITORING.md
│   ├── API_TESTING.md
│   └── PLAYWRIGHT_INTEGRATION.md
│
├── tests/                 # Test suites
│   ├── api/              # API tests (5 tests)
│   ├── web/              # Web UI tests (Selenium + Playwright)
│   ├── unit/             # Unit tests (229 tests)
│   ├── integration/      # Integration tests (19 tests)
│   └── performance/      # Performance tests (3 tests)
│
├── pages/                # Page Object Model
├── locators/             # Centralized locators
├── utils/                # Framework utilities
│   ├── test_reporter.py           # Analytics & reporting
│   ├── ml_test_analyzer.py        # ML intelligence
│   ├── test_data_manager.py       # Data management
│   ├── error_handler.py           # Error recovery
│   ├── performance_monitor.py     # Performance tracking
│   └── structured_logger.py       # Structured logging
│
├── data/                 # Test data and results
└── reports/              # Test execution reports
```

## 🧪 Running Tests

> **Manual test execution is still supported, but for full analytics, ML, and reporting, use the unified workflow above.**

### Basic Execution

```bash
# Run all tests
pytest -v

# Run by category
pytest tests/api/ -v          # API tests
pytest tests/web/ -v          # Web UI tests
pytest tests/unit/ -v         # Unit tests
pytest tests/integration/ -v  # Integration tests
pytest tests/performance/ -v  # Performance tests
```

### Advanced Execution

```bash
# API tests with Allure reporting
pytest tests/api/ -v --alluredir=reports/allure-results
allure serve reports/allure-results

# API tests without Allure (faster)
ENABLE_ALLURE=false pytest tests/api/ -v

# Playwright tests
pytest tests/web/test_playwright_search_engine.py -v --headed

# Performance benchmarks
pytest tests/performance/ --benchmark-only
```

## 📊 Features Deep Dive

> **Note:** All analytics, ML, and data exports are now triggered automatically by the workflow script. Manual usage is optional for advanced scenarios.

### 1. Analytics & Reporting
Transform test results into actionable insights with pandas-powered analytics.

```python
from utils.test_reporter import AdvancedTestReporter

reporter = AdvancedTestReporter()
analytics = reporter.generate_dataframe_analytics()
reporter.export_to_csv('reports/test_analytics.csv')
```

**[→ Full Documentation](documentation/ANALYTICS_AND_REPORTING.md)**

**Value**: Statistical analysis, outlier detection, HTML dashboards, CSV export

---

### 2. ML-Powered Intelligence
Predict failures and detect flaky tests using machine learning.

```bash
# Run ML analysis
python utils/ml_test_analyzer.py

# Output: Flaky tests, failure predictions, reliability scores
```

**[→ Full Documentation](documentation/ML_INTEGRATION.md)**

**Value**: Flaky test detection, failure prediction, test optimization

---

### 3. Test Data Management
Flexible data management with JSON, YAML, and CSV support.

```python
from utils.test_data_manager import DataManager

manager = DataManager()
data = manager.load_test_data('test_data')
config = manager.load_yaml_config('browser_settings', 'qa')
```

**[→ Full Documentation](documentation/TEST_DATA_MANAGEMENT.md)**

**Value**: Environment-specific data, multi-format support, result export

---

### 4. Error Recovery & Monitoring
Self-healing tests with intelligent retry and system monitoring.

```python
from utils.error_handler import SmartErrorHandler
import psutil

handler = SmartErrorHandler()
result = handler.execute_with_tenacity_retry(
    unstable_operation,
    max_attempts=3
)

memory = psutil.virtual_memory()
print(f"Memory usage: {memory.percent}%")
```

**[→ Full Documentation](documentation/ERROR_RECOVERY_AND_MONITORING.md)**

**Value**: Tenacity retry, Psutil monitoring, recovery strategies

---

### 5. Performance Testing
Comprehensive performance monitoring and load testing.

```bash
# Function benchmarking
pytest tests/performance/ --benchmark-only

# Load testing with Locust
locust -f tests/performance/locustfile.py --users 50 --spawn-rate 5
```

**[→ Full Documentation](documentation/PERFORMANCE_MONITORING.md)**

**Value**: Real-time monitoring, load testing, regression detection

---

### 6. API Testing
REST API automation with conditional Allure reporting.

```python
@allure.title("Test GET /users endpoint")
def test_get_users(self):
    response = self.session.get(f"{self.base_url}/users")
    assert_that(response.status_code, equal_to(200))
```

**[→ Full Documentation](documentation/API_TESTING.md)**

**Value**: Conditional Allure, PyHamcrest assertions, structured logging

---

### 7. Playwright Integration
Modern async browser automation with mobile emulation.

```python
def test_mobile_device(page: Page):
    # Test on iPhone 12
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
```

**[→ Full Documentation](documentation/PLAYWRIGHT_INTEGRATION.md)**

**Value**: Mobile emulation, network interception, cross-browser testing

## 🎯 Integration Workflow

### Complete Test Automation Pipeline

```
1. Write Tests
   ├─ Web UI (Selenium/Playwright)
   ├─ API (REST validation)
   └─ Performance (Benchmarks/Load tests)
   
2. Execute Tests
   ├─ Run test suite
   └─ Export results → data/results/
   
3. Analytics
   ├─ Test Reporter → Statistical analysis
   └─ ML Analyzer → Failure predictions
   
4. Reporting
   ├─ HTML dashboards
   ├─ CSV exports
   └─ Allure reports
   
5. Optimization
   ├─ Fix flaky tests
   ├─ Run high-risk tests first
   └─ Monitor performance trends
```

**[→ Complete Integration Guide](documentation/INDEX.md)**

## 📚 Documentation

| Topic | Description | Link |
|-------|-------------|------|
| **Getting Started** | Installation, first test | This README |
| **Complete Index** | All documentation | [INDEX.md](documentation/INDEX.md) |
| **Analytics** | Pandas analytics, reporting | [ANALYTICS_AND_REPORTING.md](documentation/ANALYTICS_AND_REPORTING.md) |
| **ML Integration** | AI-powered test intelligence | [ML_INTEGRATION.md](documentation/ML_INTEGRATION.md) |
| **Data Management** | Test data, configs, export | [TEST_DATA_MANAGEMENT.md](documentation/TEST_DATA_MANAGEMENT.md) |
| **Error Recovery** | Retry, monitoring, recovery | [ERROR_RECOVERY_AND_MONITORING.md](documentation/ERROR_RECOVERY_AND_MONITORING.md) |
| **Performance** | Monitoring, load testing | [PERFORMANCE_MONITORING.md](documentation/PERFORMANCE_MONITORING.md) |
| **API Testing** | REST API automation | [API_TESTING.md](documentation/API_TESTING.md) |
| **Playwright** | Modern browser automation | [PLAYWRIGHT_INTEGRATION.md](documentation/PLAYWRIGHT_INTEGRATION.md) |

## 🔧 Configuration

### Environment Variables

```bash
# Test environment
export TEST_ENV=qa              # local, dev, qa, prod
export BROWSER=chrome           # chrome, firefox, edge
export HEADLESS=false           # true, false

# Allure reporting
export ENABLE_ALLURE=true       # true, false

# API endpoint
export API_BASE_URL=https://api.example.com
```

### YAML Configuration

```yaml
# data/configs/browser_settings_qa.yml
browser:
  type: chrome
  headless: true
  window_size: 1920x1080

timeouts:
  implicit: 10
  explicit: 20
  page_load: 30
```

## 🏆 Framework Capabilities

- ✅ **256 Total Tests** (5 API + 229 unit + 19 integration + 3 performance)
- ✅ **7 Major Features** (Analytics, ML, Data, Error Recovery, Performance, API, Playwright)
- ✅ **6 Library Integrations** (Pandas, Numpy, YAML, Tenacity, Psutil, Scikit-learn)
- ✅ **100% Test Coverage** for all integrated features
- ✅ **Clean Architecture** following SOLID principles
- ✅ **Production-Ready** enterprise-grade capabilities

## 🚀 CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test Automation

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v --alluredir=reports/allure-results
      
      - name: Generate ML analysis
        run: python utils/ml_test_analyzer.py
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

## 💡 Best Practices

1. **Start simple** - Begin with basic Selenium/Playwright tests
2. **Add data** - Use TestDataManager for parameterized tests
3. **Export results** - Save execution data for ML analysis
4. **Monitor performance** - Track metrics from day one
5. **Analyze trends** - Run ML Analyzer weekly
6. **Optimize CI/CD** - Use predictions to prioritize tests

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and run tests
4. Format code: `black . && isort .`
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Summary

This framework provides:
- **Modern Testing**: Selenium + Playwright support
- **Intelligence**: ML-powered failure prediction
- **Analytics**: Comprehensive test result analysis
- **Reliability**: Self-healing with retry mechanisms
- **Performance**: Load testing and benchmarking
- **Flexibility**: Multi-format data management

**Built for QA engineers who demand excellence** 🚀

---

**Need help?** Check [documentation/INDEX.md](documentation/INDEX.md) for complete guides.

**Quick commands**:
```bash
pytest tests/web/ -v                    # Run web tests
pytest tests/api/ -v --alluredir=...    # API tests with Allure
python utils/ml_test_analyzer.py        # ML analysis
locust -f tests/performance/locustfile.py  # Load testing
```
