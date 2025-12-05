# Historical Test Tracking & Flaky Test Detection

## Overview

The framework uses **pytest-history** to automatically track test results across multiple runs and detect flaky tests. This is a zero-configuration solution that stores results in a SQLite database.

## 🎯 When to Use

- **Detecting flaky tests**: Find tests that sometimes pass, sometimes fail
- **Historical analysis**: Track test reliability over time
- **CI/CD optimization**: Identify unreliable tests causing pipeline failures
- **Quality monitoring**: Build confidence in your test suite

## 🔧 How It Works

1. **Automatic tracking**: Every pytest run automatically stores results in `.test-results.db`
2. **No configuration needed**: Just run pytest normally
3. **Built-in CLI**: Use `pytest-history` commands to analyze results
4. **SQLite storage**: Query directly with any SQLite client if needed

## 📊 Key Features

### 1. Automatic Test History

Every test run is automatically recorded:

```bash
# Just run tests normally - history is tracked automatically
pytest tests/unit/
pytest tests/integration/
python run_tests.py --type all
```

### 2. Flaky Test Detection

Identify tests with inconsistent pass/fail behavior:

```bash
# List all flaky tests
pytest-history flakes

# Example output:
# tests/web/test_search.py::test_search_results - flaky (passed: 7, failed: 3)
# tests/api/test_api.py::test_network_call - flaky (passed: 5, failed: 2)
```

### 3. Historical Run Analysis

View past test runs and their results:

```bash
# List all recorded test runs
pytest-history list runs

# Example output:
# 1 2025-12-04 10:26:05.262201
# 2 2025-12-04 10:26:33.421358
# 3 2025-12-04 10:27:14.076058

# View results for a specific run
pytest-history list results 3
```

## 🚀 Usage

### Basic Commands

```bash
# Run tests (history tracked automatically)
pytest tests/

# View flaky tests
pytest-history flakes

# View all test runs
pytest-history list runs

# View results for run #5
pytest-history list results 5
```

### Using run_tests.py

```bash
# Run tests with flaky analysis
python run_tests.py --type unit --flaky

# Output includes:
# ============================================================
# 🔍 FLAKY TEST ANALYSIS (pytest-history)
# ============================================================
# tests/web/test_search.py::test_flaky_example - flaky (passed: 3, failed: 2)
```

### Custom Database Location

```bash
# Use environment variable
export PYTEST_HISTORY_DB=/path/to/custom.db
pytest tests/

# Or command line
pytest --history-db /path/to/custom.db tests/

# Analyze with custom DB
pytest-history --db /path/to/custom.db flakes
```

## 📈 CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Tests
  run: pytest tests/ -v

- name: Check for Flaky Tests
  run: |
    echo "## Flaky Test Report" >> $GITHUB_STEP_SUMMARY
    pytest-history flakes >> $GITHUB_STEP_SUMMARY || echo "No flaky tests detected" >> $GITHUB_STEP_SUMMARY

- name: Upload Test History
  uses: actions/upload-artifact@v3
  with:
    name: test-history
    path: .test-results.db
```

### Persisting History Across Runs

To track flaky tests across CI runs, persist the database:

```yaml
- name: Download Previous History
  uses: actions/download-artifact@v3
  with:
    name: test-history
  continue-on-error: true

- name: Run Tests
  run: pytest tests/

- name: Upload Updated History
  uses: actions/upload-artifact@v3
  with:
    name: test-history
    path: .test-results.db
```

## 🔍 Advanced: Direct SQLite Queries

The `.test-results.db` is a standard SQLite database. Query it directly for custom analysis:

```bash
# Open with sqlite3
sqlite3 .test-results.db

# View tables
.tables

# Find tests that flip between pass/fail
SELECT t1.testcase, t1.outcome, t2.outcome
FROM "test.results" t1
JOIN "test.results" t2 ON t1.testcase = t2.testcase
  AND t1.test_run = 1 AND t2.test_run = 2
WHERE (t1.outcome = 'passed' AND t2.outcome = 'failed')
   OR (t1.outcome = 'failed' AND t2.outcome = 'passed');
```

## 📁 File Locations

| File | Purpose |
|------|---------|
| `.test-results.db` | SQLite database with test history (auto-created) |
| `pytest.ini` | Configuration comments for pytest-history |
| `run_tests.py` | `--flaky` flag for flaky test summary |

## ⚠️ Notes

- **Minimum runs needed**: Flaky detection works best with 3+ runs per test
- **Database grows**: Consider archiving old history periodically
- **gitignore**: `.test-results.db` is in `.gitignore` (local history only)

## 💡 Best Practices

1. **Run tests regularly**: More runs = better flaky detection
2. **Check flakes before merging**: Run `pytest-history flakes` in CI
3. **Fix flaky tests first**: They erode confidence in the test suite
4. **Persist in CI**: Upload/download the DB artifact for cross-run analysis

## 📚 Related Documentation

- [Pytest Configuration](PYTEST_README.md) - pytest.ini settings
- [Test Data Management](TEST_DATA_MANAGEMENT.md) - Data-driven testing
- [Analytics & Reporting](ANALYTICS_AND_REPORTING.md) - Report generation

## 🔗 External Resources

- **pytest-history PyPI**: https://pypi.org/project/pytest-history/
- **pytest-history GitHub**: https://github.com/Nicoretti/one-piece/tree/grand-line/python/pytest-history

---

**Value Proposition**: Zero-configuration flaky test detection using pytest-history. Just run your tests and let the plugin track history automatically.
