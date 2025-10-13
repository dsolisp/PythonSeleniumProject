# Performance Monitoring and Load Testing

## Overview

Real-time performance monitoring and load testing capabilities powered by **pytest-benchmark**, **Locust**, and custom performance monitors.

## 🎯 When to Use

- **Performance benchmarking**: Measure and track function execution times
- **Load testing**: Simulate concurrent users and API stress
- **Performance regression detection**: Identify slow tests automatically
- **Bottleneck identification**: Find slow operations in test suite
- **Capacity planning**: Understand system limits under load

## 🔧 Key Components

### 1. PerformanceMonitor (`utils/performance_monitor.py`)

**Purpose**: Real-time performance tracking and benchmarking

**Features**:
- Function execution timing
- Performance threshold testing
- WebDriver operation monitoring
- API request performance tracking
- Statistical benchmarking

### 2. Load Testing (Locust)

**Purpose**: Simulate multiple concurrent users for API/UI stress testing

**Features**:
- Concurrent user simulation
- Ramp-up strategies
- Real-time performance metrics
- HTML/CSV reports
- Distributed load testing

## ⚡ Performance Monitoring

### Basic Function Timing

```python
from utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor("LoginTests")

@monitor.timer(name="login_operation")
def perform_login(driver, username, password):
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()

# Execution automatically timed
perform_login(driver, "user", "pass")

# Get metrics
report = monitor.get_performance_report()
print(f"Login took: {report['login_operation']['average_time']:.2f}ms")
```

### Performance Threshold Testing

```python
from utils.performance_monitor import performance_test

@performance_test(threshold_ms=2000, name="page_load_test")
def test_page_load_performance():
    """Test fails if execution exceeds 2000ms."""
    driver.get("https://example.com")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "content"))
    )

# Automatically fails if page load > 2 seconds
```

### WebDriver Operation Monitoring

```python
from utils.performance_monitor import WebPerformance

web_perf = WebPerformance()

# Monitor page load time
load_time = web_perf.monitor_page_load(driver, "https://example.com")
print(f"Page loaded in: {load_time:.2f}ms")

# Monitor element finding
find_time = web_perf.monitor_element_find(
    driver,
    By.ID,
    "submit-button"
)
print(f"Element found in: {find_time:.2f}ms")

# Monitor click action
click_time = web_perf.monitor_element_click(
    driver,
    By.ID,
    "submit-button"
)
print(f"Click completed in: {click_time:.2f}ms")
```

### API Performance Monitoring

```python
from utils.performance_monitor import APIPerformance
import requests

api_perf = APIPerformance()
session = requests.Session()

# Monitor API request
timing_data = api_perf.monitor_api_request(
    session,
    "GET",
    "https://api.example.com/users"
)

print(f"Request time: {timing_data['request_time']:.2f}ms")
print(f"Response time: {timing_data['response_time']:.2f}ms")
print(f"Total time: {timing_data['total_time']:.2f}ms")
```

### Function Benchmarking

```python
from utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor("BenchmarkTests")

def expensive_operation():
    # Some computationally expensive task
    result = sum([i**2 for i in range(10000)])
    return result

# Benchmark function (run 100 times)
stats = monitor.benchmark_function(expensive_operation, iterations=100)

print(f"Mean: {stats['mean']:.2f}ms")
print(f"Median: {stats['median']:.2f}ms")
print(f"Std Dev: {stats['stddev']:.2f}ms")
print(f"Min: {stats['min']:.2f}ms")
print(f"Max: {stats['max']:.2f}ms")
```

## 🏋️ Load Testing with Locust

### Installation

```bash
pip install locust
```

### Basic Load Test Configuration

Create `tests/performance/locustfile.py`:

```python
from locust import HttpUser, task, between

class APILoadTestUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = "https://api.example.com"
    
    @task(3)  # Weight 3 - executed 3x more often
    def test_get_users(self):
        """GET /users endpoint."""
        self.client.get("/users")
    
    @task(2)  # Weight 2
    def test_get_posts(self):
        """GET /posts endpoint."""
        self.client.get("/posts")
    
    @task(1)  # Weight 1 - least common
    def test_create_post(self):
        """POST /posts endpoint."""
        self.client.post("/posts", json={
            "title": "Load Test Post",
            "body": "Testing under load",
            "userId": 1
        })
```

### Running Load Tests

```bash
# Interactive mode (Web UI at http://localhost:8089)
locust -f tests/performance/locustfile.py

# Headless mode (no Web UI)
locust -f tests/performance/locustfile.py \
    --headless \
    --users 50 \
    --spawn-rate 5 \
    --run-time 5m \
    --host https://api.example.com

# Generate HTML report
locust -f tests/performance/locustfile.py \
    --headless \
    --users 25 \
    --spawn-rate 2 \
    --run-time 10m \
    --html load_test_report.html
```

### Advanced Load Test Scenarios

```python
from locust import HttpUser, task, between, SequentialTaskSet

class UserBehavior(SequentialTaskSet):
    """Sequential user workflow."""
    
    @task
    def login(self):
        self.client.post("/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
    
    @task
    def browse_products(self):
        self.client.get("/products")
    
    @task
    def view_product(self):
        self.client.get("/products/1")
    
    @task
    def add_to_cart(self):
        self.client.post("/cart", json={"product_id": 1})
    
    @task
    def checkout(self):
        self.client.post("/checkout")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "https://example.com"
```

## 📊 Pytest-Benchmark Integration

### Basic Benchmarking

```python
import pytest

def test_function_performance(benchmark):
    """Benchmark function execution."""
    
    def function_to_benchmark():
        return sum([i**2 for i in range(1000)])
    
    result = benchmark(function_to_benchmark)
    assert result > 0

# Output:
# ---------------------- benchmark: 1 tests ----------------------
# Name                     Min      Max     Mean    StdDev
# test_function_perf    1.2ms    2.5ms    1.5ms    0.3ms
# ----------------------------------------------------------------
```

### Custom Benchmark Decorator

```python
from utils.performance_monitor import benchmark_decorator

@benchmark_decorator(iterations=50)
def test_search_performance(benchmark):
    """Benchmark search operation."""
    
    def search_operation():
        results = page.search("selenium python")
        return results
    
    results = benchmark(search_operation)
    assert len(results) > 0
```

### Comparison Benchmarks

```python
def test_compare_algorithms(benchmark):
    """Compare different algorithm implementations."""
    
    # Benchmark algorithm 1
    time_algo1 = benchmark(algorithm_1, iterations=100)
    
    # Benchmark algorithm 2  
    time_algo2 = benchmark(algorithm_2, iterations=100)
    
    # Assert algo1 is faster
    assert time_algo1 < time_algo2
```

## 🎯 Real-World Usage

### Example 1: Performance Regression Detection

```python
import pytest
from utils.performance_monitor import PerformanceMonitor

@pytest.fixture
def perf_monitor():
    return PerformanceMonitor("RegressionTests")

def test_login_performance_regression(perf_monitor):
    """Detect if login performance degrades."""
    
    baseline_time = 1.5  # seconds
    threshold = 1.2  # 20% slower than baseline
    
    @perf_monitor.timer(name="login")
    def login():
        page.login("user", "pass")
    
    login()
    
    metrics = perf_monitor.get_performance_report()
    actual_time = metrics['login']['average_time'] / 1000  # Convert to seconds
    
    assert actual_time < baseline_time * threshold, \
        f"Login is {((actual_time / baseline_time) - 1) * 100:.1f}% slower than baseline"
```

### Example 2: API Load Testing

```bash
# Simulate 100 concurrent users
locust -f tests/performance/api_load_test.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 10m \
    --host https://api.staging.example.com \
    --html reports/load_test_$(date +%Y%m%d_%H%M%S).html

# Monitor for errors and response times
# Fails if error rate > 5% or p95 response time > 1000ms
```

### Example 3: CI/CD Performance Gates

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Performance Tests
        run: |
          pytest tests/performance/ \
            --benchmark-only \
            --benchmark-min-rounds=10
      
      - name: Check Performance Thresholds
        run: |
          python scripts/check_performance_thresholds.py \
            --max-avg-time 2000 \
            --max-p95-time 5000
      
      - name: Run Load Test
        run: |
          locust -f tests/performance/locustfile.py \
            --headless \
            --users 50 \
            --spawn-rate 5 \
            --run-time 3m \
            --html reports/load_test.html
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: performance-reports
          path: reports/
```

### Example 4: Performance Monitoring Dashboard

```python
from utils.performance_monitor import PerformanceMonitor
import matplotlib.pyplot as plt

monitor = PerformanceMonitor("SuitePerformance")

# Run tests with monitoring
test_results = []
for test in test_suite:
    with monitor.timer(test.name):
        test.execute()
    
    metrics = monitor.get_metrics(test.name)
    test_results.append({
        'name': test.name,
        'duration': metrics['average_time']
    })

# Generate performance chart
names = [r['name'] for r in test_results]
durations = [r['duration'] for r in test_results]

plt.figure(figsize=(10, 6))
plt.bar(names, durations)
plt.xlabel('Test Name')
plt.ylabel('Duration (ms)')
plt.title('Test Performance Dashboard')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/performance_dashboard.png')
```

## 📈 Performance Metrics

### Key Metrics Tracked

- **Response Time**: Time from request to response
- **Throughput**: Requests per second
- **Error Rate**: Percentage of failed requests
- **Percentiles**: P50, P95, P99 response times
- **Resource Usage**: CPU, memory during execution
- **Concurrent Users**: Maximum supported load

### Locust Metrics

```python
# After load test completes, Locust provides:
{
    "total_rps": 45.2,              # Requests per second
    "total_fail_per_sec": 0.1,      # Failures per second
    "response_time_percentile_50": 230,   # P50 (median)
    "response_time_percentile_95": 890,   # P95
    "response_time_percentile_99": 1450,  # P99
    "num_requests": 27150,
    "num_failures": 35
}
```

## 💡 Best Practices

1. **Set baselines**: Establish performance baselines before optimizing
2. **Use percentiles**: P95/P99 more meaningful than averages
3. **Test under load**: Performance issues appear under stress
4. **Monitor trends**: Track performance over time
5. **Test early**: Catch regressions before production
6. **Real scenarios**: Load test realistic user behavior
7. **Resource limits**: Know your infrastructure capacity

## 📚 Related Documentation

- [Error Recovery & Monitoring](ERROR_RECOVERY_AND_MONITORING.md) - System resource monitoring
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Performance data analysis
- [API Testing](API_TESTING.md) - API performance testing

## 🔗 File Locations

- **Implementation**: `utils/performance_monitor.py`
- **Load Tests**: `tests/performance/locustfile.py`
- **Benchmark Tests**: `tests/performance/test_performance_monitoring.py`
- **Reports**: `reports/performance/`, `reports/load_tests/`

---

**Value Proposition**: Comprehensive performance monitoring and load testing - catch performance regressions early, understand system limits, and ensure applications perform under real-world conditions.
