# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.27-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.49-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-7.x-orange.svg)](https://pytest.org)
[![Tests](https://img.shields.io/badge/Tests-200%2B-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Enterprise-grade test automation portfolio demonstrating modern QA engineering** 🚀

---

## 📚 Learning Resources

| Resource | Description |
|----------|-------------|
| 📖 **[Zero-to-Hero Tutorial](docs/ZERO_TO_HERO.md)** | Complete guide to building this framework from scratch |
| 📋 **[Cheat Sheet](documentation/PYTHON_AUTOMATION_CHEAT_SHEET.md)** | Quick reference for pytest, Selenium, Playwright commands |
| 📑 **[Full Documentation](documentation/INDEX.md)** | All documentation in one place |

---

## 🎯 What Makes This Project Special

| Feature | Why It Matters |
|---------|----------------|
| **Dual Framework Support** | Selenium AND Playwright - shows versatility |
| **Real CI/CD Integration** | GitHub Actions (`.github/workflows/ci.yml`, `full-tests.yml`, `nightly.yml`) |
| **Flaky Test Detection** | pytest-history tracks test reliability over time |
| **Visual Regression Testing** | Selenium screenshots + Pillow + pixelmatch (`utils/diff_handler.py`), baselines in `baselines/` |
| **Load Testing** | Performance testing with Locust |
| **Retries & failures** | `SmartErrorHandler.execute_with_retry` (stdlib backoff) + failure screenshots via `conftest` / settings |
| **Clean Architecture** | Page Object Model, modular utilities, clear docstrings |

### Project metrics (approximate; verify locally)
- **Large Python surface** across `pages/`, `tests/`, and `utils/`
- **200+ tests** across unit, web, API, integration, performance, and markers
- **Readable style** — docstrings and straightforward control flow
- **Quality gates** — `ruff`, `mypy`, `bandit` (see `scripts/run_ci_checks.sh` and CI)

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
- **Visual regression**: Pillow + pixelmatch (`utils/diff_handler.py`); baselines under `baselines/`
- **Cross-Browser**: Chrome, Firefox, Edge, Safari support
- **Database Testing**: SQLite integration with test data management
- **Security Testing**: SSL verification and security-focused test markers
- **Load Testing**: Locust integration for performance under load

### 📊 Intelligence & analytics
- **Flaky history**: `pytest-history` (SQLite `.test-results.db`) — see `documentation/TEST_ANALYTICS.md`
- **Workflow output**: `run_full_workflow.py` writes CSV/JSON under `data/results` and reports under `reports/`
- **Reporting**: Allure (`allure-pytest`), pytest-html, pytest-json-report where configured
- **Benchmarking**: `pytest-benchmark` under `tests/performance/`

### 🔧 Reliability & performance
- **Retries**: stdlib exponential backoff in `utils/error_handler.py` (`execute_with_retry`)
- **Load testing**: Locust (`tests/performance/locustfile.py`)
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
├── 📁 tests/                        # pytest suites (markers in pytest.ini)
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── web/                         # Selenium + Playwright UI tests
│   ├── ui/visual/                   # SauceDemo visual regression (baselines/)
│   ├── backend/                     # e.g. schema / API shape checks
│   └── performance/                 # Locust + pytest-benchmark
├── 📁 pages/                        # 📄 Page Object Model implementations
│   ├── base_page.py                 # Base page with common functionality
│   ├── search_engine_page.py        # Search engine page objects
│   ├── playwright_search_engine_page.py  # Playwright-specific pages
│   └── playwright_base_page.py      # Playwright base page
├── 📁 utils/                        # 🔧 Framework utilities (see each module)
│   ├── webdriver_factory.py         # Selenium driver lifecycle + cleanup
│   ├── playwright_factory.py        # Playwright browser lifecycle
│   ├── error_handler.py             # Clean errors, screenshots, stdlib retries
│   ├── diff_handler.py              # Pillow + pixelmatch image compare
│   ├── otel.py                      # OpenTelemetry wiring used from conftest
│   ├── test_data_manager.py         # JSON/YAML/CSV test data
│   ├── structured_logger.py         # Structured logging helpers
│   └── sql_connection.py            # SQLite helpers
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
│   ├── analytics/                   # Analytics outputs & summaries
│   ├── trends/                      # Performance trend analysis
│   └── coverage_html/               # Code coverage reports
├── 📁 baselines/                    # 📸 Committed visual baselines (SauceDemo UI)
├── 📁 screenshots/                # Actuals, diffs, failure screenshots
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
python run_full_workflow.py  # Complete pipeline: tests + reporting + analytics
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

# Visual regression (Selenium + pixelmatch)
pytest tests/ui/visual/test_visual_regression.py -v

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
| **Analytics** | [📊 Analytics Guide](documentation/ANALYTICS_AND_REPORTING.md) | Reports, exports, and workflow output |
| **Test Analytics** | [📈 Analytics Engine](documentation/TEST_ANALYTICS.md) | Flaky detection & reliability scoring |
| **API Testing** | [🔗 API Guide](documentation/API_TESTING.md) | REST automation with Allure |
| **Playwright** | [🎭 Playwright Guide](documentation/PLAYWRIGHT_INTEGRATION.md) | Modern browser automation |
| **Performance** | [⚡ Performance Guide](documentation/PERFORMANCE_MONITORING.md) | Load testing & benchmarking |
| **Error Recovery** | [🔄 Recovery Guide](documentation/ERROR_RECOVERY_AND_MONITORING.md) | Retries, logging, screenshots (see `utils/error_handler.py`) |
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

## 🏆 What you get in the repo today

- **Layered tests**: unit, web (Selenium + Playwright), API, integration, visual, performance, backend helpers — see `tests/` and `pytest.ini` markers
- **Auth reuse for SauceDemo**: session fixture + `.auth/sauce.json` (see `conftest.py`, ADR-009)
- **Tracing**: OpenTelemetry hooks from `conftest.py` → `utils/otel.py`
- **Parallel runs**: `pytest-xdist` (`pytest -n …`)
- **Quality**: `ruff`, `mypy`, `bandit`, `safety` in CI scripts where enabled

## 🚀 CI/CD Integration

CI is defined under `.github/workflows/` (for example `ci.yml` for PR checks, `full-tests.yml` and `nightly.yml` for broader suites). Open those files for the exact jobs, Python version, and commands.

## 💡 Best Practices

1. **Use the unified workflow** - `python run_full_workflow.py` for complete automation
2. **Check the tutorials** - See `documentation/` for feature guides  
3. **Run quality checks** - Use `bash scripts/run_ci_checks.sh` before committing
4. **Monitor analytics** - Review flaky summaries and performance trends
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

**❌ Visual regression setup**
```bash
# Pixelmatch + Pillow are in requirements.txt — reinstall if needed
pip install -r requirements.txt

# Run visual tests (creates baselines under baselines/ if missing — commit intentionally)
pytest tests/ui/visual/test_visual_regression.py -v
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
