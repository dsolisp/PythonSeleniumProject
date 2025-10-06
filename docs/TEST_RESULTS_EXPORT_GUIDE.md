# Test Results Export Feature - Quick Guide

## Overview

The `data/results/` directory is used to export and archive test execution results in both YAML (human-readable) and JSON (machine-readable) formats.

## 📋 Quick Usage

### 1. Basic YAML Export

```python
from utils.test_data_manager import DataManager

manager = DataManager()

# Prepare your test results
test_results = {
    "total_tests": 25,
    "passed": 23,
    "failed": 2,
    "success_rate": 0.92,
    "test_details": [...],
}

# Export to YAML (saved in data/results/)
yaml_file = manager.save_test_results_yaml(test_results)
print(f"Results exported to: {yaml_file}")
# Output: data/results/test_results_20251006_160530.yml
```

### 2. JSON Export (Organized by Environment)

```python
# Export results for specific environments
manager.save_test_results(
    test_name="api_tests",
    results={"status": "passed", "duration": 1.2},
    environment="staging"  # or "local", "production", etc.
)
# Saved to: data/results/staging/api_tests_20251006_160530.json
```

### 3. Custom Filename

```python
# Use a custom filename instead of auto-generated timestamp
manager.save_test_results_yaml(
    test_results,
    filename="smoke_tests_results.yml"
)
# Saved to: data/results/smoke_tests_results.yml
```

## 🧪 Pytest Integration

### Method 1: Using Fixtures

```python
# conftest.py
import pytest
from utils.test_data_manager import DataManager

@pytest.fixture(scope="session")
def results_exporter():
    return DataManager()

# In your test file
def test_example(results_exporter):
    # Your test logic
    result = perform_test()
    assert result is True
    
    # Export results
    results_exporter.save_test_results_yaml({
        "test_name": "test_example",
        "status": "passed",
        "duration": 1.2
    })
```

### Method 2: Class-Level Integration

```python
class TestAPISuite:
    @classmethod
    def setup_class(cls):
        cls.manager = DataManager()
        cls.test_results = []
    
    def test_endpoint_1(self):
        # Test logic
        self.test_results.append({"name": "test_endpoint_1", "status": "passed"})
    
    def test_endpoint_2(self):
        # Test logic
        self.test_results.append({"name": "test_endpoint_2", "status": "passed"})
    
    @classmethod
    def teardown_class(cls):
        # Export all results after suite completes
        summary = {
            "test_suite": "API Tests",
            "total_tests": len(cls.test_results),
            "passed": sum(1 for t in cls.test_results if t["status"] == "passed"),
            "test_details": cls.test_results,
        }
        
        yaml_file = cls.manager.save_test_results_yaml(summary, filename="api_suite_results.yml")
        print(f"\n📊 Suite results: {yaml_file}")
```

### Method 3: pytest Hook (Automatic Export)

```python
# conftest.py
from utils.test_data_manager import DataManager

def pytest_sessionfinish(session, exitstatus):
    """Automatically export results after test session"""
    manager = DataManager()
    
    results = {
        "total_tests": session.testscollected,
        "passed": session.testscollected - session.testsfailed,
        "failed": session.testsfailed,
        "exit_code": exitstatus,
    }
    
    yaml_file = manager.save_test_results_yaml(results)
    print(f"\n✅ Test session results exported to: {yaml_file}")
```

## 🗂️ File Organization

```
data/
└── results/
    ├── test_results_20251006_160452.yml          # YAML exports (timestamped)
    ├── smoke_tests_results.yml                   # YAML exports (custom name)
    ├── local/                                    # Environment-specific JSON
    │   └── api_tests_20251006_160530.json
    ├── staging/
    │   └── api_tests_20251006_160530.json
    └── production/
        └── api_tests_20251006_160530.json
```

## 📊 Export Formats

### YAML Format (Human-Readable)

```yaml
environment_info:
  browser: chrome
  environment: staging
  os: macOS
performance_metrics:
  avg_duration: 2.67
  max_duration: 4.5
  min_duration: 1.2
test_details:
- duration: 1.2
  name: test_login
  status: passed
- duration: 4.5
  error: Element not found
  name: test_checkout
  status: failed
test_execution:
  failed: 2
  passed: 23
  success_rate: 92.00%
  timestamp: '2025-10-06T16:04:52.107899'
  total_tests: 25
```

### JSON Format (Machine-Readable)

```json
{
    "test_name": "api_tests",
    "environment": "staging",
    "timestamp": "20251006_160530",
    "execution_time": "2025-10-06T16:05:30.321161",
    "results": {
        "browser": "chrome",
        "tests": [
            {"name": "test_api_health", "status": "passed", "duration": 0.5},
            {"name": "test_api_users", "status": "passed", "duration": 1.2}
        ],
        "summary": {
            "total": 2,
            "passed": 2,
            "failed": 0
        }
    }
}
```

## 🧹 Cleanup Old Results

```python
manager = DataManager()

# Keep only last 30 days (default)
manager.cleanup_old_results(days_to_keep=30)

# Keep only last 7 days
manager.cleanup_old_results(days_to_keep=7)

# Remove all old results
manager.cleanup_old_results(days_to_keep=0)
```

## 🎯 Use Cases

### 1. CI/CD Integration
```bash
# Run tests and export results
pytest tests/ -v

# Results automatically exported to data/results/
# CI can parse JSON files for dashboard/metrics
```

### 2. Historical Tracking
```python
# Export each test run with timestamp
# Automatically organized by environment
# Easy to track trends over time
```

### 3. Report Generation
```python
# Load exported results
import yaml
with open('data/results/test_results_20251006_160530.yml') as f:
    results = yaml.safe_load(f)

# Generate custom reports
# Compare with previous runs
# Create dashboards
```

### 4. Team Collaboration
```yaml
# YAML format is git-friendly and human-readable
# Easy code reviews
# Clear documentation of test outcomes
```

## 📖 More Examples

Run the comprehensive examples:
```bash
python examples/export_test_results_example.py
```

This will:
- ✅ Create sample YAML exports
- ✅ Create environment-specific JSON exports  
- ✅ Show pytest integration patterns
- ✅ Demonstrate cleanup functionality
- ✅ Display real-world usage examples

## 🔗 Related Files

- **Implementation**: `utils/test_data_manager.py`
- **Examples**: `examples/export_test_results_example.py`
- **Tests**: `tests/unit/test_library_integrations.py::TestYAMLIntegration`
- **Storage**: `data/results/`

---

**💡 Tip**: Use YAML for human-readable reports and JSON for automated CI/CD processing!
