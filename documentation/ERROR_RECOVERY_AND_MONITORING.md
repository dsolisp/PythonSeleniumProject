# Error Recovery and System Monitoring

## Unified Workflow

> **Recommended:** Use the integrated workflow script for all error recovery and monitoring. All error handling, retries, and system monitoring are now automatically triggered by running:
>
> ```bash
> python run_full_workflow.py
> ```
>
> This script runs all tests, applies error recovery strategies, and monitors system resources—no manual steps required.

## Overview

Error recovery and system monitoring are now fully automated as part of the unified workflow. The framework uses **Tenacity** (retry mechanisms) and **Psutil** (system monitoring) to ensure reliability, all orchestrated by `run_full_workflow.py`.

## 🎯 When to Use

- **After running the workflow script**: All error recovery and monitoring are applied automatically
- **Flaky tests**: Automatic retry for unstable elements
- **Network issues**: Handle transient failures gracefully
- **Performance monitoring**: Track memory/CPU during execution
- **Resource management**: Detect resource exhaustion
- **Production reliability**: Self-healing test execution

## 🔧 Key Components (Automated)

### 1. SmartErrorHandler (`utils/error_handler.py`)

**Purpose**: Intelligent error classification and automatic recovery

**Features**:
- Exception-specific retry strategies
- Exponential backoff with configurable delays
- System resource monitoring
- Recovery success tracking
- Multiple recovery strategies (retry/refresh/restart)

## 🔄 Retry Mechanisms (Tenacity)

### Basic Retry

```python
from utils.error_handler import SmartErrorHandler

handler = SmartErrorHandler()

# Execute with retry
def unstable_operation():
    return driver.find_element(By.ID, "dynamic-element")

result = handler.execute_with_tenacity_retry(
    unstable_operation,
    max_attempts=3,
    wait_strategy="exponential"
)
```

### Advanced Retry Configuration

```python
from tenacity import (
    Retrying,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

# Retry only for specific exceptions
retry_strategy = Retrying(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(ElementNotInteractableException),
    reraise=True
)

for attempt in retry_strategy:
    with attempt:
        element.click()  # Will retry on ElementNotInteractableException
```

### Decorator Pattern

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def flaky_api_call():
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()

# Automatically retries up to 3 times with 2-second wait
data = flaky_api_call()
```

## 📊 System Monitoring (Psutil)

### Memory Monitoring

```python
from utils.error_handler import SmartErrorHandler

handler = SmartErrorHandler()

# Real-time memory usage
memory_data = handler.monitor_memory_usage()

print(f"Current memory: {memory_data['current_memory_mb']} MB")
print(f"Peak memory: {memory_data['peak_memory_mb']} MB")
print(f"Available memory: {memory_data['available_memory_mb']} MB")
print(f"Memory percent: {memory_data['memory_percent']}%")
print(f"CPU percent: {memory_data['cpu_percent']}%")
```

### Performance Tracking During Tests

```python
import psutil

# Before test execution
process = psutil.Process()
memory_before = process.memory_info().rss / 1024 / 1024  # MB
cpu_before = psutil.cpu_percent(interval=1)

# Run test
execute_test()

# After test execution
memory_after = process.memory_info().rss / 1024 / 1024
cpu_after = psutil.cpu_percent(interval=1)

print(f"Memory used: {memory_after - memory_before:.2f} MB")
print(f"CPU usage: {cpu_after:.1f}%")
```

### System Health Check

```python
import psutil

# System specifications
total_memory = psutil.virtual_memory().total / (1024**3)  # GB
cpu_count = psutil.cpu_count()
disk_usage = psutil.disk_usage('/').percent

print(f"System: {cpu_count} CPUs, {total_memory:.1f} GB RAM")
print(f"Disk usage: {disk_usage}%")

# Resource availability check
if psutil.virtual_memory().percent > 90:
    print("⚠️ Warning: Low memory available")
if psutil.cpu_percent(interval=1) > 80:
    print("⚠️ Warning: High CPU usage")
```

## 🛠️ Recovery Strategies

### Strategy 1: Retry Action

**Use case**: Transient failures, timing issues

```python
def retry_strategy(driver, element, error):
    """Retry the same action up to 3 times."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            time.sleep(1)  # Brief wait
            element.click()
            return True
        except Exception:
            if attempt == max_retries - 1:
                return False
    return False
```

### Strategy 2: Refresh Page

**Use case**: Stale elements, page state issues

```python
def refresh_strategy(driver, element, error):
    """Refresh page and retry."""
    driver.refresh()
    time.sleep(2)
    try:
        element = driver.find_element(*locator)
        element.click()
        return True
    except Exception:
        return False
```

### Strategy 3: Restart Browser

**Use case**: Browser crashes, memory leaks

```python
def restart_strategy(driver, element, error):
    """Restart browser and retry."""
    driver.quit()
    driver = webdriver.Chrome()
    driver.get(original_url)
    time.sleep(3)
    try:
        element = driver.find_element(*locator)
        element.click()
        return True
    except Exception:
        return False
```

## 🎯 Real-World Usage

### Example 1: Robust Element Interaction

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def click_with_retry(driver, locator):
    """Click element with automatic retry on failure."""
    element = driver.find_element(*locator)
    element.click()

# Usage
try:
    click_with_retry(driver, (By.ID, "submit-button"))
except Exception as e:
    print(f"Failed after retries: {e}")
```

### Example 2: Memory-Aware Test Execution

```python
import psutil

def test_with_memory_monitoring():
    """Test with automatic memory monitoring."""
    initial_memory = psutil.virtual_memory().percent
    
    # Execute test
    perform_heavy_operation()
    
    # Check memory usage
    current_memory = psutil.virtual_memory().percent
    memory_increase = current_memory - initial_memory
    
    if memory_increase > 20:
        print(f"⚠️ High memory usage: +{memory_increase}%")
        
    # Cleanup if needed
    if psutil.virtual_memory().percent > 85:
        cleanup_resources()
```

### Example 3: Network-Aware API Testing

```python
from tenacity import retry, stop_after_delay, retry_if_exception_type
import requests

@retry(
    stop=stop_after_delay(30),  # Retry for up to 30 seconds
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout
    ))
)
def api_call_with_network_retry(url):
    """API call with network failure retry."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

# Automatically retries on network errors
data = api_call_with_network_retry("https://api.example.com/data")
```

### Example 4: Resource-Based Test Skipping

```python
import psutil
import pytest

def check_system_resources():
    """Check if system has sufficient resources."""
    memory_available = psutil.virtual_memory().available / (1024**3)  # GB
    cpu_idle = 100 - psutil.cpu_percent(interval=1)
    
    return memory_available > 2 and cpu_idle > 20

@pytest.mark.skipif(
    not check_system_resources(),
    reason="Insufficient system resources"
)
def test_resource_intensive_operation():
    """Test that requires significant resources."""
    perform_heavy_computation()
```

## 📈 Monitoring Integration

### CI/CD Resource Tracking

```yaml
# GitHub Actions - Track resource usage
- name: Monitor Resources
  run: |
    python -c "
    import psutil
    print(f'Memory: {psutil.virtual_memory().percent}%')
    print(f'CPU: {psutil.cpu_percent()}%')
    "

- name: Run Tests with Monitoring
  run: pytest tests/ --verbose
  
- name: Check Resource Usage After Tests
  run: |
    python -c "
    import psutil
    if psutil.virtual_memory().percent > 90:
        print('::warning::High memory usage detected')
    "
```

### Performance Alerts

```python
def monitor_test_performance(test_function):
    """Decorator to monitor and alert on resource usage."""
    def wrapper(*args, **kwargs):
        # Before execution
        memory_before = psutil.virtual_memory().percent
        cpu_before = psutil.cpu_percent(interval=1)
        
        # Execute test
        result = test_function(*args, **kwargs)
        
        # After execution
        memory_after = psutil.virtual_memory().percent
        cpu_after = psutil.cpu_percent(interval=1)
        
        # Alert if thresholds exceeded
        if memory_after - memory_before > 20:
            send_alert(f"High memory usage in {test_function.__name__}")
        if cpu_after > 80:
            send_alert(f"High CPU usage in {test_function.__name__}")
            
        return result
    return wrapper
```

## ⚙️ Configuration

### Tenacity Configuration Options

```python
from tenacity import (
    Retrying,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
    wait_exponential,
    wait_random
)

# Stop conditions
stop_after_attempt(5)           # Stop after 5 attempts
stop_after_delay(30)            # Stop after 30 seconds

# Wait strategies
wait_fixed(2)                   # Wait 2 seconds between attempts
wait_exponential(multiplier=1)  # 1s, 2s, 4s, 8s, ...
wait_random(min=1, max=5)       # Random wait 1-5 seconds
```

### Psutil Monitoring Options

```python
import psutil

# Process-specific monitoring
process = psutil.Process()
process.cpu_percent(interval=1)
process.memory_info()
process.num_threads()

# System-wide monitoring
psutil.virtual_memory()
psutil.cpu_percent(interval=1)
psutil.disk_usage('/')
psutil.net_io_counters()
```

## 💡 Best Practices

1. **Use exponential backoff**: Prevents overwhelming services
2. **Set maximum attempts**: Avoid infinite retry loops
3. **Monitor memory**: Detect leaks early
4. **Log retry attempts**: Track recovery patterns
5. **Specific exceptions**: Only retry recoverable errors
6. **Resource thresholds**: Skip tests when resources low
7. **Cleanup on failure**: Release resources after errors

## 📚 Related Documentation

- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Performance benchmarking
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Execution analytics

## 🔗 File Locations

- **Implementation**: `utils/error_handler.py`
- **Tests**: `tests/unit/test_library_integrations.py` (Tenacity/Psutil tests)

---

**Value Proposition**: Build self-healing, production-grade test automation with intelligent error recovery and comprehensive system monitoring - reducing flaky tests and improving reliability.
