# Documentation Index

Complete documentation for the Python Selenium Test Automation Framework.

## 📚 Core Documentation

### 🚀 Getting Started
- **[README.md](../README.md)** - Quick start guide and overview
- **[Local Development Guide](guides/LOCAL_DEV_GUIDE.md)** - Development tools and local setup
- **[Pytest Configuration Guide](guides/PYTEST_README.md)** - Testing framework setup and options
- **[Installation & Setup](#installation)** - Environment setup and dependencies

### 🧪 Testing Capabilities

#### Web UI Testing
- **[Playwright Integration](guides/PLAYWRIGHT_INTEGRATION.md)** - Modern async browser automation
  - Mobile device emulation
  - Network interception
  - Cross-browser testing (Chromium, Firefox, WebKit)
  - Performance metrics and Core Web Vitals
  
- **Selenium Web Testing** - Traditional Selenium automation
  - Page Object Model
  - Element interactions
  - Visual testing
  - (See `pages/` and `tests/ui/` in this repo for concrete examples)

#### API Testing
- **[API Testing Guide](guides/API_TESTING.md)** - REST API automation
  - Conditional Allure reporting
  - PyHamcrest assertions
  - Request/response validation
  - Structured logging

### 📊 Analytics & Reporting

- **[Analytics and Reporting](guides/ANALYTICS_AND_REPORTING.md)** - Test result reports
  - HTML/JSON report generation
  - CI/CD integration
  - CSV export for external tools

- **[Test Analytics](guides/TEST_ANALYTICS.md)** - Historical test tracking
  - Flaky test detection via pytest-history
  - Test run history analysis
  - Zero-configuration setup

### 🔧 Infrastructure & Utilities

- **[Test Data Management](guides/TEST_DATA_MANAGEMENT.md)** - Data-driven testing
  - Multi-format support (JSON, YAML, CSV)
  - Environment-specific configurations
  - Test result export
  - Dynamic data generation
  
- **[Error Recovery & Monitoring](guides/ERROR_RECOVERY_AND_MONITORING.md)** - Reliability features
  - Clean error formatting (`format_error` / `ErrorInfo`) and optional screenshots on failure
  - Stdlib-only exponential backoff retries (`SmartErrorHandler.execute_with_retry`)
  - No separate “error classifier” layer and no CPU/RAM monitoring (no psutil-style resource tracking in this repo)
  
- **[Performance Monitoring](guides/PERFORMANCE_MONITORING.md)** - Performance testing
  - Real-time performance tracking
  - Locust load testing
  - Pytest-benchmark integration
  - Performance regression detection

## 🗺️ Feature Integration Map

```
Test Execution
    │
    ├─ Web UI Tests
    │   ├─ Selenium (`pages/`, `tests/ui/`)
    │   └─ Playwright (optional; see guides/PLAYWRIGHT_INTEGRATION.md — not a separate `tests/web/` tree)
    │
    ├─ API Tests (`tests/backend/test_api.py`)
    │   ├─ REST validation (SWAPI sample)
    │   └─ Optional Allure when you add steps/decorators
    │
    ├─ Performance Tests (tests/performance/)
    │   ├─ Benchmarking
    │   └─ Load testing
    │
    └─ Data Management (utils/test_data_manager.py)
        ├─ Load test data
        └─ Export results

Results & History
    │
    ├─ JSON/YAML export (var/data/results/)
    └─ Test history (.test-results.db)
        └─ pytest-history plugin
            ├─ Flaky test detection
            └─ Run history tracking

Monitoring & Recovery
    │
    └─ Error Handler (utils/error_handler.py)
        └─ Dependency-free retry patterns
```

## 📖 Usage Workflows

### Workflow 1: Data-Driven Web Testing
```
1. Define test data → data/test_data.json
2. Load data → DataManager.load_test_data()
3. Execute tests → pytest tests/ui/
4. Results tracked automatically → .test-results.db
```

### Workflow 2: API Testing with Reporting
```
1. Write API tests → tests/backend/test_api.py (or add modules alongside it)
2. Run with Allure → pytest --alluredir=var/allure-results
3. Generate report → allure serve var/allure-results
4. View structured logs → Check JSON logs in console
```

### Workflow 3: Flaky Test Detection
```
1. Run tests regularly → pytest tests/
2. History tracked automatically → .test-results.db
3. Check flaky tests → pytest-history flakes
4. Fix unreliable tests first
```

### Workflow 4: Performance Testing
```
1. Benchmark tests → pytest tests/performance/ --benchmark-only
2. Load test APIs → locust -f tests/performance/locustfile.py
3. Set thresholds → Fail tests exceeding limits
```

## 🎯 Quick Reference

### When to Use Each Feature

| Need | Use | Document |
|------|-----|----------|
| Test web UI | Selenium or Playwright | [Playwright](guides/PLAYWRIGHT_INTEGRATION.md) |
| Test REST APIs | API Testing | [API Testing](guides/API_TESTING.md) |
| Generate reports | pytest-html, pytest-json | [Analytics](guides/ANALYTICS_AND_REPORTING.md) |
| Detect flaky tests | pytest-history | [Test Analytics](guides/TEST_ANALYTICS.md) |
| Manage test data | DataManager | [Data Management](guides/TEST_DATA_MANAGEMENT.md) |
| Handle errors | Error Handler | [Error Recovery](guides/ERROR_RECOVERY_AND_MONITORING.md) |
| Load test APIs | Locust | [Performance](guides/PERFORMANCE_MONITORING.md) |

### Command Cheat Sheet

```bash
# Run tests
pytest tests/ui/ -v                     # Selenium UI tests
pytest tests/backend/test_api.py -m api -v   # API (SWAPI) tests
python scripts/run_tests.py --type unit         # Unit tests via runner

# Flaky test detection
pytest-history flakes                   # List flaky tests
pytest-history list runs                # View test run history
python scripts/run_tests.py --type unit --flaky # Run with flaky summary

# Generate reports
pytest --html=report.html               # HTML report
allure serve var/allure-results     # Allure report

# Performance testing
pytest tests/performance/ --benchmark-only  # Benchmarks
locust -f tests/performance/locustfile.py  # Load testing
```

## 🔗 External Resources

- **Selenium Documentation**: https://selenium.dev/documentation/
- **Playwright Documentation**: https://playwright.dev/python/
- **pytest-history**: https://pypi.org/project/pytest-history/
- **Locust Documentation**: https://locust.io/
- **Allure Reports**: https://docs.qameta.io/allure/

## 💡 Best Practices

1. **Start Simple**: Begin with basic Selenium/Playwright tests
2. **Add Data**: Use DataManager for parameterized tests
3. **Track History**: Let pytest-history record all runs
4. **Fix Flaky Tests**: Run `pytest-history flakes` regularly
5. **Monitor Performance**: Use benchmarks from day one

## 🆘 Troubleshooting

- **Import errors**: Ensure `pip install -r requirements.txt`
- **Playwright not found**: Run `playwright install`
- **No flaky tests**: Need 3+ runs with mixed pass/fail results
- **Allure not generating**: Install Allure CLI: `brew install allure`

---

**Need help?** Check the specific feature documentation above or create an issue on GitHub.

**Quick Start**: Jump to [README.md](../README.md) for installation and your first test.
