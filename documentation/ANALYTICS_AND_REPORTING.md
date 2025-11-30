# Analytics and Reporting

## Overview

The framework provides comprehensive analytics and reporting capabilities powered by **pandas**, **numpy**, and **Jinja2**. These tools transform raw test execution data into actionable insights.

## 🎯 When to Use

- **After test execution**: Generate detailed execution reports
- **Performance analysis**: Identify slow tests and bottlenecks
- **Trend tracking**: Monitor test suite health over time
- **Data export**: Share results with external tools (Excel, BI tools)
- **Executive reporting**: Create dashboard-style reports for stakeholders

> **Tip:** Run `python run_full_workflow.py` to automatically trigger all analytics, reporting, and exports.

## 🔧 Key Components

### 1. AdvancedTestReporter (`utils/test_reporter.py`)

**Purpose**: Comprehensive test result analysis and report generation

**Features**:
- DataFrame-based analytics with pandas
- Statistical analysis (mean, median, outlier detection)
- HTML dashboard generation with Jinja2
- CSV export for external analysis
- Performance trend tracking

**Usage Example**:
```python
from utils.test_reporter import AdvancedTestReporter, Result
from datetime import datetime

# Initialize reporter
reporter = AdvancedTestReporter()
reporter.start_test_suite('production_tests', 'prod', 'chrome')

# Add test results
result = Result(
    test_name='test_login',
    status='PASSED',
    duration=1.2,
    timestamp=datetime.now(),
    environment='prod',
    browser='chrome'
)
reporter.add_test_result(result)

# Generate analytics
analytics = reporter.generate_dataframe_analytics()
print(f"Success rate: {analytics['success_rate']:.1f}%")

# Export to CSV
csv_file = reporter.export_to_csv()
print(f"Results exported to: {csv_file}")
```

### 2. DataFrame Analytics

**Statistical analysis with pandas**:
- Average, median, min, max duration
- Standard deviation and outlier detection
- Success/failure rates by environment
- Performance trends over time

**Example Analysis**:
```python
import pandas as pd
import numpy as np

# Analyze by environment
env_stats = df.groupby('environment').agg({
    'duration': ['mean', 'std', 'count'],
    'status': lambda x: (x == 'PASSED').mean() * 100
})

# Identify outliers (Z-score > 2)
df['z_score'] = np.abs((df['duration'] - df['duration'].mean()) / df['duration'].std())
outliers = df[df['z_score'] > 2]
```

### 3. HTML Dashboard Generation

**Template-based Reporting with Jinja2**:

```python
from jinja2 import Template

# Custom dashboard template
template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>{{ suite_name }} - Test Report</title>
    <style>
        .metric { background: #f0f8ff; padding: 20px; margin: 10px; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
    </style>
</head>
<body>
    <h1>{{ suite_name }}</h1>
    <div class="metric">
        <h3>Summary</h3>
        <p>Environment: {{ environment }}</p>
        <p>Total Tests: {{ total_tests }}</p>
        <p>Success Rate: {{ success_rate }}%</p>
    </div>
    <table>
        <tr><th>Test</th><th>Status</th><th>Duration</th></tr>
        {% for test in results %}
        <tr>
            <td>{{ test.test_name }}</td>
            <td class="{{ test.status.lower() }}">{{ test.status }}</td>
            <td>{{ test.duration }}s</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
''')

# Render report
html = template.render(
    suite_name='Production Tests',
    environment='prod',
    total_tests=50,
    success_rate=94.0,
    results=test_results
)
```

## 📊 Report Types

### 1. JSON Reports
**Use case**: CI/CD integration, programmatic processing
```python
reporter.generate_json_report('reports/json/test_results.json')
```

### 2. CSV Reports
**Use case**: Excel analysis, data visualization tools
```python
reporter.export_to_csv('reports/analytics/test_data.csv')
```

### 3. HTML Dashboards
```python
reporter.generate_html_dashboard('reports/html/dashboard.html')
```

## 🔬 Advanced Analytics

### Performance Outlier Detection

```python
# Z-score formula: (x - mean) / std_dev
# Tests with |Z| > 2 are considered outliers

outliers = reporter.detect_performance_outliers(threshold=2.0)
for test in outliers:
    print(f"{test['name']}: {test['duration']}s (Z-score: {test['z_score']:.2f})")
```

### Trend Analysis

Track test performance over multiple executions:

```python
trends = reporter.analyze_trends(days=30)
print(f"Average duration trend: {trends['duration_trend']}")
print(f"Success rate trend: {trends['success_rate_trend']}")
```

## 🎨 Customization

Create your own Jinja2 templates:

```python
custom_template = """
{% for test in failed_tests %}
<div class="failed-test">
    <h3>{{ test.test_name }}</h3>
    <p>Error: {{ test.error_message }}</p>
</div>
{% endfor %}
"""

reporter.generate_custom_report(custom_template, output='custom_report.html')
```

## 📈 Integration Points

### With CI/CD Pipelines

```yaml
# GitHub Actions example
- name: Generate Test Report
  run: |
    python -c "
    from utils.test_reporter import AdvancedTestReporter
    reporter = AdvancedTestReporter()
    reporter.load_latest_results()
    reporter.export_to_csv('reports/ci_results.csv')
    "

- name: Upload Reports
  uses: actions/upload-artifact@v3
  with:
    name: test-reports
    path: reports/
```

### With External Tools

**Export to Excel**:
```python
# CSV can be opened directly in Excel
reporter.export_to_csv('quarterly_results.csv')
```

**Power BI / Tableau Integration**:
```python
# JSON format works well with BI tools
reporter.generate_json_report('bi_data.json')
```

## 📚 Related Documentation

- [Machine Learning Analysis](ML_INTEGRATION.md) - ML-powered test intelligence
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Real-time metrics

## 🔗 File Locations

- **Implementation**: `utils/test_reporter.py`
- **Templates**: `reports/templates/` (optional)
- **Output**: `reports/json/`, `reports/html/`, `reports/analytics/`

---

**Value Proposition**: Transform raw test results into actionable insights with enterprise-grade analytics powered by pandas, numpy, and Jinja2.
