# Analytics and Reporting

## Overview

The framework provides comprehensive reporting capabilities using **pytest plugins** and **pytest-history** for flaky test detection. These tools transform raw test execution data into actionable insights.

## 🎯 When to Use

- **After test execution**: Generate detailed HTML/JSON reports
- **Flaky test detection**: Identify tests with inconsistent behavior
- **Trend tracking**: Monitor test suite health over time
- **Data export**: Share results with external tools (JSON)
- **CI/CD integration**: Automatic reporting in pipelines

## 🔧 Key Components

### 1. pytest-html Reports

**Purpose**: Beautiful HTML reports with test details

```bash
# Generate HTML report
pytest tests/ --html=reports/html/report.html --self-contained-html
```

### 2. pytest-json-report

**Purpose**: JSON output for CI/CD integration

```bash
# Generate JSON report
pytest tests/ --json-report --json-report-file=reports/json/results.json
```

### 3. pytest-history (Flaky Test Detection)

**Purpose**: Track test results across runs and detect flaky tests

**Features**:
- Automatic history tracking (zero config)
- Flaky test detection
- Run history analysis
- SQLite-based storage

**Usage**:
```bash
# Run tests (history tracked automatically)
pytest tests/

# View flaky tests
pytest-history flakes

# View test run history
pytest-history list runs

# Use via run_tests.py
python run_tests.py --type unit --flaky
```

## 📊 Report Types

### 1. HTML Reports (pytest-html)
**Use case**: Human-readable reports for stakeholders

```bash
pytest tests/ --html=reports/report.html --self-contained-html
```

### 2. JSON Reports (pytest-json-report)
**Use case**: CI/CD integration, programmatic processing

```bash
pytest tests/ --json-report --json-report-file=reports/results.json
```

### 3. Flaky Test Reports (pytest-history)
**Use case**: Identify unreliable tests

```bash
pytest-history flakes
```

## 📈 Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Tests with Reports
  run: |
    pytest tests/ --html=reports/report.html --json-report

- name: Check Flaky Tests
  run: pytest-history flakes || echo "No flaky tests"

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: reports/
```

## 📚 Related Documentation

- [Test Analytics](TEST_ANALYTICS.md) - Flaky detection via pytest-history
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Benchmark testing

## 🔗 File Locations

- **Test History DB**: `.test-results.db` (auto-created by pytest-history)
- **Report Output**: `reports/`

---

**Value Proposition**: Transform raw test results into actionable insights with pytest reporting plugins and automatic flaky test detection.
