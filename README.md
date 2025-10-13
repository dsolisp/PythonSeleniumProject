# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.16-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-8.4-orange.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Enterprise-grade test automation with ML-powered intelligence** 🚀

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

That's it! Runs tests, analytics, ML predictions, and generates reports automatically.

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
- **ML-Powered**: AI failure prediction and flaky test detection
- **Advanced Analytics**: Pandas-powered statistical analysis
- **Smart Reporting**: HTML dashboards and CSV exports
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
├── 🐍 run_full_workflow.py    # 🚀 Complete QA automation pipeline
├── 🐚 setup_env.sh           # ⚙️ Auto environment setup
├── 📁 documentation/         # 📚 Feature tutorials & guides
├── 📁 tests/                 # 293+ test cases
├── 📁 utils/                 # Framework utilities
├── 📁 scripts/               # Automation scripts
└── 📁 reports/               # Generated reports
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
| **Analytics** | [📊 Analytics Guide](documentation/ANALYTICS_AND_REPORTING.md) | Pandas analytics & dashboards |
| **ML Intelligence** | [🤖 ML Guide](documentation/ML_INTEGRATION.md) | AI-powered test optimization |
| **API Testing** | [🔗 API Guide](documentation/API_TESTING.md) | REST automation with Allure |
| **Playwright** | [🎭 Playwright Guide](documentation/PLAYWRIGHT_INTEGRATION.md) | Modern browser automation |
| **Visual Testing** | [👁️ Visual Guide](documentation/TEST_DATA_MANAGEMENT.md) | Visual regression testing |
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

- ✅ **293+ Tests** across all categories (unit, integration, performance)
- ✅ **7 Major Features** fully integrated (web, API, visual, ML, performance)
- ✅ **6 Library Integrations** (Pandas, ML, monitoring, etc.)
- ✅ **Multiple Test Types** (smoke, regression, visual, security, database)
- ✅ **Production-Ready** enterprise capabilities
- ✅ **ML-Powered** intelligence features
- ✅ **Parallel Execution** support for faster testing
- ✅ **Code Quality** integrated (ruff, mypy, bandit, safety)

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

## 🏗️ Architecture Overview

```
PythonSeleniumProject/
├── 🧪 tests/                 # Test suites (unit, integration, performance)
│   ├── unit/                 # Fast, isolated unit tests
│   ├── integration/          # End-to-end and visual regression tests
│   ├── api/                  # REST API testing
│   └── performance/          # Load testing and benchmarking
├── 📄 pages/                 # Page Object Model implementations
├── 🔧 utils/                 # Core framework utilities
│   ├── test_data_manager.py  # Data loading and export
│   ├── test_reporter.py      # Analytics and reporting
│   ├── ml_test_analyzer.py   # AI-powered test intelligence
│   └── performance_monitor.py # Performance tracking
├── ⚙️ config/                # Environment configurations
└── 📊 data/results/          # Test execution data for ML analysis
```

---

**Ready to automate your testing?** Start with `python run_full_workflow.py` 🚀

**Need help?** Check [documentation/INDEX.md](documentation/INDEX.md) for detailed guides.
