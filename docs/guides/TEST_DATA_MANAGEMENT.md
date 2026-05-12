# Test Data Management

## Overview

Data management system supporting **JSON**, **YAML**, and **CSV** formats for flexible, environment-specific test data handling.

## 🎯 When to Use

- **Data-driven testing**: Parameterized tests with external data
- **Environment management**: Different data per environment (local/qa/prod)
- **Configuration management**: Complex, hierarchical test configurations
- **Test result export**: Save execution results in YAML format
- **Dynamic data generation**: Create search scenarios on-demand

## 🔧 Key Components

### DataManager (`utils/test_data_manager.py`)

**Purpose**: Unified interface for test data operations

**Available Methods**:
| Method | Purpose |
|--------|---------|
| `load_test_data(filename, environment)` | Load JSON/YAML/CSV with caching |
| `load_yaml_config(config_name, environment)` | Load YAML config (creates default if missing) |
| `save_test_results_yaml(results, filename)` | Export test results to YAML |
| `get_search_scenarios(environment)` | Get search test scenarios |
| `get_user_accounts(role, environment)` | Get user accounts, optionally filtered |
| `generate_search_data(count)` | Generate dynamic search scenarios |
| `cleanup_old_results(days_to_keep)` | Remove old result files |
| `validate_data_schema(data, schema_name)` | Validate data structure |

## 📁 Data Organization

### Directory Structure

```
data/
├── test_data.json              # Main test data
├── configs/                    # YAML configurations
│   ├── browser_config_local.yml
│   ├── browser_settings_qa.yml
│   ├── browser_settings_production.yml
│   └── browser_settings_test.yml
└── results/                    # Test execution results
    ├── local/
    ├── staging/
    └── production/
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
            "password": "admin_pass"
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

**Purpose**: Save execution results for reporting

```python
# After test execution
test_results = {
    'total_tests': 10,
    'passed': 8,
    'failed': 2,
    'success_rate': 0.8,
    'test_details': [
        {'name': 'test_login', 'status': 'passed', 'duration': 1.2},
        {'name': 'test_checkout', 'status': 'failed', 'duration': 3.5}
    ],
    'performance_metrics': {'avg_duration': 2.35},
    'environment_info': {'browser': 'chrome'}
}

# Export to YAML
path = manager.save_test_results_yaml(test_results)
# Saves to: data/results/results_20251006_160530.yml
print(f"Results saved to: {path}")
```

### 5. Dynamic Data Generation

```python
# Generate search test scenarios
scenarios = manager.generate_search_data(count=5)
# Returns list of dicts with:
# - name, search_term, expected_results_count
# - timeout, expected_title_contains
# - generated=True, created_at timestamp

for scenario in scenarios:
    print(f"Search: {scenario['search_term']}")
```

### 6. Data Accessors

```python
# Get search scenarios from test_data.json
scenarios = manager.get_search_scenarios(environment='default')

# Get user accounts, optionally filtered by role
all_users = manager.get_user_accounts()
admins = manager.get_user_accounts(role='admin')
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

### Example 3: Test Result Export

```python
# Export test results after execution
from utils.test_data_manager import DataManager

manager = DataManager()

# Collect results
results = {
    'total_tests': 25,
    'passed': 23,
    'failed': 2,
    'success_rate': 0.92,
    'test_details': [
        {'name': 'test_login', 'status': 'passed', 'duration': 1.2},
        {'name': 'test_checkout', 'status': 'failed', 'duration': 3.5}
    ]
}

# Save to YAML
path = manager.save_test_results_yaml(results)
print(f"Results saved: {path}")
```

> **Note**: For automatic test history tracking, pytest-history handles this automatically.
> Just run `pytest tests/` and results are stored in `.test-results.db`.

## 🔗 Integration with Test History

Test results are tracked automatically by pytest-history:

```bash
# Run tests - history tracked automatically
pytest tests/

# View flaky tests
pytest-history flakes

# View test run history
pytest-history list runs
```

For manual result exports (e.g., for external reporting), use DataManager:

```python
manager = DataManager()
manager.save_test_results_yaml(results)
# Saves to: data/results/results_[timestamp].yml
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
# Validate against predefined schemas
# Available schemas: 'search_scenario', 'user_account', 'api_endpoint'
is_valid = manager.validate_data_schema(data, 'search_scenario')
# Returns True if data has required fields: ['name', 'search_term']
```

### Cleanup Old Results

```python
# Remove result files older than 30 days
manager.cleanup_old_results(days_to_keep=30)
```

## 📚 Related Documentation

- [Test Analytics](TEST_ANALYTICS.md) - Flaky test detection via pytest-history
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Report generation
- [API Testing](API_TESTING.md) - Data-driven API tests

## 🔗 File Locations

- **Implementation**: `utils/test_data_manager.py`
- **Test Data**: `data/test_data.json`
- **Configurations**: `data/configs/*.yml`
- **Results**: `data/results/*.yml`

## 💡 Best Practices

1. **Separate environments**: Use different data files per environment
2. **YAML for configs**: Use YAML for complex, nested configurations
3. **JSON for data**: Use JSON for programmatic test data
4. **Version control**: Commit data structure, not sensitive values
5. **Cleanup regularly**: Use `cleanup_old_results()` to prevent bloat

---

**Value Proposition**: Flexible, multi-format data management enabling data-driven testing with environment-specific configurations.
