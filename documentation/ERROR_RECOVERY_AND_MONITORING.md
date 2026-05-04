# Error Recovery

## Unified Workflow

> **Recommended:** Use the integrated workflow script for error recovery:
>
> ```bash
> python run_full_workflow.py
> ```
>
> This script runs all tests and applies error recovery strategies automatically.

## Overview

Error recovery is automated as part of the unified workflow. The framework uses a **stdlib-based retry mechanism** with exponential backoff—zero external dependencies.

## 🎯 When to Use

- **Flaky tests**: Automatic retry for unstable elements
- **Network issues**: Handle transient failures gracefully
- **Production reliability**: Self-healing test execution

## 🔧 Key Components

### SmartErrorHandler (`utils/error_handler.py`)

**Purpose**: Clean error formatting and retry logic

**Features**:
- Exponential backoff with configurable delays
- Exception-specific retry control
- Clean, human-readable error output
- Screenshot capture on failure

## 🔄 Retry Mechanisms (stdlib)

### Basic Retry

```python
from utils.error_handler import SmartErrorHandler

handler = SmartErrorHandler()

# Execute with retry
def unstable_operation():
    return driver.find_element(By.ID, "dynamic-element")

result = handler.execute_with_retry(
    unstable_operation,
    max_attempts=3,
    initial_delay=1.0  # exponential: 1s, 2s, 4s...
)
```

### Retry for Specific Exceptions

```python
from selenium.common.exceptions import StaleElementReferenceException

handler = SmartErrorHandler()

result = handler.execute_with_retry(
    click_element,
    max_attempts=5,
    retry_exceptions=(StaleElementReferenceException,),
    initial_delay=0.5
)
```

### How It Works

The retry mechanism uses exponential backoff:

1. **Attempt 1**: Execute immediately
2. **Attempt 2**: Wait 1s, then execute
3. **Attempt 3**: Wait 2s, then execute
4. **Attempt 4**: Wait 4s, then execute
5. Maximum delay capped at 10 seconds

```python
# Implementation (stdlib only, no external deps)
for attempt in range(max_attempts):
    try:
        return operation(*args, **kwargs)
    except retry_exceptions as e:
        if attempt < max_attempts - 1:
            delay = initial_delay * (2 ** attempt)
            delay = min(delay, 10.0)  # Cap at 10s
            time.sleep(delay)
```

## 🛠️ Recovery Strategies

### Strategy 1: Retry with Handler

**Use case**: Transient failures, timing issues

```python
from utils.error_handler import SmartErrorHandler

handler = SmartErrorHandler()

def click_element():
    element = driver.find_element(By.ID, "button")
    element.click()

# Retry up to 3 times with exponential backoff
handler.execute_with_retry(click_element, max_attempts=3)
```

### Strategy 2: Refresh Page

**Use case**: Stale elements, page state issues

```python
def refresh_and_click(driver, locator):
    """Refresh page and retry."""
    driver.refresh()
    time.sleep(2)
    element = driver.find_element(*locator)
    element.click()

handler.execute_with_retry(
    lambda: refresh_and_click(driver, (By.ID, "button")),
    max_attempts=2
)
```

## 🎯 Real-World Usage

### Example: Robust Element Interaction

```python
from utils.error_handler import SmartErrorHandler
from selenium.common.exceptions import StaleElementReferenceException

handler = SmartErrorHandler()

def click_submit(driver):
    element = driver.find_element(By.ID, "submit-button")
    element.click()

# Retry only on stale element errors
result = handler.execute_with_retry(
    lambda: click_submit(driver),
    max_attempts=3,
    retry_exceptions=(StaleElementReferenceException,)
)
```

### Example 2: Network-Aware API Testing

```python
from utils.error_handler import SmartErrorHandler
import requests

handler = SmartErrorHandler()

def api_call(url):
    """API call that might fail on network issues."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# Retry on connection errors
data = handler.execute_with_retry(
    lambda: api_call("https://api.example.com/data"),
    max_attempts=3,
    retry_exceptions=(
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    )
)
```

## 📈 CI/CD Integration

### GitHub Actions Error Handling

```yaml
# GitHub Actions - Run tests with retry
- name: Run Tests with Retry
  run: |
    python -m pytest tests/ --reruns 2 --reruns-delay 1
```

## ⚙️ Configuration

### Retry Configuration Options

```python
handler.execute_with_retry(
    operation,
    max_attempts=3,          # Maximum retry attempts
    retry_exceptions=None,   # Tuple of exceptions to retry (default: all)
    initial_delay=1.0,       # Initial delay in seconds
)
# Delay doubles each retry: 1s → 2s → 4s (capped at 10s)
```

## 💡 Best Practices

1. **Use exponential backoff**: Prevents overwhelming services
2. **Set maximum attempts**: Avoid infinite retry loops
3. **Log retry attempts**: Track recovery patterns
4. **Specific exceptions**: Only retry recoverable errors
5. **Cleanup on failure**: Release resources after errors

## 📚 Related Documentation

- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Performance benchmarking
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing

## 🔗 File Locations

- **Implementation**: `utils/error_handler.py`
- **Tests**: `tests/unit/test_library_integrations.py`

---

**Value Proposition**: Build self-healing test automation with intelligent retry logic—using only Python stdlib for zero external dependencies.
