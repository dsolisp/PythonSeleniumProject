# Test Analytics Engine

## Unified Workflow

> **Recommended:** Use the integrated workflow script for test analytics. Statistical analysis, flaky test detection, and reliability scoring are automatically triggered by running:
>
> ```bash
> python run_full_workflow.py
> ```
>
> This script runs all tests, exports results, performs analytics, and generates analysis reports—no manual steps required.

## Overview

Test analytics is fully automated as part of the unified workflow. The Test Analytics Engine (`utils/test_analytics.py`) uses **pandas** for statistical analysis to provide flaky test detection, reliability scoring, and performance anomaly detection based on historical execution data.

## 🎯 When to Use

- **After running the workflow script**: Analysis reports are generated automatically
- **Test suite optimization**: Flaky tests and performance issues are detected
- **CI/CD optimization**: Use analytics to prioritize test improvements
- **Quality monitoring**: Track test reliability over time

## 📊 Key Features (Automated)

### 1. Flaky Test Detection

**Purpose**: Identify tests with inconsistent pass/fail behavior

**How it Works**:
- Analyzes test pass rates across multiple executions
- Identifies tests with success rates < 90%
- Requires minimum 3 executions per test

**Usage**:
```bash
# Run analyzer
python utils/test_analytics.py

# Output:
⚠️  Flaky Tests (3):
   • test_checkout: 65% pass rate
   • test_payment: 80% pass rate
   • test_network_interception: 75% pass rate
```

### 2. Performance Anomaly Detection

**Purpose**: Identify tests with unusual execution times

**Metrics**:
- Average duration per test
- Identifies slow tests (duration > threshold)
- Tracks performance trends

**Usage**:
```python
from utils.test_analytics import TestAnalytics

analytics = TestAnalytics()
analytics.load_test_results()

# Output:
🐢 Slow Tests (5):
   • test_api_users: 1.20s
   • test_visual_comparison: 2.50s
```

### 3. Test Reliability Scoring

**Purpose**: Rank tests by reliability for prioritization

**Scoring Approach**:
- Pass rate calculation per test
- Risk scoring based on failure frequency
- Prioritized list for test maintenance

**Usage**:
```python
analytics = TestAnalytics()
analytics.load_test_results()
analytics.generate_report()

# Output:
🏆 Test Reliability (Top 5 risks):
   • test_multiple_browsers: 25% pass [⚠️ FLAKY]
   • test_mobile_emulation: 75% pass [⚠️ FLAKY]
   • test_api_health: 100% pass [Risk: 0%]
```

## 📊 Data Requirements

### Input Data Format

The analyzer reads JSON files from `data/results/`:

```
data/results/
├── local/
│   └── api_tests_20251006_160530.json
├── staging/
│   └── web_tests_20251006_161234.json
└── production/
    └── integration_tests_20251006_162000.json
```

**Expected JSON Structure**:
```json
{
    "test_name": "api_tests",
    "environment": "staging",
    "timestamp": "20251006_160530",
    "results": {
        "browser": "chrome",
        "headless": false,
        "tests": [
            {
                "name": "test_api_health",
                "status": "passed",
                "duration": 0.5
            },
            {
                "name": "test_api_users",
                "status": "failed",
                "duration": 1.2
            }
        ]
    }
}
```

### Minimum Dataset Requirements

- **For basic analytics**: Any amount of data
- **For flaky detection**: Minimum 3 executions per test
- **Best results**: 20+ executions for trend analysis

## 🚀 Usage Scenarios

### 1. CI/CD Integration

**Identify flaky tests before they cause CI failures**:

```bash
# Run analytics
python utils/test_analytics.py > reports/test_analysis.txt

# Review flaky tests
grep "FLAKY" reports/test_analysis.txt
```

### 2. Weekly Maintenance Report

```bash
# Generate weekly health report
python utils/test_analytics.py > reports/weekly_health_$(date +%Y%m%d).txt

# Review:
# - Flaky tests to fix
# - Slow tests to optimize
# - Reliability trends
```

### 3. Test Prioritization

**Focus on unreliable tests first**:

```python
from utils.test_analytics import TestAnalytics

analytics = TestAnalytics()
analytics.load_test_results()
flaky_tests = analytics.detect_flaky_tests()

# Prioritize fixing flaky tests
for test in flaky_tests:
    print(f"Fix: {test['name']} - {test['pass_rate']}% pass rate")
```

## 📈 Report Generation

### Console Report

```bash
python utils/test_analytics.py
```

**Output includes**:
- Dataset overview (total test executions)
- Flaky test list with pass rates
- Slow test identification
- Test reliability rankings

### Integrated Workflow

```bash
# Full pipeline with analytics
python run_full_workflow.py

# Output shows:
# [POST] Running test analytics (flaky detection, reliability scores)...
# ⚠️  Flaky Tests (3):
# 🐢 Slow Tests (5):
# 🏆 Test Reliability (Top 5 risks):
```

## 🔧 Configuration

The analytics engine reads from `data/results/` directory. Results are exported automatically by the test framework.

## ⚠️ Limitations

### Small Datasets
- Flaky detection requires minimum 3 executions per test
- More data = more accurate trends
- Solution: Run tests regularly and accumulate data

### All Passing Tests
- If all tests always pass, no flaky tests will be detected
- Solution: Include varied execution scenarios
- Solution: Ensure consistent test result exports

## 💡 Best Practices

1. **Regular Execution**: Run full workflow daily to track trends
2. **Prioritize Flaky Tests**: Fix identified flaky tests first - highest ROI
3. **Track Performance**: Monitor for gradual performance degradation
4. **Data Hygiene**: Maintain consistent test result format

## 📚 Related Documentation

- [Test Results Export](TEST_DATA_MANAGEMENT.md#test-results-export) - How to export data for analysis
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Complementary analytics features
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Real-time performance tracking

## 🔗 File Locations

- **Implementation**: `utils/test_analytics.py`
- **Input Data**: `data/results/*.json`
- **Workflow**: `run_full_workflow.py`

---

**Value Proposition**: Use statistical analysis to detect flaky tests, identify slow tests, and score test reliability - transforming reactive testing into proactive quality assurance.
