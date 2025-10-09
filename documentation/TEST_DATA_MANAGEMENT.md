# Test Data Management

## Unified Workflow

> **Recommended:** Use the integrated workflow script for all test data export and management. Test data export and result archiving are now automatically triggered by running:

```bash
python run_full_workflow.py
```

# Test Data Management

## Overview

Comprehensive data management system supporting **JSON**, **YAML**, and **CSV** formats for flexible, environment-specific test data handling.

## 🎯 When to Use

- **After running the workflow script**: Test results are exported and managed automatically
- **Data-driven testing**: Parameterized tests with external data (see exported results)
- **Environment management**: Different data per environment (see results in `data/results/`)
- **Configuration management**: Complex, hierarchical test configurations (see YAML/JSON in `data/configs/`)
- **Test result export**: Results are saved for analysis and ML (see `data/results/`)
- **Dynamic data generation**: Still available for advanced scenarios

- **Data-driven testing**: Parameterized tests with external data
- **Environment management**: Different data per environment (local/dev/qa/prod)
- **Configuration management**: Complex, hierarchical test configurations
- **Test result export**: Save execution results for analysis
- **Dynamic data generation**: Create test users, scenarios on-demand

## 🔧 Key Components

### 4. Export Test Results (Automated)

**Purpose**: Unified interface for all test data operations

**Features**:
- Multi-format support (JSON, YAML, CSV)
- Environment-specific data loading
- Data caching for performance
- Dynamic data generation
- Result archiving

## 📁 Data Organization

### Directory Structure

```
data/
├── test_data.json              # Main test data
├── configs/                    # YAML configurations
│   ├── browser_settings_local.yml
│   ├── browser_settings_qa.yml
│   └── browser_settings_prod.yml
├── results/                    # Test execution results
│   ├── local/
│   ├── staging/
│   └── production/
└── environments/               # Environment-specific data
    ├── local.json
    ├── qa.json
    └── prod.json
```

## 🎨 Usage Patterns

### 1. Load Test Data (JSON)

```python
from utils.test_data_manager import DataManager

manager = DataManager()

# Load main test data
data = manager.load_test_data('test_data')

# Access test scenarios
search_query = data['scenarios']['basic_search']['query']
expected_result = data['scenarios']['basic_search']['expected_results'][0]
```

**Example JSON Structure**:
```json
{
    "users": {
        "standard": {
            "username": "test_user",
            "password": "secure_pass"
        },
        "admin": {
            "username": "admin_user",
        Test results exported by the workflow script are automatically consumed by the ML Analyzer—no manual steps required.
        }
    },
    "scenarios": {
        "basic_search": {
            "query": "selenium python",
            "expected_results": ["Selenium", "Python"]
        }
    }
}
```

### 2. Load YAML Configuration

**Purpose**: Complex, hierarchical configurations (better than JSON for nested structures)

```python
# Load environment-specific config
config = manager.load_yaml_config('browser_settings', 'qa')

# Access configuration
timeout = config['timeouts']['explicit']
browser = config['browser']['type']
headless = config['browser']['headless']
```

**Example YAML Configuration**:
```yaml
# browser_settings_qa.yml
browser:
  type: chrome
  headless: true
  window_size: 1920x1080
  
timeouts:
  implicit: 10
  explicit: 20
  page_load: 30
  
capabilities:
  accept_insecure_certs: true
  page_load_strategy: normal
  
logging:
  level: INFO
  enable_screenshots: true
```

### 3. Environment-Specific Data

```python
# Load data for specific environment
qa_data = manager.load_test_data('user_credentials', environment='qa')
prod_data = manager.load_test_data('user_credentials', environment='prod')

# Different values per environment
qa_url = qa_data['base_url']      # https://qa.example.com
prod_url = prod_data['base_url']   # https://prod.example.com
```

### 4. Export Test Results

**Purpose**: Save execution results for ML analysis and reporting

```python
# After test execution
test_results = {
    'test_name': 'api_tests',
    'environment': 'staging',
    'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
    'results': {
        'browser': 'chrome',
        'headless': False,
        'tests': [
            {
                'name': 'test_login',
                'status': 'passed',
                'duration': 1.2
            },
            {
                'name': 'test_checkout',
                'status': 'failed',
                'duration': 3.5
            }
        ]
    }
}

# Export to JSON
manager.save_test_results_json(test_results)
# Saves to: data/results/staging/api_tests_20251006_160530.json

# Export to YAML (human-readable)
manager.save_test_results_yaml(test_results)
# Saves to: data/results/staging/api_tests_20251006_160530.yml
```

### 5. Dynamic Data Generation

```python
# Generate test user on-demand
user = manager.generate_test_user(
    prefix='testuser',
    environment='qa'
)
# Returns: {'username': 'testuser_qa_1234', 'password': 'auto_generated_pass'}

# Generate test scenario
scenario = manager.generate_test_scenario(
    scenario_type='search',
    complexity='simple'
)
```

## 🎯 Real-World Examples

### Example 1: Data-Driven Login Test

```python
from utils.test_data_manager import DataManager
import pytest

@pytest.fixture
def test_data():
    manager = DataManager()
    return manager.load_test_data('test_data')

@pytest.mark.parametrize("user_type", ["standard", "admin", "guest"])
def test_login_various_users(test_data, user_type):
    user = test_data['users'][user_type]
    
    login_page.enter_username(user['username'])
    login_page.enter_password(user['password'])
    login_page.click_login()
    
    assert login_page.is_logged_in()
```

### Example 2: Environment-Aware Configuration

```python
# conftest.py
import os
from utils.test_data_manager import DataManager

@pytest.fixture(scope='session')
def config():
    manager = DataManager()
    env = os.getenv('TEST_ENV', 'local')
    return manager.load_yaml_config('browser_settings', env)

def test_with_env_config(driver, config):
    # Use environment-specific settings
    driver.set_page_load_timeout(config['timeouts']['page_load'])
    driver.get(config['base_url'])
```

### Example 3: Test Result Export Integration

```python
# conftest.py - Automatic export after test session
import pytest
from utils.test_data_manager import DataManager

@pytest.fixture(scope='session')
def test_results_collector():
    results = []
    yield results
    
    # Export results after all tests complete
    if results:
        manager = DataManager()
        export_data = {
            'test_name': 'regression_suite',
            'environment': os.getenv('TEST_ENV', 'local'),
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'results': {
                'browser': 'chrome',
                'tests': results
            }
        }
        manager.save_test_results_json(export_data)

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        test_results_collector = item.funcargs.get('test_results_collector')
        if test_results_collector is not None:
            test_results_collector.append({
                'name': item.name,
                'status': 'passed' if report.passed else 'failed',
                'duration': report.duration
            })
```

## 🔗 Integration with ML Analyzer

Test results exported via DataManager are automatically consumed by ML Analyzer:

```python
# Export results during test execution
manager = DataManager()
manager.save_test_results_json(results)

# ML Analyzer picks them up automatically
from utils.ml_test_analyzer import MLTestAnalyzer
analyzer = MLTestAnalyzer()  # Reads from data/results/
analyzer.load_historical_data()
analyzer.detect_flaky_tests()
```

## 📊 Supported Formats

### JSON
**Best for**: Structured data, API payloads, programmatic access
```json
{
    "test_scenarios": [...],
    "users": {...}
}
```

### YAML  
**Best for**: Configuration files, hierarchical data, human editing
```yaml
database:
  host: localhost
  port: 5432
  credentials:
    user: admin
    password: secret
```

### CSV
**Best for**: Tabular data, Excel compatibility, bulk data
```csv
username,password,role
user1,pass1,admin
user2,pass2,user
```

## 🎨 Advanced Features

### Data Caching

```python
# First load - reads from file
data1 = manager.load_test_data('test_data')

# Second load - returns cached version (faster)
data2 = manager.load_test_data('test_data')
```

### Data Validation

```python
# Validate required fields
try:
    manager.validate_test_data(data, required_fields=['users', 'scenarios'])
except ValueError as e:
    print(f"Invalid data: {e}")
```

### Data Versioning

```python
# Archive old results
manager.archive_results(older_than_days=30)

# Load specific version
historical_data = manager.load_historical_data('2024_Q1')
```

## 📚 Related Documentation

- [ML Integration](ML_INTEGRATION.md) - How ML Analyzer uses exported data
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Analyzing test results
- [API Testing](API_TESTING.md) - Data-driven API tests

## 🔗 File Locations

- **Implementation**: `utils/test_data_manager.py`
- **Test Data**: `data/test_data.json`
- **Configurations**: `data/configs/*.yml`
- **Results**: `data/results/[environment]/*.json`
- **Examples**: `examples/export_test_results_example.py`

## 💡 Best Practices

1. **Separate environments**: Use different data files per environment
2. **YAML for configs**: Use YAML for complex, nested configurations
3. **JSON for data**: Use JSON for programmatic test data
4. **Regular exports**: Export test results after each run
5. **Version control**: Commit data structure, not sensitive values
6. **Data cleanup**: Archive old results to prevent directory bloat

---

**Value Proposition**: Flexible, multi-format data management enabling true data-driven testing with environment-specific configurations and seamless ML integration.
