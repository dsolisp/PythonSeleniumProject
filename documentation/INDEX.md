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

### 📊 Analytics & Intelligence

- **[Analytics and Reporting](ANALYTICS_AND_REPORTING.md)** - Test result analysis
  - Pandas DataFrame analytics
  - Statistical analysis and outlier detection
  - HTML dashboard generation with Jinja2
  - CSV export for external tools
  
- **[Machine Learning Integration](ML_INTEGRATION.md)** - AI-powered test intelligence
  - Flaky test detection
  - Failure prediction with Random Forest
  - Performance anomaly detection
  - Test reliability scoring

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

Results Export (data/results/)
    │
    ├─ JSON/YAML format
    └─ Environment-specific
    
Analytics Pipeline
    │
    ├─ Test Reporter (utils/test_reporter.py)
    │   ├─ Pandas analytics
    │   ├─ Statistical analysis
    │   └─ HTML dashboards
    │
    └─ ML Analyzer (utils/ml_test_analyzer.py)
        ├─ Flaky test detection
        ├─ Failure prediction
        └─ Performance analysis

Monitoring & Recovery
    │
    ├─ Error Handler (utils/error_handler.py)
    │   ├─ Tenacity retry
    │   └─ Recovery strategies
    │
    └─ Performance Monitor (utils/performance_monitor.py)
        ├─ Psutil tracking
        └─ Real-time metrics
```

## 📖 Usage Workflows

### Workflow 1: Data-Driven Web Testing
```
1. Define test data → data/test_data.json
2. Load data → TestDataManager.load_test_data()
3. Execute tests → tests/web/
4. Export results → TestDataManager.save_test_results_json()
5. Analyze → AdvancedTestReporter.generate_dataframe_analytics()
```

### Workflow 2: API Testing with Reporting
```
1. Write API tests → tests/api/test_api.py
2. Run with Allure → pytest --alluredir=reports/allure-results
3. Generate report → allure serve reports/allure-results
4. View structured logs → Check JSON logs in console
```

### Workflow 3: ML-Powered Test Optimization
```
1. Run tests regularly → Export to data/results/
2. Collect historical data → 20-30+ executions
3. Train ML model → MLTestAnalyzer.train_failure_predictor()
4. Get predictions → MLTestAnalyzer.predict_test_failures()
5. Optimize CI/CD → Run high-risk tests first
```

### Workflow 4: Performance Testing
```
1. Benchmark functions → @performance_test decorator
2. Load test APIs → locust -f locustfile.py
3. Monitor resources → Psutil system tracking
4. Analyze trends → PerformanceMonitor.get_performance_report()
5. Set thresholds → Fail tests exceeding limits
```

## 🎯 Quick Reference

### When to Use Each Feature

| Need | Use | Document |
|------|-----|----------|
| Test web UI | Selenium or Playwright | [Playwright](PLAYWRIGHT_INTEGRATION.md) |
| Test REST APIs | API Testing | [API Testing](API_TESTING.md) |
| Analyze test results | Test Reporter | [Analytics](ANALYTICS_AND_REPORTING.md) |
| Predict failures | ML Analyzer | [ML Integration](ML_INTEGRATION.md) |
| Manage test data | Test Data Manager | [Data Management](TEST_DATA_MANAGEMENT.md) |
| Handle flaky tests | Error Handler | [Error Recovery](ERROR_RECOVERY_AND_MONITORING.md) |
| Load test APIs | Locust | [Performance](PERFORMANCE_MONITORING.md) |
| Track performance | Performance Monitor | [Performance](PERFORMANCE_MONITORING.md) |

### Command Cheat Sheet

```bash
# Run tests
pytest tests/web/ -v                    # Selenium web tests
pytest tests/api/ -v                    # API tests (fast mode)
ENABLE_ALLURE=true pytest tests/api/    # API tests with Allure

# Generate reports
allure serve reports/allure-results     # View Allure report
python utils/ml_test_analyzer.py        # ML analysis report

# Performance testing
pytest tests/performance/ --benchmark-only  # Benchmarks
locust -f tests/performance/locustfile.py  # Load testing

# Data operations
python examples/export_test_results_example.py  # Export results
```

## 🔗 External Resources

- **Selenium Documentation**: https://selenium.dev/documentation/
- **Playwright Documentation**: https://playwright.dev/python/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Scikit-learn Documentation**: https://scikit-learn.org/stable/
- **Locust Documentation**: https://locust.io/
- **Allure Reports**: https://docs.qameta.io/allure/

## 💡 Best Practices

1. **Start Simple**: Begin with basic Selenium/Playwright tests
2. **Add Data**: Use TestDataManager for parameterized tests
3. **Export Results**: Save execution data for ML analysis
4. **Monitor Performance**: Track metrics from day one
5. **Analyze Trends**: Run ML Analyzer weekly for insights
6. **Optimize CI/CD**: Use predictions to prioritize tests

## 🆘 Troubleshooting

- **Import errors**: Ensure `pip install -r requirements.txt`
- **Playwright not found**: Run `playwright install`
- **ML predictions inaccurate**: Collect more historical data (20+ runs)
- **Allure not generating**: Install Allure CLI: `brew install allure`
- **Performance issues**: Check system resources with Psutil

---

**Need help?** Check the specific feature documentation above or create an issue on GitHub.

**Quick Start**: Jump to [README.md](../README.md) for installation and your first test.
