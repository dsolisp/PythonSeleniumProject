# Changelog

All notable changes to the Python Selenium Test Automation Framework.

## [2.1.0] - 2025-12-04

### 🔄 Flaky Test Detection Overhaul

This release replaces the custom test analytics implementation with `pytest-history` for simpler, zero-configuration flaky test detection.

### Removed
- **utils/test_analytics.py** - Replaced with pytest-history plugin
- Custom pandas-based statistical analysis for flaky detection
- ML analysis references throughout documentation

### Added
- **pytest-history>=0.3.0** - Automatic test history tracking
- `--flaky` flag to `run_tests.py` for flaky test summary
- `.test-results.db` SQLite database for test history (auto-created)

### Changed
- **run_tests.py** - Added `--flaky` argument for pytest-history integration
- **run_full_workflow.py** - Uses pytest-history instead of custom analytics
- **pytest.ini** - Added pytest-history configuration comments
- **requirements.txt** - Updated pytest to >=8.0.0, added pytest-history

### Documentation Updated
- **TEST_ANALYTICS.md** - Complete rewrite for pytest-history
- **ANALYTICS_AND_REPORTING.md** - Updated for new approach
- **INDEX.md** - Removed old references, added new commands
- **TEST_DATA_MANAGEMENT.md** - Removed ML analysis references
- **TUTORIAL.md** - Updated flaky detection section
- **README.md** - Updated project structure

### How to Use
```bash
# Run tests (history tracked automatically)
pytest tests/

# View flaky tests
pytest-history flakes

# View test run history
pytest-history list runs

# Use via run_tests.py
python run_tests.py --type unit --flaky
```

---

## [2.0.0] - 2025-11-30

### 🎯 Major Refactoring Release

This release focuses on reducing code bloat while maintaining portfolio showcase value.

### Removed
- **scikit-learn dependency** - Replaced ML-based analysis with pure statistical methods
- Removed duplicate methods across page objects
- Cleaned up redundant utility functions

### Changed

#### utils/ml_test_analyzer.py (663 → 243 lines, -63%)
- Replaced sklearn RandomForestClassifier with pandas/numpy statistical analysis
- Still provides: flaky test detection, slow test identification, reliability scoring
- Removed: ML failure prediction (replaced with statistical risk scoring)
- Removed: Feature importance analysis

#### utils/sql_connection.py (602 → 126 lines, -79%)
- Consolidated redundant query functions
- Simplified to essential CRUD operations
- Maintained SQL injection prevention
- Added backward compatibility aliases

#### utils/structured_logger.py (442 → 110 lines, -75%)
- Streamlined JSON structured logging
- Removed verbose domain-specific methods
- Kept core logging levels + test lifecycle methods

#### tests/unit/test_sql_*.py (583 → 183 lines, -69%)
- Replaced excessive mocking with real in-memory SQLite tests
- More maintainable and readable test code

### Improved
- **Test execution**: 212 unit tests, all passing
- **Linter compliance**: Zero ruff errors
- **Type hints**: Updated to use `Optional[]` properly

### Metrics

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| ml_test_analyzer.py | 663 lines | 243 lines | 63% |
| sql_connection.py | 602 lines | 126 lines | 79% |
| structured_logger.py | 442 lines | 110 lines | 75% |
| SQL test files | 583 lines | 183 lines | 69% |
| **Total refactored** | **2,290 lines** | **662 lines** | **71%** |

---

## [1.5.0] - Previous

### Added
- Playwright integration with visual testing
- Locust load testing support
- Allure reporting integration
- ML-powered test analysis (now simplified in 2.0.0)

### Features
- Page Object Model for Selenium and Playwright
- Multi-format test data management (JSON/YAML/CSV)
- Performance monitoring with psutil
- Smart error recovery with retry logic

---

## Architecture Overview

### Current Project Structure (Post-Refactoring)

```
Total Python Lines: ~12,552

pages/           1,624 lines  (Page Object Model)
  base_page.py         559    Essential - Selenium base
  playwright_*.py      587    Essential - Playwright pages
  search_engine_*.py   683    Essential - Demo pages

utils/           2,600 lines  (Framework Utilities)
  error_handler.py     506    Essential - Smart recovery
  test_reporter.py     491    Essential - Pandas analytics
  performance_*.py     453    Essential - Monitoring
  webdriver_factory.py 312    Essential - Driver management
  playwright_factory.py 280   Essential - Browser management
  test_data_manager.py 280    Valuable - Data loading
  ml_test_analyzer.py  243    Valuable - Statistical analysis
  logger.py            142    Consider consolidating
  sql_connection.py    126    Valuable - Database utils
  structured_logger.py 110    Valuable - JSON logging
  diff_handler.py       16    Used by tests

tests/           6,043 lines  (Test Suite)
  unit/          2,698    Fast isolated tests
  web/           1,258    UI automation
  integration/     870    End-to-end tests
  api/             543    REST validation
  performance/     674    Load/benchmark

locators/          249 lines  (Element Selectors)
config/            125 lines  (Settings)
```

### Test Statistics
- **270 tests** collected
- **212 unit tests** passing
- **58 integration/web/api/performance tests**

### Dependencies
- Core: selenium, playwright, pytest
- Analytics: pandas, numpy
- Reporting: allure-pytest, pytest-html
- Performance: locust, pytest-benchmark
- Quality: ruff, mypy, bandit

