# API Testing Guide

## Overview

Comprehensive REST API testing with conditional Allure reporting, structured logging, and PyHamcrest assertions.

## 🎯 When to Use

- **API validation**: Test REST endpoints for correctness
- **Integration testing**: Verify API contracts between services
- **Contract testing**: Ensure API specifications are met
- **Regression testing**: Validate API changes don't break functionality
- **Performance testing**: Monitor API response times

## 🔧 Key Components

### 1. Unified API Tests (`tests/api/test_api.py`)

**Features**:
- Conditional Allure reporting (toggle on/off)
- Structured JSON logging
- PyHamcrest rich assertions
- Request/response tracking
- Performance monitoring

### 2. Conditional Allure Reporting

**Purpose**: Enable rich reporting when needed, fast execution when not

**Configuration** (`config/settings.py`):
```python
class Settings:
    ENABLE_ALLURE = os.getenv("ENABLE_ALLURE", "true").lower() == "true"
```

**Benefits**:
- **ENABLE_ALLURE=true**: Rich reports, step-by-step tracking, attachments
- **ENABLE_ALLURE=false**: Faster execution (~2% speed gain), clean output

## 📋 Test Structure

### Basic Test Pattern

```python
import allure
import requests
from hamcrest import assert_that, equal_to, greater_than
from config.settings import settings

@allure.epic("API Testing")
@allure.feature("User Management")
class TestUserAPI:
    
    def setup_method(self, method):
        """Setup before each test."""
        if settings.ENABLE_ALLURE:
            from utils.structured_logger import get_test_logger
            self.test_logger = get_test_logger(method.__name__)
        
        self.base_url = "https://api.example.com"
        self.session = requests.Session()
    
    @allure.story("GET Operations")
    @allure.title("Verify GET /users endpoint")
    def test_get_users(self):
        """Test GET /users returns user list."""
        
        # Conditional Allure step
        if settings.ENABLE_ALLURE:
            with allure.step("Send GET request to /users"):
                response = self.session.get(f"{self.base_url}/users")
        else:
            response = self.session.get(f"{self.base_url}/users")
        
        # PyHamcrest assertions
        assert_that(response.status_code, equal_to(200))
        assert_that(len(response.json()), greater_than(0))
        
        # Conditional logging
        if settings.ENABLE_ALLURE and hasattr(self, 'test_logger'):
            self.test_logger.log_assertion(
                "Status code is 200",
                response.status_code == 200,
                expected=200,
                actual=response.status_code
            )
```

## 🚀 Running API Tests

### With Allure Reporting (Default)

```bash
# Run with rich Allure reports
pytest tests/api/ -v --alluredir=reports/allure-results --clean-alluredir

# Generate and view HTML report
allure serve reports/allure-results
```

### Without Allure (Fast Mode)

```bash
# Faster execution, clean console output
ENABLE_ALLURE=false pytest tests/api/ -v

# Or set permanently
export ENABLE_ALLURE=false
pytest tests/api/ -v
```

### Specific Test Execution

```bash
# Run specific test class
pytest tests/api/test_api.py::TestUserAPI -v

# Run specific test method
pytest tests/api/test_api.py::TestUserAPI::test_get_users -v

# Run with markers
pytest tests/api/ -m "smoke" -v
pytest tests/api/ -m "critical" -v
```

## 🎨 PyHamcrest Assertions

### Basic Assertions

```python
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    is_not,
    greater_than,
    less_than,
    contains_string,
    has_key,
    instance_of
)

# Equality
assert_that(response.status_code, equal_to(200))
assert_that(user['active'], is_(True))

# Comparisons
assert_that(response.elapsed.total_seconds(), less_than(2.0))
assert_that(len(data), greater_than(0))

# String matching
assert_that(response.text, contains_string("success"))

# Dictionary/JSON assertions
assert_that(response.json(), has_key("data"))
assert_that(response.json()['data'], instance_of(list))
```

### Advanced Assertions

```python
from hamcrest import (
    has_entries,
    has_items,
    all_of,
    any_of,
    not_none,
    matches_regexp
)

# Complex object matching
assert_that(user, has_entries({
    'id': greater_than(0),
    'email': contains_string('@'),
    'active': is_(True)
}))

# Collection assertions
assert_that(user_list, has_items(
    has_entries({'role': 'admin'}),
    has_entries({'role': 'user'})
))

# Combined conditions
assert_that(response_time, all_of(
    greater_than(0),
    less_than(1000)
))

# Pattern matching
assert_that(user['email'], matches_regexp(r'^[\w\.-]+@[\w\.-]+\.\w+$'))
```

## 📊 Structured Logging

### API Request Logging

```python
from utils.structured_logger import get_logger

logger = get_logger("APITests")

# Log API request
response = session.get(url)
logger.api_request(
    method="GET",
    url=url,
    status_code=response.status_code,
    response_time=response.elapsed.total_seconds() * 1000
)

# Output (JSON):
{
    "event_type": "api_request",
    "method": "GET",
    "url": "https://api.example.com/users",
    "status_code": 200,
    "response_time": 245.5,
    "timestamp": "2025-10-08T10:30:15.123Z",
    "level": "info"
}
```

### Test Execution Logging

```python
from utils.structured_logger import get_test_logger

test_logger = get_test_logger("test_create_user")

# Start test
test_logger.start_test(
    test_type="API",
    test_suite="User Management",
    framework="requests"
)

# Log steps
test_logger.log_step("Send POST request", "api_call")
test_logger.log_step("Validate response", "assertion")

# Log assertions
test_logger.log_assertion(
    "Status code is 201",
    response.status_code == 201,
    expected=201,
    actual=response.status_code
)

# End test
test_logger.end_test("PASS")
```

## 🎯 Real-World Examples

### Example 1: CRUD Operations

```python
@allure.feature("User CRUD")
class TestUserCRUD:
    
    @allure.story("Create User")
    def test_create_user(self):
        """Test POST /users creates new user."""
        new_user = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
        
        response = self.session.post(
            f"{self.base_url}/users",
            json=new_user
        )
        
        assert_that(response.status_code, equal_to(201))
        created_user = response.json()
        assert_that(created_user, has_entries({
            'name': new_user['name'],
            'email': new_user['email']
        }))
        assert_that(created_user['id'], greater_than(0))
        
        return created_user['id']
    
    @allure.story("Read User")
    def test_get_user(self):
        """Test GET /users/{id} returns user details."""
        user_id = self.test_create_user()
        
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        
        assert_that(response.status_code, equal_to(200))
        user = response.json()
        assert_that(user['id'], equal_to(user_id))
    
    @allure.story("Update User")
    def test_update_user(self):
        """Test PUT /users/{id} updates user."""
        user_id = self.test_create_user()
        
        updated_data = {"name": "Updated Name"}
        response = self.session.put(
            f"{self.base_url}/users/{user_id}",
            json=updated_data
        )
        
        assert_that(response.status_code, equal_to(200))
        assert_that(response.json()['name'], equal_to("Updated Name"))
    
    @allure.story("Delete User")
    def test_delete_user(self):
        """Test DELETE /users/{id} removes user."""
        user_id = self.test_create_user()
        
        response = self.session.delete(f"{self.base_url}/users/{user_id}")
        assert_that(response.status_code, equal_to(204))
        
        # Verify deletion
        get_response = self.session.get(f"{self.base_url}/users/{user_id}")
        assert_that(get_response.status_code, equal_to(404))
```

### Example 2: Error Handling

```python
@allure.feature("Error Handling")
class TestAPIErrors:
    
    def test_404_not_found(self):
        """Test API returns 404 for non-existent resource."""
        response = self.session.get(f"{self.base_url}/users/999999")
        
        assert_that(response.status_code, equal_to(404))
        assert_that(response.json(), has_key('error'))
    
    def test_400_bad_request(self):
        """Test API returns 400 for invalid data."""
        invalid_user = {"email": "invalid-email"}  # Missing required fields
        
        response = self.session.post(
            f"{self.base_url}/users",
            json=invalid_user
        )
        
        assert_that(response.status_code, equal_to(400))
        assert_that(response.json(), has_entries({
            'error': contains_string('validation'),
            'details': instance_of(list)
        }))
    
    def test_401_unauthorized(self):
        """Test API returns 401 without authentication."""
        session = requests.Session()  # No auth headers
        
        response = session.post(
            f"{self.base_url}/admin/users",
            json={"name": "Admin User"}
        )
        
        assert_that(response.status_code, equal_to(401))
```

### Example 3: Performance Testing

```python
@allure.feature("Performance")
class TestAPIPerformance:
    
    def test_response_time_threshold(self):
        """Test API responds within acceptable time."""
        import time
        
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/users")
        response_time = (time.time() - start_time) * 1000  # ms
        
        assert_that(response.status_code, equal_to(200))
        assert_that(response_time, less_than(1000), 
                   f"Response time {response_time:.0f}ms exceeds threshold")
    
    def test_concurrent_requests(self):
        """Test API handles concurrent requests."""
        from concurrent.futures import ThreadPoolExecutor
        
        def make_request():
            response = self.session.get(f"{self.base_url}/users")
            return response.status_code == 200
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda _: make_request(), range(50)))
        
        success_rate = sum(results) / len(results) * 100
        assert_that(success_rate, greater_than(95), 
                   f"Success rate {success_rate:.1f}% below threshold")
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run API tests (fast mode)
        env:
          ENABLE_ALLURE: false
        run: pytest tests/api/ -v --junitxml=reports/junit.xml
      
      - name: Run API tests (full reporting)
        if: github.event_name == 'pull_request'
        run: pytest tests/api/ -v --alluredir=reports/allure-results
      
      - name: Generate Allure report
        if: always()
        run: allure generate reports/allure-results -o reports/allure-html
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: api-test-reports
          path: reports/
```

## 💡 Best Practices

1. **Use PyHamcrest**: More readable assertions than standard assert
2. **Conditional Allure**: Enable for debugging, disable for speed
3. **Structured logging**: JSON logs for aggregation/analysis
4. **Request/Response validation**: Verify both happy and error paths
5. **Performance thresholds**: Set acceptable response times
6. **Test isolation**: Each test should be independent
7. **Cleanup**: Remove test data after execution

## 📚 Related Documentation

- [Performance Monitoring](PERFORMANCE_MONITORING.md) - API load testing
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Test result analysis
- [Error Recovery](ERROR_RECOVERY_AND_MONITORING.md) - Network retry strategies

## 🔗 File Locations

- **Tests**: `tests/api/test_api.py`
- **Settings**: `config/settings.py`
- **Structured Logger**: `utils/structured_logger.py`
- **Reports**: `reports/allure-results/`, `reports/json/`

---

**Value Proposition**: Comprehensive API testing with flexible reporting, rich assertions, and production-grade logging - test REST APIs efficiently with full observability when needed.
