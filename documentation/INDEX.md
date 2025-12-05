# Documentation Index

Complete documentation for the Python Selenium Test Automation Framework.

## 📚 Core Documentation

### 🚀 Getting Started
- **[README.md](../README.md)** - Quick start guide and overview
- **[Local Development Guide](LOCAL_DEV_GUIDE.md)** - Development tools and local setup
- **[Pytest Configuration Guide](PYTEST_README.md)** - Testing framework setup and options
- **[Installation & Setup](#installation)** - Environment setup and dependencies

### 🧪 Testing Capabilities

#### Web UI Testing
- **[Playwright Integration](PLAYWRIGHT_INTEGRATION.md)** - Modern async browser automation
  - Mobile device emulation
  - Network interception
  - Cross-browser testing (Chromium, Firefox, WebKit)
  - Performance metrics and Core Web Vitals
  
- **[Selenium Web Testing](../pages/README.md)** - Traditional Selenium automation
  - Page Object Model
  - Element interactions
  - Visual testing

#### API Testing
- **[API Testing Guide](API_TESTING.md)** - REST API automation
  - Conditional Allure reporting
  - PyHamcrest assertions
  - Request/response validation
  - Structured logging

### 📊 Analytics & Reporting

- **[Analytics and Reporting](ANALYTICS_AND_REPORTING.md)** - Test result reports
  - HTML/JSON report generation
  - CI/CD integration
  - CSV export for external tools

- **[Test Analytics](TEST_ANALYTICS.md)** - Historical test tracking
  - Flaky test detection via pytest-history
  - Test run history analysis
  - Zero-configuration setup

### 🔧 Infrastructure & Utilities

- **[Test Data Management](TEST_DATA_MANAGEMENT.md)** - Data-driven testing
  - Multi-format support (JSON, YAML, CSV)
  - Environment-specific configurations
  - Test result export
  - Dynamic data generation
  
- **[Error Recovery & Monitoring](ERROR_RECOVERY_AND_MONITORING.md)** - Reliability features
  - Tenacity retry mechanisms
  - Psutil system monitoring
  - Smart error classification
  - Resource usage tracking
  
- **[Performance Monitoring](PERFORMANCE_MONITORING.md)** - Performance testing
  - Real-time performance tracking
  - Locust load testing
  - Pytest-benchmark integration
  - Performance regression detection

## 🗺️ Feature Integration Map

```
Test Execution
    │
    ├─ Web UI Tests
    │   ├─ Selenium (pages/)
    │   └─ Playwright (tests/web/test_playwright_*.py)
    │
    ├─ API Tests (tests/api/)
    │   ├─ REST validation
    │   └─ Conditional Allure reporting
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
    ├─ JSON/YAML export (data/results/)
    └─ Test history (.test-results.db)
        └─ pytest-history plugin
            ├─ Flaky test detection
            └─ Run history tracking

Monitoring & Recovery
    │
    └─ Error Handler (utils/error_handler.py)
        └─ Tenacity retry
```

## 📖 Usage Workflows

### Workflow 1: Data-Driven Web Testing
```
1. Define test data → data/test_data.json
2. Load data → DataManager.load_test_data()
3. Execute tests → pytest tests/web/
4. Results tracked automatically → .test-results.db
```

### Workflow 2: API Testing with Reporting
```
1. Write API tests → tests/api/test_api.py
2. Run with Allure → pytest --alluredir=reports/allure-results
3. Generate report → allure serve reports/allure-results
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
| Test web UI | Selenium or Playwright | [Playwright](PLAYWRIGHT_INTEGRATION.md) |
| Test REST APIs | API Testing | [API Testing](API_TESTING.md) |
| Generate reports | pytest-html, pytest-json | [Analytics](ANALYTICS_AND_REPORTING.md) |
| Detect flaky tests | pytest-history | [Test Analytics](TEST_ANALYTICS.md) |
| Manage test data | DataManager | [Data Management](TEST_DATA_MANAGEMENT.md) |
| Handle errors | Error Handler | [Error Recovery](ERROR_RECOVERY_AND_MONITORING.md) |
| Load test APIs | Locust | [Performance](PERFORMANCE_MONITORING.md) |

### Command Cheat Sheet

```bash
# Run tests
pytest tests/web/ -v                    # Selenium web tests
pytest tests/api/ -v                    # API tests
python run_tests.py --type unit         # Unit tests via runner

# Flaky test detection
pytest-history flakes                   # List flaky tests
pytest-history list runs                # View test run history
python run_tests.py --type unit --flaky # Run with flaky summary

# Generate reports
pytest --html=report.html               # HTML report
allure serve reports/allure-results     # Allure report

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
