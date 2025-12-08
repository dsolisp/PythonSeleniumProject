# Local Development Tools Guide

This guide shows you how to use the code quality and security tools **locally** during development, the same tools that run in the CI/CD pipeline.

## 🛠️ Setup Development Tools

```bash
# Install framework with development tools (recommended)
pip install -r requirements.txt

# For advanced CI/CD features (optional)
pip install -r requirements-dev.txt
```

**Note:** All essential development tools (ruff, mypy, bandit, safety) are now included in the main `requirements.txt` for easy local development!

## 📝 Code Quality Tools (Local Usage)

### 1. **Code Formatting & Linting with Ruff**

**Check for code issues:**
```bash
ruff check .
```

**Auto-fix code issues:**
```bash
ruff check --fix .
```

**Check formatting:**
```bash
ruff format --check .
```

**Auto-fix formatting:**
```bash
ruff format .
```

**Check specific files/directories:**
```bash
ruff check pages/base_page.py
ruff format utils/
```

### 2. **Type Checking with mypy** (Optional)

> **Note**: This project uses a simplified approach with clear docstrings instead of complex type hints (`Any`, `Optional`, etc.). mypy is still available for checking any type annotations that exist.

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
# Format and fix code with Ruff
ruff check --fix .
ruff format .

# Check for issues
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
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
  - repo: https://github.com/PyCQA/bandit
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
  "python.formatting.provider": "none",
  "ruff.enable": true,
  "ruff.organizeImports": true,
  "ruff.fixAll": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.ruff": "explicit",
    "source.organizeImports.ruff": "explicit"
  },
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true
}
```

### PyCharm Settings

1. **Ruff**: Install the Ruff plugin, then configure it as the formatter and linter
2. **MyPy**: File → Settings → Tools → External Tools → Add MyPy  
3. **Bandit**: File → Settings → Tools → External Tools → Add Bandit

## 📊 Understanding the Results

### Ruff Output
- **Fixed**: Issues that were automatically corrected
- **Would reformat**: Files that need formatting (use `ruff format` to fix)
- **Found X errors**: Code quality issues detected (use `ruff check --fix` to auto-fix where possible)

### mypy Output
- **Success**: No type errors found
- **error: X**: Type annotation issues to fix
- **note: X**: Additional type information

### Bandit Severity
- **LOW**: Minor security issues
- **MEDIUM**: Moderate security concerns  
- **HIGH**: Critical security vulnerabilities

### Safety Output
- **Vulnerabilities found**: Dependencies with known security issues
- **Recommendations**: Updated package versions to install

## 🔄 CI/CD Integration

These **same commands** run automatically in the GitHub Actions pipeline:

- **Code Quality Stage**: `ruff check` and `ruff format --check` (replaces black, isort, flake8)
- **Type Checking Stage**: `mypy` for type annotations
- **Security Stage**: `bandit -r .` and `safety check`
- **Test Stage**: `pytest` with coverage reports

Your local checks ensure CI/CD pipeline success! 🎉