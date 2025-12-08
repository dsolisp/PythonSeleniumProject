# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.27-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.49-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-8.x-orange.svg)](https://pytest.org)
[![Tests](https://img.shields.io/badge/Tests-263-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Enterprise-grade test automation portfolio demonstrating modern QA engineering** 🚀

---

## 📚 Learning Resources

| Resource | Description |
|----------|-------------|
| 📖 **[Zero-to-Hero Tutorial](documentation/ZERO_TO_HERO_TUTORIAL.md)** | Complete guide to building this framework from scratch |
| 📋 **[Cheat Sheet](documentation/PYTHON_AUTOMATION_CHEAT_SHEET.md)** | Quick reference for pytest, Selenium, Playwright commands |
| 📑 **[Full Documentation](documentation/INDEX.md)** | All documentation in one place |

---

## 🎯 What Makes This Project Special

| Feature | Why It Matters |
|---------|----------------|
| **Dual Framework Support** | Selenium AND Playwright - shows versatility |
| **Real CI/CD Integration** | 607-line GitHub Actions workflow with matrix testing |
| **Flaky Test Detection** | pytest-history tracks test reliability over time |
| **Visual Regression Testing** | Multiple approaches (pixelmatch, playwright-visual) |
| **Performance Monitoring** | Real-time metrics with psutil + load testing with Locust |
| **Self-Healing Tests** | Smart error recovery with retry logic |
| **Clean Architecture** | Page Object Model, modular utilities, clear docstrings |

### Project Metrics
- **~10,000 lines** of production-quality Python
- **263 tests** (205 unit + 58 integration/web/api/performance)
- **Simple, readable code** with clear docstrings over complex type hints
- **Zero linter warnings** (ruff/bandit compliant)

## 📋 Prerequisites

- **Python 3.9+** (tested with 3.9.6, 3.13)
- **Git** for version control
- **Modern web browsers** (Chrome, Firefox, Edge, Safari)
- **4GB+ RAM** recommended for full test suite
- **Internet connection** for browser driver downloads

## ⚡ Quick Start

```bash
# One-command setup and full QA pipeline
./setup_env.sh && python run_full_workflow.py
```

That's it! Runs tests, generates reports, and checks for flaky tests automatically.

## ✨ Key Features

### 🧪 Testing Capabilities
- **Web Automation**: Selenium + Playwright with Page Object Model
- **API Testing**: REST validation with conditional Allure reporting
- **Visual Regression**: Multiple approaches (pytest-playwright-visual, pixelmatch, Applitools)
- **Cross-Browser**: Chrome, Firefox, Edge, Safari support
- **Database Testing**: SQLite integration with test data management
- **Security Testing**: SSL verification and security-focused test markers
- **Load Testing**: Locust integration for performance under load

### 📊 Intelligence & Analytics
- **Statistical Analysis**: Flaky test detection and reliability scoring
- **Advanced Analytics**: Pandas-powered test result analysis
- **Smart Reporting**: HTML dashboards, CSV exports, Allure integration
- **Benchmarking**: pytest-benchmark integration for performance tracking

### 🔧 Enterprise Features
- **Self-Healing**: Automatic retry with intelligent error recovery
- **Performance Monitoring**: Real-time metrics and load testing
- **Data Management**: Multi-format support (JSON/YAML/CSV)
- **Parallel Execution**: pytest-xdist support for faster test runs
- **Code Quality**: Integrated ruff, mypy, bandit, and safety tools

## 🏗️ Project Structure

```
PythonSeleniumProject/
├── 🐍 run_full_workflow.py          # 🚀 Complete QA automation pipeline
├── 🐚 setup_env.sh                  # ⚙️ Auto environment setup
├── 📁 documentation/                # 📚 Feature tutorials & guides
│   ├── INDEX.md                     # Complete documentation index
│   ├── LOCAL_DEV_GUIDE.md           # Development tools guide
│   ├── PYTEST_README.md             # Pytest configuration guide
│   ├── ANALYTICS_AND_REPORTING.md   # Test analytics & reporting
│   ├── TEST_ANALYTICS.md            # Flaky detection & reliability scoring
│   ├── API_TESTING.md               # REST API automation
│   ├── PLAYWRIGHT_INTEGRATION.md    # Modern browser automation
│   ├── TEST_DATA_MANAGEMENT.md      # Data management & export
│   ├── ERROR_RECOVERY_AND_MONITORING.md  # Self-healing & monitoring
│   ├── PERFORMANCE_MONITORING.md    # Load testing & benchmarking
│   └── RECOMMENDATIONS.md           # Framework usage patterns
├── 📁 tests/                        # 🧪 260+ tests across categories
│   ├── unit/                        # 211 fast, isolated unit tests
│   ├── integration/                 # End-to-end & visual regression tests
│   ├── api/                         # REST API validation tests
│   ├── web/                         # UI automation tests (Selenium/Playwright)
│   └── performance/                 # Load & performance benchmarking
├── 📁 pages/                        # 📄 Page Object Model implementations
│   ├── base_page.py                 # Base page with common functionality
│   ├── search_engine_page.py        # Search engine page objects
│   ├── playwright_search_engine_page.py  # Playwright-specific pages
│   └── playwright_base_page.py      # Playwright base page
├── 📁 utils/                        # 🔧 Core framework utilities (~2,500 lines)
│   ├── error_handler.py             # Self-healing error recovery (487 lines)
│   ├── performance_monitor.py       # Real-time performance tracking (457 lines)
│   ├── webdriver_factory.py         # Selenium driver management (297 lines)
│   ├── test_data_manager.py         # Multi-format data loading (285 lines)
│   ├── playwright_factory.py        # Playwright browser management (282 lines)
│   ├── structured_logger.py         # JSON structured logging (266 lines)
│   └── sql_connection.py            # SQLite utilities (165 lines)
├── 📁 config/                       # ⚙️ Environment configurations
│   ├── settings.py                  # Core configuration management
│   ├── local.yaml                   # Local development settings
│   ├── ci.yaml                      # CI/CD environment settings
│   └── capabilities.json            # Browser capabilities
├── 📁 locators/                     # 🎯 Element locators & selectors
│   ├── search_engine_locators.py    # Search page locators
│   ├── playwright_search_engine_locators.py  # Playwright locators
│   ├── result_page_locators.py      # Results page locators
│   └── test_framework_locators.py   # Framework-specific locators
├── 📁 scripts/                      # 🛠️ Automation & utility scripts
│   ├── run_ci_checks.sh             # Code quality validation
│   ├── run_ci_checks_legacy.sh      # Legacy quality checks
│   └── normalize_results.py         # Data processing utilities
├── 📁 data/                         # 💾 Test data & results storage
│   ├── configs/                     # Environment-specific configs
│   └── results/                     # Test execution data for archiving
│       ├── local/                   # Local environment results
│       ├── staging/                 # Staging environment results
│       └── production/              # Production environment results
├── 📁 reports/                      # 📊 Generated test reports
│   ├── html/                        # HTML test reports
│   ├── json/                        # JSON test data
│   ├── allure-results/              # Allure reporting data
│   ├── analytics/                   # ML analytics & trends
│   ├── trends/                      # Performance trend analysis
│   └── coverage_html/               # Code coverage reports
├── 📁 screenshots/                  # 📸 Visual testing artifacts
│   ├── visual-baselines/            # Baseline screenshots
│   └── [test-screenshots]/          # Test execution screenshots
├── 📁 screenshots_diff/             # 🔍 Visual comparison differences
├── 📁 logs/                         # 📝 Test execution logs
├── 📁 drivers/                      # 🚗 WebDriver executables
├── 📁 downloads/                    # 📥 Downloaded test artifacts
├── 📁 examples/                     # 💡 Usage examples & demos
├── 📁 resources/                    # 📦 Test resources & fixtures
└── 📁 test_reports/                 # 📋 Legacy test report storage
```

## 🧪 Running Tests

### Unified Workflow (Recommended)
```bash
python run_full_workflow.py  # Complete pipeline: tests + analytics + ML
```

### Manual Execution
```bash
# Clean development runs (minimal output)
pytest tests/
pytest tests/web/test_playwright_search_engine.py::test_playwright_search_basic

# Full reporting for CI/CD (detailed output)
pytest -c pytest-ci.ini tests/ --cov-report=html

# With Allure reporting
pytest -c pytest-ci.ini tests/ --alluredir=reports/allure-results
allure serve reports/allure-results

# Visual regression testing
pytest tests/integration/test_playwright_visual_pytest_plugin.py -v
pytest tests/integration/test_image_diff.py -v

# Load testing
locust -f tests/performance/locustfile.py

# Benchmarking
pytest tests/performance/ --benchmark-only

# Parallel execution (4 workers)
pytest tests/ -n 4 --dist=loadfile

# Security-focused tests
pytest -m security tests/

# Database tests
pytest -m database tests/
```

**Note**: Default pytest runs are now clean and minimal. Use `pytest-ci.ini` for detailed reporting with coverage, HTML reports, etc.

## 📚 Documentation

| Feature | Tutorial | Description |
|---------|----------|-------------|
| **Local Development** | [🛠️ Local Dev Guide](documentation/LOCAL_DEV_GUIDE.md) | Development tools & local setup |
| **Pytest Configuration** | [🧪 Pytest Guide](documentation/PYTEST_README.md) | Testing framework setup & options |
| **Analytics** | [📊 Analytics Guide](documentation/ANALYTICS_AND_REPORTING.md) | Pandas analytics & dashboards |
| **Test Analytics** | [📈 Analytics Engine](documentation/TEST_ANALYTICS.md) | Flaky detection & reliability scoring |
| **API Testing** | [🔗 API Guide](documentation/API_TESTING.md) | REST automation with Allure |
| **Playwright** | [🎭 Playwright Guide](documentation/PLAYWRIGHT_INTEGRATION.md) | Modern browser automation |
| **Performance** | [⚡ Performance Guide](documentation/PERFORMANCE_MONITORING.md) | Load testing & benchmarking |
| **Error Recovery** | [🔄 Recovery Guide](documentation/ERROR_RECOVERY_AND_MONITORING.md) | Self-healing & monitoring |
| **Data Management** | [💾 Data Guide](documentation/TEST_DATA_MANAGEMENT.md) | Test data & configurations |
| **Recommendations** | [💡 Best Practices](documentation/RECOMMENDATIONS.md) | Framework usage patterns |
| **All Docs** | [📖 Index](documentation/INDEX.md) | Complete documentation |

## 🛠️ Automation Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| **Full Pipeline** | Complete QA workflow | `python run_full_workflow.py` |
| **Environment Setup** | Auto-setup venv & deps | `./setup_env.sh` |
| **Result Normalization** | Data processing | `python scripts/normalize_results.py` |
| **Quality Checks** | Code validation | `bash scripts/run_ci_checks.sh` |
| **Test Runner** | Custom test execution | `python run_tests.py` |

## 🏆 Framework Stats

- ✅ **263 Tests** across all categories (unit, integration, performance)
- ✅ **7 Major Features** fully integrated (web, API, visual, analytics, performance)
- ✅ **22 Package Dependencies** (streamlined from 34, all actively used)
- ✅ **Multiple Test Types** (smoke, regression, visual, security, database)
- ✅ **Production-Ready** enterprise capabilities
- ✅ **Statistical Analytics** for flaky test detection and reliability scoring
- ✅ **Parallel Execution** support for faster testing
- ✅ **Code Quality** integrated (ruff, mypy, bandit)

## 🚀 CI/CD Integration

```yaml
# .github/workflows/test.yml
name: QA Automation
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./setup_env.sh
      - run: python run_full_workflow.py
      - uses: actions/upload-artifact@v3
        with:
          name: reports
          path: reports/
```

## 💡 Best Practices

1. **Use the unified workflow** - `python run_full_workflow.py` for complete automation
2. **Check the tutorials** - See `documentation/` for feature guides  
3. **Run quality checks** - Use `bash scripts/run_ci_checks.sh` before committing
4. **Monitor analytics** - Review ML predictions and performance trends
5. **Use appropriate test markers** - Leverage pytest markers for targeted test runs
6. **Enable parallel execution** - Use `pytest -n 4` for faster test runs in CI/CD
7. **Configure environments** - Use `config/local.yaml` for local development

## 🐛 Troubleshooting

### Common Issues & Solutions

**❌ Import Errors**
```bash
# Ensure virtual environment is activated
source venv-enhanced/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

**❌ Browser Driver Issues**
```bash
# Install Playwright browsers
playwright install

# Update Selenium drivers
webdriver-manager update
```

**❌ Visual Regression Setup**
```bash
# Install visual testing dependencies
pip install pixelmatch pytest-playwright-visual

# Set up baseline screenshots
pytest tests/integration/test_playwright_visual_pytest_plugin.py --snapshot-update
```

**❌ Allure Reporting Issues**
```bash
# Install Allure CLI (macOS)
brew install allure

# Generate and serve report
allure serve reports/allure-results
```

**❌ Performance Testing**
```bash
# Install Locust for load testing
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py
```

**❌ Code Quality Checks**
```bash
# Run all quality checks
bash scripts/run_ci_checks.sh

# Format code
ruff format .

# Check types
mypy .
```

### Environment-Specific Issues

**Local Development**: Use `config/local.yaml` for relaxed timeouts and debug logging
**CI/CD Environment**: Use `config/ci.yaml` for headless browsers and parallel execution
**Performance Issues**: Check system resources - framework requires 4GB+ RAM for full suite

## 🤝 Contributing

1. Fork the repository
2. Run quality checks: `bash scripts/run_ci_checks.sh`
3. Make changes and test: `python run_full_workflow.py`
4. Follow the established patterns (Page Object Model, hamcrest assertions, etc.)
5. Update documentation if adding new features
6. Submit a pull request

### Development Workflow
```bash
# Set up development environment
./setup_env.sh

# Run tests in watch mode during development
pytest tests/unit/ -v --tb=short

# Check code quality
ruff check . && mypy .

# Run full pipeline before committing
python run_full_workflow.py
```

---

**Ready to automate your testing?** Start with `python run_full_workflow.py` 🚀

**Need help?** Check [documentation/INDEX.md](documentation/INDEX.md) for detailed guides.
