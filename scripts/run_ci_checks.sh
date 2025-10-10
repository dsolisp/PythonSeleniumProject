#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Activate venv-enhanced if not already active
if [ -z "${VIRTUAL_ENV-}" ] && [ -f "$ROOT_DIR/venv-enhanced/bin/activate" ]; then
  source "$ROOT_DIR/venv-enhanced/bin/activate"
fi

echo "Running CI-style checks from: $ROOT_DIR"
echo "Using python: $(which python)"
echo "Python version: $(python --version 2>&1)"
echo "Pip version: $(pip --version 2>&1)"
echo "VIRTUAL_ENV: ${VIRTUAL_ENV-}"

FAILED=0

run_check() {
  echo
  echo "> $*"
  if ! "$@"; then
    echo "   FAIL: $*"
    FAILED=1
  else
    echo "   OK"
  fi
}

# Define included source directories (edit as needed)
INCLUDE_DIRS="pages tests utils config locators"

# Exclude patterns for tools that support it
EXCLUDE_CSV="venv,venv-enhanced,.venv,__pycache__,.pytest_cache,.git,build,dist,data/results,downloads,drivers,reports,test_reports,logs,screenshots,screenshots_diff,resources"

# Auto-fix stage using Ruff (replaces black, isort, autoflake)
echo
echo "=== Auto-fix stage (Ruff) ==="
for DIR in $INCLUDE_DIRS; do
  if [ -d "$DIR" ]; then
    echo "Fixing $DIR..."
    run_check python -m ruff check --fix "$DIR"
    run_check python -m ruff format "$DIR"
  fi
done

# Checks using Ruff (replaces flake8, black --check, isort --check-only)
echo
echo "=== Quality checks (Ruff) ==="
run_check python -m ruff check $INCLUDE_DIRS
run_check python -m ruff format --check $INCLUDE_DIRS

# Keep mypy for type checking (Ruff has limited type checking)
echo
echo "=== Type checking (mypy) ==="
run_check python -m mypy pages/ utils/ --ignore-missing-imports

# Keep bandit for security scanning (Ruff has some security rules but bandit is more comprehensive)
echo
echo "=== Security scanning (bandit) ==="
python -m bandit -r $INCLUDE_DIRS \
  -s B101,B105,B110,B112,B311,B404,B603 \
  --exclude "$EXCLUDE_CSV" || true

# Safety: only run if SAFETY_API_KEY present
if [ -n "${SAFETY_API_KEY-}" ]; then
  echo
  echo "=== Dependency security (safety) ==="
  run_check python -m safety check
else
  echo "Skipping safety check (set SAFETY_API_KEY to enable non-interactive safety)"
fi

if [ "$FAILED" -ne 0 ]; then
  echo
  echo "One or more checks failed. Inspect the output above."
  exit 2
else
  echo
  echo "All checks completed successfully!"
  exit 0
fi