# ML Test Analyzer - Quick Reference

## 🤖 What It Does

The ML Test Analyzer (`utils/ml_test_analyzer.py`) uses machine learning to analyze your historical test results and provide intelligence about your test suite.

## 📊 Features

### 1. **Flaky Test Detection** 🔄
Identifies tests that fail inconsistently:
```bash
⚠️  Found 3 flaky tests:
   • test_checkout: 65.0% pass rate (13/20 passed)
   • test_payment: 80.0% pass rate (16/20 passed)
   • test_login: 90.0% pass rate (18/20 passed)
```

### 2. **Performance Trend Analysis** 📈
Detects performance anomalies and slow tests:
```bash
📈 Performance Statistics:
   Average duration: 2.45s
   Median duration:  1.80s
   
⚠️  Found 5 performance outliers:
   • test_heavy_processing: 15.30s (environment: staging)
   • test_large_dataset: 12.80s (environment: production)
```

### 3. **Test Reliability Scoring** 🏆
Ranks tests by reliability:
```bash
🏆 Most Reliable Tests:
   • test_api_health: 100.0% pass rate, 0.50s avg
   • test_database_connection: 99.5% pass rate, 0.75s avg

⚠️  Least Reliable Tests:
   • test_checkout: 65.0% pass rate, 4.50s avg
   • test_payment_gateway: 72.0% pass rate, 3.20s avg
```

### 4. **ML Failure Prediction** 🔮
Predicts which tests are likely to fail:
```bash
🔮 Failure Predictions:
   • test_checkout: 85.5% failure risk - High risk - run first
   • test_payment: 62.3% failure risk - Medium risk - monitor
   • test_login: 12.1% failure risk - Low risk - standard execution
```

## 🚀 Usage

### Basic Usage

```bash
# Run the analyzer
python utils/ml_test_analyzer.py

# Or with explicit Python path
PYTHONPATH=/path/to/project python utils/ml_test_analyzer.py
```

### Programmatic Usage

```python
from utils.ml_test_analyzer import MLTestAnalyzer

# Initialize analyzer
analyzer = MLTestAnalyzer()

# Load historical data
df = analyzer.load_historical_data()

# Run analyses
flaky_tests = analyzer.detect_flaky_tests()
performance_stats = analyzer.analyze_performance_trends()
test_stats = analyzer.get_test_statistics()

# Train ML model
accuracy, model = analyzer.train_failure_predictor()

# Predict failures for upcoming tests
predictions = analyzer.predict_test_failures([
    {
        'test_name': 'test_checkout',
        'environment': 'staging',
        'browser': 'chrome',
        'duration': 2.5,
        'headless': False
    }
])

# Generate comprehensive report
analyzer.generate_report('reports/my_analysis.txt')
```

## 📋 Prerequisites

### Required
- Python 3.8+
- pandas (for data analysis)
- numpy (for numerical operations)

### Optional (for ML features)
- scikit-learn (for ML predictions)

```bash
# Install ML dependencies
pip install scikit-learn

# Or add to requirements.txt
scikit-learn>=1.3.0
```

## 📂 Data Requirements

The analyzer reads test results from `data/results/` directory:

```
data/results/
├── local/
│   └── api_tests_20251006_160530.json
├── staging/
│   └── api_tests_20251006_160530.json
└── production/
    └── api_tests_20251006_160530.json
```

### Expected JSON Format

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

## 🎯 Real-World Use Cases

### 1. **CI/CD Optimization**
```bash
# Run analyzer before test execution
python utils/ml_test_analyzer.py

# High-risk tests identified → Run those first
# Low-risk tests → Can be skipped in rapid feedback cycles
```

### 2. **Test Suite Maintenance**
```bash
# Weekly maintenance report
python utils/ml_test_analyzer.py > reports/weekly_test_health.txt

# Action items:
# - Fix flaky tests
# - Investigate performance outliers
# - Optimize slow tests
```

### 3. **Intelligent Test Selection**
```python
# Only run tests likely to catch bugs
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()
predictions = analyzer.predict_test_failures(all_tests)

# Run only high-risk tests for this code change
high_risk_tests = [p for p in predictions if p['failure_probability'] > 0.5]
```

### 4. **Performance Monitoring**
```python
# Track performance trends over time
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()
stats = analyzer.analyze_performance_trends()

if stats['avg_duration'] > historical_average * 1.2:
    alert("Performance degradation detected!")
```

## 📊 Output Reports

### Console Output
Real-time analysis results displayed during execution.

### Text Report
Comprehensive report saved to `reports/ml_analysis_report.txt`:
- Dataset overview
- Flaky tests list
- Performance statistics
- Test reliability rankings
- ML model performance

## 🔧 Configuration

### Customize Flaky Test Threshold
```python
analyzer = MLTestAnalyzer()
analyzer.load_historical_data()

# Require minimum 5 runs instead of default 3
flaky_tests = analyzer.detect_flaky_tests(min_runs=5)
```

### Custom Results Directory
```python
# Use different results directory
analyzer = MLTestAnalyzer(results_dir="custom/path/to/results")
```

### Custom Report Output
```python
# Save report to custom location
analyzer.generate_report(output_file="reports/custom_report.txt")
```

## 🎓 ML Model Details

### Algorithm
- **Random Forest Classifier** (scikit-learn)
- 100 decision trees
- Predicts binary outcome: pass/fail

### Features Used
- Test name (encoded)
- Environment (encoded)
- Browser type (encoded)
- Test duration
- Headless mode

### Training
- Automatic train/test split (80/20)
- Cross-validation for accuracy
- Feature importance analysis

### Prediction Output
- Failure probability (0.0 to 1.0)
- Risk classification (High/Medium/Low)
- Actionable recommendations

## 🚨 Limitations

### Small Dataset
- ML model requires sufficient historical data
- Minimum ~20-30 test executions recommended
- With fewer samples, predictions may be inaccurate

### All Passing Tests
- If all tests always pass, ML cannot learn failure patterns
- Analyzer still provides valuable statistics

### Data Quality
- Requires consistent test result format
- Missing data fields may affect accuracy

## 💡 Tips

### 1. **Regular Execution**
Run the analyzer regularly (daily/weekly) to track trends:
```bash
# Add to cron job or CI/CD pipeline
0 9 * * 1 python utils/ml_test_analyzer.py > reports/weekly_analysis.txt
```

### 2. **Combine with Test Exports**
Automatically export test results after each run:
```python
# In conftest.py
def pytest_sessionfinish(session, exitstatus):
    from utils.test_data_manager import DataManager
    manager = DataManager()
    # Export results...
    
    # Then run analyzer
    from utils.ml_test_analyzer import MLTestAnalyzer
    analyzer = MLTestAnalyzer()
    analyzer.load_historical_data()
    analyzer.generate_report()
```

### 3. **Focus on Flaky Tests**
Prioritize fixing flaky tests identified by the analyzer - they cause the most pain in CI/CD.

### 4. **Track Performance Trends**
Compare reports over time to identify gradual performance degradation.

## 📚 Related Files

- **Implementation**: `utils/ml_test_analyzer.py`
- **Data Source**: `data/results/**/*.json`
- **Test Data Exporter**: `utils/test_data_manager.py`
- **Examples**: `examples/export_test_results_example.py`
- **Documentation**: `docs/TEST_RESULTS_EXPORT_GUIDE.md`

## 🔗 Integration Points

- **Test Export** → ML Analyzer → **CI/CD Decisions**
- **Historical Data** → ML Analyzer → **Test Optimization**
- **Performance Metrics** → ML Analyzer → **Alerts/Monitoring**

---

**🤖 Built with pandas, numpy, and scikit-learn for intelligent test suite analysis!**
