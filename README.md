# Python Selenium Test Automation Framework

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.16-green.svg)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.40-blueviolet.svg)](https://playwright.dev)
[![Pytest](https://img.shields.io/badge/Pytest-8.4-orange.svg)](https://pytest.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Enterprise-grade test automation with ML-powered intelligence** 🚀

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
- **Cross-Browser**: Chrome, Firefox, Edge, Safari support

### 📊 Intelligence & Analytics
- **ML-Powered**: AI failure prediction and flaky test detection
- **Advanced Analytics**: Pandas-powered statistical analysis
- **Smart Reporting**: HTML dashboards and CSV exports

### 🔧 Enterprise Features
- **Self-Healing**: Automatic retry with intelligent error recovery
- **Performance Monitoring**: Real-time metrics and load testing
- **Data Management**: Multi-format support (JSON/YAML/CSV)

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
# Run specific test categories
pytest tests/api/ -v          # API tests
pytest tests/web/ -v          # Web UI tests  
pytest tests/unit/ -v         # Unit tests

# With Allure reporting
pytest tests/ --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 📚 Documentation

| Feature | Tutorial | Description |
|---------|----------|-------------|
| **Analytics** | [📊 Analytics Guide](documentation/ANALYTICS_AND_REPORTING.md) | Pandas analytics & dashboards |
| **ML Intelligence** | [🤖 ML Guide](documentation/ML_INTEGRATION.md) | AI-powered test optimization |
| **API Testing** | [🔗 API Guide](documentation/API_TESTING.md) | REST automation with Allure |
| **Playwright** | [🎭 Playwright Guide](documentation/PLAYWRIGHT_INTEGRATION.md) | Modern browser automation |
| **All Docs** | [📖 Index](documentation/INDEX.md) | Complete documentation |

## 🛠️ Automation Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| **Full Pipeline** | Complete QA workflow | `python run_full_workflow.py` |
| **Environment Setup** | Auto-setup venv & deps | `./setup_env.sh` |
| **Result Normalization** | Data processing | `python scripts/normalize_results.py` |
| **Quality Checks** | Code validation | `bash scripts/run_ci_checks.sh` |

## 🏆 Framework Stats

- ✅ **293+ Tests** across all categories
- ✅ **7 Major Features** fully integrated  
- ✅ **6 Library Integrations** (Pandas, ML, etc.)
- ✅ **Production-Ready** enterprise capabilities
- ✅ **ML-Powered** intelligence features

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

## 🤝 Contributing

1. Fork the repository
2. Run quality checks: `bash scripts/run_ci_checks.sh`
3. Make changes and test: `python run_full_workflow.py`
4. Submit a pull request

---

**Ready to automate your testing?** Start with `python run_full_workflow.py` 🚀

**Need help?** Check [documentation/INDEX.md](documentation/INDEX.md) for detailed guides.
