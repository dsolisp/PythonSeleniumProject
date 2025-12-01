# Analytics and Reporting

## Overview

The framework provides comprehensive analytics and reporting capabilities using **pytest plugins** and the **Test Analytics Engine**. These tools transform raw test execution data into actionable insights.

## 🎯 When to Use

- **After test execution**: Generate detailed HTML/JSON reports
- **Performance analysis**: Identify slow and flaky tests
- **Trend tracking**: Monitor test suite health over time
- **Data export**: Share results with external tools (CSV, JSON)
- **CI/CD integration**: Automatic reporting in pipelines

> **Tip:** Run `python run_full_workflow.py` to automatically trigger tests, analytics, and report generation.

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

### 3. Test Analytics Engine (`utils/test_analytics.py`)

**Purpose**: Statistical analysis of test execution data

**Features**:
- Flaky test detection
- Slow test identification
- Reliability scoring
- Pandas-based analysis

**Usage**:
```bash
# Run analytics after tests
python utils/test_analytics.py

# Output:
# ⚠️  Flaky Tests (3):
#    • test_network: 75% pass rate
# 🐢 Slow Tests (5):
#    • test_api_users: 1.20s
# 🏆 Test Reliability (Top 5 risks):
#    • test_checkout: 65% pass [⚠️ FLAKY]
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

### 3. CSV Analytics Export
**Use case**: Excel analysis, data visualization tools

The full workflow automatically exports to `reports/analytics_summary.csv`:
```bash
python run_full_workflow.py
```

## 📈 Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Run Tests with Reports
  run: |
    pytest tests/ --html=reports/report.html --json-report

- name: Run Analytics
  run: python utils/test_analytics.py

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: reports/
```

## 📚 Related Documentation

- [Test Analytics](TEST_ANALYTICS.md) - Flaky detection & reliability scoring
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Real-time metrics

## 🔗 File Locations

- **Analytics Engine**: `utils/test_analytics.py`
- **Report Output**: `reports/`
- **Analytics CSV**: `reports/analytics_summary.csv`

---

**Value Proposition**: Transform raw test results into actionable insights with pytest reporting plugins and statistical analytics.
