# Machine Learning Integration

## Unified Workflow

> **Recommended:** Use the integrated workflow script for all ML-powered analysis. ML analysis, flaky test detection, and predictions are now automatically triggered by running:
>
> ```bash
> python run_full_workflow.py
> ```
>
> This script runs all tests, exports results, performs analytics, and runs ML analysis—no manual steps required.

## Overview

ML-powered analysis is now fully automated as part of the unified workflow. The ML Test Analyzer uses **scikit-learn** to provide intelligent test analysis, failure prediction, and test optimization recommendations based on historical execution data, all orchestrated by `run_full_workflow.py`.

## 🎯 When to Use

- **After running the workflow script**: ML analysis and predictions are generated automatically
- **Test suite optimization**: Flaky tests and performance issues are detected (see ML report)
- **CI/CD optimization**: Use ML outputs to prioritize test improvements
- **Capacity planning**: Understand test execution patterns (see ML analysis output)

## 🤖 Key Features (Automated)

### 1. Flaky Test Detection

**Purpose**: Identify tests with inconsistent pass/fail behavior

**How it Works**:
- Analyzes test pass rates across multiple executions
- Identifies tests with success rates < 90%
- Requires minimum 3 executions per test

**Usage**:
```bash
# Run analyzer
python utils/ml_test_analyzer.py

# Output:
⚠️  Found 3 flaky tests:
   • test_checkout: 65.0% pass rate (13/20 passed)
   • test_payment: 80.0% pass rate (16/20 passed)
   • test_login: 90.0% pass rate (18/20 passed)
```

### 2. Performance Anomaly Detection

**Purpose**: Identify tests with unusual execution times

**Metrics**:
- Average duration
- Median duration
- Standard deviation
- Outlier detection (Z-score > 2)

**Usage**:
```python
from utils.ml_test_analyzer import MLTestAnalyzer

analyzer = MLTestAnalyzer()
analyzer.load_historical_data()
stats = analyzer.analyze_performance_trends()

print(f"Average: {stats['avg_duration']}s")
print(f"Outliers: {len(stats['outliers'])}")
```

### 3. ML-Powered Failure Prediction

**Purpose**: Predict which tests are likely to fail in next execution

**Algorithm**: Random Forest Classifier (100 trees)

**Features Used**:
- Test name (encoded)
- Environment (dev/qa/prod)
- Browser type
- Test duration
- Headless mode

**Model Training**:
```python
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()

# Train model
accuracy, model = analyzer.train_failure_predictor()
print(f"Model accuracy: {accuracy:.1%}")

# Make predictions
predictions = analyzer.predict_test_failures([
    {
        'test_name': 'test_checkout',
        'environment': 'staging',
        'browser': 'chrome',
        'duration': 2.5,
        'headless': False
    }
])

# Output:
🔮 Failure Predictions:
   • test_checkout: 85.5% failure risk - High risk
```

### 4. Test Reliability Scoring

**Purpose**: Rank tests by reliability for prioritization

**Scoring Formula**:
```python
reliability_score = (pass_rate * 0.7) + (performance_score * 0.3)
```

**Usage**:
```python
stats = analyzer.get_test_statistics()

# Most reliable tests
print("🏆 Most Reliable:")
for test in stats['most_reliable'][:5]:
    print(f"  {test['name']}: {test['pass_rate']:.1%}")

# Least reliable tests  
print("⚠️  Needs Attention:")
for test in stats['least_reliable'][:5]:
    print(f"  {test['name']}: {test['pass_rate']:.1%}")
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
- **For ML predictions**: 20-30+ test executions recommended
- **For flaky detection**: Minimum 3 executions per test
- **Best results**: 50+ executions across multiple environments

## 🚀 Usage Scenarios

### 1. CI/CD Integration

**Optimize test execution order** - run risky tests first:

```bash
# Pre-test analysis
python utils/ml_test_analyzer.py > reports/pre_test_analysis.txt

# Parse predictions
high_risk_tests=$(cat reports/pre_test_analysis.txt | grep "High risk" | awk '{print $2}')

# Run high-risk tests first
pytest $high_risk_tests --maxfail=1
```

### 2. Weekly Maintenance Report

```bash
# Generate weekly health report
python utils/ml_test_analyzer.py > reports/weekly_health_$(date +%Y%m%d).txt

# Review:
# - Flaky tests to fix
# - Performance degradations
# - Reliability trends
```

### 3. Intelligent Test Selection

**Run only tests likely to catch bugs**:

```python
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()

# Get failure predictions
all_tests = load_test_manifest()
predictions = analyzer.predict_test_failures(all_tests)

# Run only high-risk tests (>50% failure probability)
high_risk = [p for p in predictions if p['failure_probability'] > 0.5]
run_tests(high_risk)
```

### 4. Performance Monitoring

```python
# Continuous performance tracking
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()

current_stats = analyzer.analyze_performance_trends()
historical_baseline = load_baseline_metrics()

# Alert if degradation detected
if current_stats['avg_duration'] > historical_baseline * 1.2:
    send_alert("Performance degradation: 20% slower than baseline")
```

## 📈 Report Generation

### Console Report

```bash
python utils/ml_test_analyzer.py
```

**Output includes**:
- Dataset overview (total tests, date range)
- Flaky test list with pass rates
- Performance statistics
- Test reliability rankings
- ML model accuracy
- Failure predictions

### File Report

```python
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()
analyzer.generate_report(output_file='reports/ml_analysis.txt')
```

### Programmatic Access

```python
# Get structured data for custom processing
analyzer = MLTestAnalyzer()
data = analyzer.load_historical_data()

flaky_tests = analyzer.detect_flaky_tests()
performance_data = analyzer.analyze_performance_trends()
statistics = analyzer.get_test_statistics()

# Use data in custom workflows
for test in flaky_tests:
    create_jira_ticket(test)
    notify_team(test)
```

## 🔧 Configuration

### Custom Thresholds

```python
# Adjust flaky test threshold
flaky_tests = analyzer.detect_flaky_tests(min_runs=5)  # Default: 3

# Custom results directory
analyzer = MLTestAnalyzer(results_dir="custom/path/results")

# Output location
analyzer.generate_report(output_file="custom/report.txt")
```

### Model Tuning

```python
# Customize Random Forest parameters
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,  # More trees (default: 100)
    max_depth=10,      # Deeper trees
    random_state=42
)

analyzer.model = model
analyzer.train_failure_predictor()
```

## ⚠️ Limitations

### Small Datasets
- ML predictions require sufficient data
- With <20 executions, predictions may be unreliable
- Solution: Collect more historical data before relying on predictions

### All Passing Tests
- If all tests always pass, ML cannot learn failure patterns
- Solution: Include varied execution scenarios (different environments, browsers)

### Data Quality
- Inconsistent data format affects accuracy
- Missing fields reduce prediction quality
- Solution: Ensure consistent test result exports

## 💡 Best Practices

1. **Regular Execution**: Run analyzer daily/weekly to track trends
2. **Combine with Exports**: Auto-export test results for continuous analysis
3. **Prioritize Flaky Tests**: Fix identified flaky tests first - highest ROI
4. **Track Performance**: Monitor for gradual performance degradation
5. **CI/CD Integration**: Use predictions to optimize test execution order
6. **Data Hygiene**: Maintain consistent test result format

## 📚 Related Documentation

- [Test Results Export](TEST_DATA_MANAGEMENT.md#test-results-export) - How to export data for ML analysis
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Complementary analytics features
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Real-time performance tracking

## 🔗 File Locations

- **Implementation**: `utils/ml_test_analyzer.py`
- **Input Data**: `data/results/**/*.json`
- **Reports**: `reports/ml_analysis_*.txt`
- **Documentation**: `docs/ML_ANALYZER_GUIDE.md` (detailed guide)

---

**Value Proposition**: Leverage machine learning to predict failures, detect flaky tests, and optimize test execution - transforming reactive testing into proactive quality assurance.
