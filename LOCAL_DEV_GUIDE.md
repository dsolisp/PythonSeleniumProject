# Local Development Tools Guide

This guide shows you how to use the code quality and security tools **locally** during development, the same tools that run in the CI/CD pipeline.

## 🛠️ Setup Development Tools

```bash
# Install framework with development tools (recommended)
pip install -r requirements.txt

# For advanced CI/CD features (optional)
pip install -r requirements-dev.txt
```

**Note:** All essential development tools (black, flake8, mypy, bandit, safety) are now included in the main `requirements.txt` for easy local development!

## 📝 Code Quality Tools (Local Usage)

### 1. **Code Formatting with Black**

**Check formatting issues:**
```bash
black --check --diff .
```

**Auto-fix formatting:**
```bash
black .
```

**Format specific files:**
```bash
black pages/base_page.py utils/
```

### 2. **Import Sorting with isort**

**Check import order:**
```bash
isort . --check-only --diff
```

**Auto-fix import sorting:**
```bash
isort .
```

**Fix specific files:**
```bash
isort pages/ tests/
```

### 3. **Code Linting with flake8**

**Check for code issues:**
```bash
flake8 . --max-line-length=88
```

**Check only critical errors:**
```bash
flake8 . --select=E9,F63,F7,F82 --show-source
```

**Check specific directories:**
```bash
flake8 pages/ tests/ utils/
```

### 4. **Type Checking with mypy**

**Check type annotations:**
```bash
mypy . --ignore-missing-imports
```

**Check specific files:**
```bash
mypy pages/base_page.py --ignore-missing-imports
```

## 🔒 Security Tools (Local Usage)

### 5. **Security Scanning with Bandit**

**Scan for security vulnerabilities:**
```bash
bandit -r .
```

**Generate JSON report:**
```bash
bandit -r . -f json -o security-report.json
```

**Exclude certain files:**
```bash
bandit -r . --exclude venv-enhanced/,node_modules/
```

### 6. **Dependency Security with Safety**

**Check for vulnerable dependencies:**
```bash
safety check
```

**Generate JSON report:**
```bash
safety check --json --output safety-report.json
```

**Check specific requirements file:**
```bash
safety check -r requirements.txt
```

## ⚡ Quick Development Workflow

**Pre-commit checks (run before committing):**
```bash
# Format and organize code
black .
isort .

# Check for issues
flake8 . --max-line-length=88
mypy . --ignore-missing-imports

# Security checks
bandit -r . --exclude venv-enhanced/
safety check

# Run tests
pytest -v
```

## 🚀 Automated Git Hooks (Optional)

Install pre-commit hooks to run these tools automatically:

```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', '.', '--exclude', 'venv-enhanced/']
```

## 🎯 IDE Integration

### VS Code Settings

Add to `.vscode/settings.json`:
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true,
  "editor.formatOnSave": true,
  "python.sortImports.args": ["--profile", "black"]
}
```

### PyCharm Settings

1. **Black**: File → Settings → Tools → External Tools → Add Black
2. **isort**: File → Settings → Tools → External Tools → Add isort  
3. **flake8**: File → Settings → Tools → External Tools → Add flake8

## 📊 Understanding the Results

### Black Output
- **Reformatted files**: Automatically fixed formatting
- **Would reformat**: Preview of changes with `--check --diff`

### isort Output  
- **Fixing**: Import order corrections
- **Skipped**: Files already correctly formatted

### flake8 Codes
- **E9**: Runtime syntax errors
- **F63**: Invalid syntax in type comments  
- **F7**: Syntax errors in docstrings
- **F82**: Undefined names in `__all__`

### Bandit Severity
- **LOW**: Minor security issues
- **MEDIUM**: Moderate security concerns
- **HIGH**: Critical security vulnerabilities

### Safety Output
- **Vulnerabilities found**: Dependencies with known security issues
- **Recommendations**: Updated package versions to install

## 🔄 CI/CD Integration

These **same commands** run automatically in the GitHub Actions pipeline:

- **Security Stage**: `bandit -r .` and `safety check`
- **Code Quality Stage**: `black --check`, `isort --check-only`, `flake8`, `mypy`
- **Test Stage**: `pytest` with coverage reports

Your local checks ensure CI/CD pipeline success! 🎉