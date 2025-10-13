# Pytest Configuration Guide

## Quick Development Runs (Default)
```bash
# Clean, minimal output for development (warnings disabled)
pytest tests/
pytest tests/web/test_playwright_search_engine.py::test_playwright_search_basic
```

## Full Reporting for CI/CD
```bash
# Detailed reports with coverage, HTML, XML, etc. (warnings enabled)
pytest -c pytest-ci.ini tests/
pytest -c pytest-ci.ini --cov-report=html tests/
```

## Common Development Options
```bash
# Run specific test with verbose output
pytest -v tests/web/test_playwright_search_engine.py::test_playwright_search_basic

# Run tests with coverage (one-time)
pytest --cov=pages --cov-report=html tests/

# Run failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "search"

# Stop on first failure
pytest -x
```

## Configuration Files
- `pytest.ini` - Minimal configuration for development (warnings disabled for clean output)
- `pytest-ci.ini` - Full reporting configuration for CI/CD (warnings enabled for debugging)