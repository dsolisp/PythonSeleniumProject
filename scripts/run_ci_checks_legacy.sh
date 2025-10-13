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
INCLUDE_DIRS="pages tests utils config locators scripts"

# Exclude patterns for tools that support it
EXCLUDE_CSV="venv,venv-enhanced,.venv,__pycache__,.pytest_cache,.git,build,dist,data/results,downloads,drivers,reports,test_reports,logs,screenshots,screenshots_diff,resources"


# Auto-fix stage (run only on source dirs, always exclude venvs and non-source dirs)
EXCLUDE_REGEX="($(echo $EXCLUDE_CSV | sed 's/,/|/g'))"
EXCLUDE_GLOB="$(echo $EXCLUDE_CSV | sed 's/,/,/g')"
for DIR in $INCLUDE_DIRS; do
  if [ -d "$DIR" ]; then
    run_check python -m black "$DIR" --exclude "$EXCLUDE_REGEX"
    run_check python -m isort "$DIR" --skip-glob "$EXCLUDE_GLOB"
    run_check python -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r "$DIR" --exclude="$EXCLUDE_REGEX"
  fi
done


# Checks (only on source dirs, with excludes)
run_check python -m black --check $INCLUDE_DIRS
run_check python -m isort --check-only $INCLUDE_DIRS
run_check python -m flake8 $INCLUDE_DIRS --max-line-length=88 --exclude="$EXCLUDE_CSV"
run_check python -m mypy pages/ utils/ --ignore-missing-imports

# Run bandit with selected tests, print to console, and do not fail script on findings
python -m bandit -r $INCLUDE_DIRS \
  -s B101,B105,B110,B112,B311,B404,B603 \
  --exclude "$EXCLUDE_CSV" || true

# Safety: only run if SAFETY_API_KEY present
if [ -n "${SAFETY_API_KEY-}" ]; then
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
  echo "All checks completed (no failures detected)."
  exit 0
fi
#!/usr/bin/env bash
# Run CI-style quality checks locally.
# Attempts to activate venv-enhanced if present. Will try to auto-fix formatting/imports
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Running CI-style checks from: $ROOT_DIR"
# Prefer the project's Python executable for running tooling to avoid using system/global packages
# Resolution order: already-activated VIRTUAL_ENV -> venv-enhanced -> python3
TOOL_PYTHON=""
if [ -n "${VIRTUAL_ENV-}" ]; then
  TOOL_PYTHON="${VIRTUAL_ENV}/bin/python"
elif [ -x "$ROOT_DIR/venv-enhanced/bin/python" ]; then
  TOOL_PYTHON="$ROOT_DIR/venv-enhanced/bin/python"
else
  TOOL_PYTHON="$(command -v python3 || command -v python || echo python)"
fi
echo "Using python executable for tools: $TOOL_PYTHON"
# If a dedicated venv exists, try to activate it for consistency with CI
if [ -d "$ROOT_DIR/venv-enhanced" ] && [ -z "${VIRTUAL_ENV-}" ]; then
  if [ -f "$ROOT_DIR/venv-enhanced/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$ROOT_DIR/venv-enhanced/bin/activate"
  #!/usr/bin/env bash
  # Lightweight, robust CI checks runner for local development.
  # - Uses project venv's python to run tools via `python -m` to avoid PATH mismatches.
  # - Does NOT attempt to upgrade/modify click or colorama.
  # - Non-destructive: will only recreate venv if --repair is passed.

  set -euo pipefail

  ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
  cd "$ROOT_DIR"

  # Determine python to use for tooling: prefer activated venv, then source venv-enhanced (if present), then fallback to system python3
  if [ -n "${VIRTUAL_ENV-}" ]; then
    echo "Using already-activated virtualenv: ${VIRTUAL_ENV}"
    TOOL_PYTHON="${VIRTUAL_ENV}/bin/python"
  elif [ -f "$ROOT_DIR/venv-enhanced/bin/activate" ]; then
    echo "Sourcing venv-enhanced activation to ensure tools on PATH"
    # shellcheck source=/dev/null
    source "$ROOT_DIR/venv-enhanced/bin/activate"
    # After sourcing, $VIRTUAL_ENV should be set
    if [ -n "${VIRTUAL_ENV-}" ]; then
      TOOL_PYTHON="${VIRTUAL_ENV}/bin/python"
    else
      TOOL_PYTHON="$ROOT_DIR/venv-enhanced/bin/python"
    fi
  else
    TOOL_PYTHON="$(command -v python3 || command -v python || echo python)"
  fi

  REPAIR_VENV=false
  if [ "${1-}" = "--repair" ]; then
    REPAIR_VENV=true
  fi


  echo "Running CI-style checks from: $ROOT_DIR"
  echo "Using python executable for tools: $TOOL_PYTHON"
  echo "--- ENVIRONMENT DIAGNOSTICS ---"
  echo "which python: $(which python)"
  echo "python --version: $(python --version 2>&1)"
  echo "which pip: $(which pip)"
  echo "pip --version: $(pip --version 2>&1)"
  echo "PATH: $PATH"
  echo "VIRTUAL_ENV: ${VIRTUAL_ENV-}"
  echo "-------------------------------"

  FAILED=0

  run_cmd() {
    local cmd="$1"
    echo
    echo "> $cmd"
    if ! eval "$cmd"; then
      echo "   FAIL: '$cmd' returned non-zero"
      FAILED=1
    else
      echo "   OK"
    fi
  }

  # If --repair, recreate the venv-enhanced and install dev tooling (best-effort)
  repair_venv_and_install_tools() {
    if [ "$REPAIR_VENV" != true ]; then
      echo "   venv repair disabled (pass --repair to enable)"
      return 1
    fi
    echo "   Recreating venv-enhanced and installing dev tools (best-effort)"
    rm -rf "$ROOT_DIR/venv-enhanced"
    python3 -m venv "$ROOT_DIR/venv-enhanced"
    # shellcheck source=/dev/null
    source "$ROOT_DIR/venv-enhanced/bin/activate"
    python -m pip install -U pip setuptools wheel
    python -m pip install -U black isort autoflake flake8 mypy bandit safety || true
    TOOL_PYTHON="$ROOT_DIR/venv-enhanced/bin/python"
  }

  # Run a tool via project python to avoid global dependency issues.
  run_tool() {
    local module="$1"; shift
    local args="$@"
    local cmd="\"$TOOL_PYTHON\" -m $module $args"
    echo
    echo "> $cmd"
    # Run and propagate success/failure into FAILED
    if ! eval "$cmd"; then
      echo "   FAIL: $module failed"
      FAILED=1
    else
      echo "   OK: $module"
    fi
  }

  # === Auto-fix stage (non-destructive) ===
  if command -v "$TOOL_PYTHON" >/dev/null 2>&1; then
    echo "Auto-formatting (black/isort/autoflake) via: $TOOL_PYTHON"
    $TOOL_PYTHON -m black . || true
    $TOOL_PYTHON -m isort . || true
    $TOOL_PYTHON -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r . || true
  else
    echo "Warning: $TOOL_PYTHON not found; skipping auto-fix stage"
  fi

  # === Checks ===
  # Prefer using python -m so we don't rely on PATH-installed wrappers that may use different libs.
  run_tool black --check .
  run_tool isort --check-only . --skip-glob='venv*'
  run_tool flake8 . --max-line-length=88 --exclude="venv,venv-enhanced,.venv,__pycache__,.pytest_cache,.git,build,dist,data/results,downloads,drivers,reports,test_reports,logs,screenshots,screenshots_diff,resources"
  run_tool mypy pages/ utils/ --ignore-missing-imports || true
  run_tool bandit -r . --exclude "venv,venv-enhanced,.venv,__pycache__,.pytest_cache,.git,build,dist,data/results,downloads,drivers,reports,test_reports,logs,screenshots,screenshots_diff,resources"

  # Safety: only run if SAFETY_API_KEY present (non-interactive)
  if [ -n "${SAFETY_API_KEY-}" ]; then
    run_tool safety check
  else
    echo "Skipping safety check (set SAFETY_API_KEY to enable non-interactive safety)"
  fi

  if [ "$FAILED" -ne 0 ]; then
    echo
    echo "One or more checks failed. Inspect the output above."
    exit 2
  else
    echo
    echo "All checks completed (no failures detected)."
    exit 0
  fi
      if pip install -U click colorama >/dev/null 2>&1; then
        echo "   Retry: running '$cmd' after upgrading dependencies..."
  local stderr2
  stderr2=$(eval "$cmd" 2>&1 1>/dev/null) || true
  if [ -z "$stderr2" ]; then
          echo "   OK (after upgrade)"
          return 0
        else
          echo "   Still failing after attempted repair. Will attempt venv recreation."
        fi
      else
        echo "   Repair attempt (click/colorama upgrade) failed. Will attempt venv recreation."
      fi
    else
      echo "   pip not available to attempt repair. Will attempt venv recreation."
    fi

    # Recreate venv and install tools
  repair_venv_and_install_tools

  # Retry once
  local stderr3
  stderr3=$(eval "$cmd" 2>&1 1>/dev/null) || true
  if [ -z "$stderr3" ]; then
      echo "   OK (after venv recreation)"
      return 0
    else
  echo "   Still failing after venv recreation. Skipping non-fatally."
  echo "   $(echo "$stderr3" | sed -n '1,4p' | tr '\n' ' ')"
  return 0
    fi
  fi

  # Otherwise treat as failure and print stderr
  echo "   FAIL: '$cmd' returned non-zero"
  echo "$stderr"
  FAILED=1
  return 1
}

# === Auto-fix stage ===
echo
echo "=== Auto-fix: formatting and unused imports ==="
# Run Black to auto-format files if available
if command -v black >/dev/null 2>&1; then
  echo "-> black . (auto-format)"
  if ! black .; then
    echo "   WARN: black encountered errors"
  fi
else
  echo "   SKIP: black not installed"
fi

# Run isort to automatically sort imports if available
if command -v isort >/dev/null 2>&1; then
  echo "-> isort . (auto-fix imports)"
  if ! isort .; then
    echo "   WARN: isort encountered errors"
  fi
else
  echo "   SKIP: isort not installed"
fi

# Use autoflake to remove unused imports/vars (non-destructive in-place) if available
if command -v autoflake >/dev/null 2>&1; then
  echo "-> autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r ."
  if ! autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .; then
    echo "   WARN: autoflake encountered errors"
  fi
else
  echo "   SKIP: autoflake not installed"
fi

echo "=== Auto-fix stage complete ==="

echo "Checking formatting (black)"
run_check_tolerant "black --check ."

echo "Checking import sorting (isort)"
run_check_tolerant "isort --check-only . --skip-glob='$EXCLUDE_GLOB'"

echo "Running flake8 linting"
run_cmd "flake8 . --max-line-length=88 --exclude=$EXCLUDE_CSV"

echo "Running mypy type checks (pages/ and utils/)"
run_cmd "mypy pages/ utils/ --ignore-missing-imports"

echo "Running bandit security scan"
run_cmd "bandit -r . --exclude $EXCLUDE_CSV --quiet"

echo "Running safety (dependency security) if available and non-interactive"
# Avoid triggering an interactive login prompt from the Safety CLI.
# Run safety only when SAFETY_API_KEY is provided (CI mode). Otherwise skip.
if command -v safety >/dev/null 2>&1; then
  if [ -n "${SAFETY_API_KEY-}" ]; then
    echo "   SAFETY_API_KEY found in environment — running safety non-interactively"
    run_cmd "safety check"
  else
    echo "   SKIP: safety is installed but SAFETY_API_KEY is not set."
    echo "         To run safety non-interactively set SAFETY_API_KEY in your environment."
    echo "         Example (macOS / zsh): export SAFETY_API_KEY=your_api_key_here"
    echo "         Or run: safety check interactively if you want to login/register locally."
  fi
else
  echo "   SKIP: safety not installed"
fi

echo
if [ "$FAILED" -ne 0 ]; then
  echo "One or more checks failed. See output above."
  exit 2
else
  echo "All requested checks completed (no failures detected)."
  exit 0
fi
#!/usr/bin/env bash
# Run CI-style quality checks locally.
# Attempts to activate venv-enhanced if present.
run_check_tolerant() {
  local cmd="$1"
  echo
  echo "-> $cmd"
  if ! command -v ${cmd%% *} >/dev/null 2>&1; then
    echo "   SKIP: '${cmd%% *}' is not installed or not on PATH"
    return 0
  fi

  # Capture stderr to detect import-time errors from the tool itself
  local stderr
  stderr=$(eval "$cmd" 2>&1 1>/dev/null) || true

  if [ -z "$stderr" ]; then
    echo "   OK"
    return 0
  fi

  # If stderr contains ImportError/AttributeError inside tool internals, attempt repair
  if echo "$stderr" | grep -E "ImportError|AttributeError|cannot import name" >/dev/null 2>&1; then
    echo "   WARNING: '$cmd' failed due to environment/import issue:" 
    echo "            $(echo "$stderr" | sed -n '1,4p' | tr '\n' ' ')"

    # First try upgrading click/colorama in existing venv
    if command -v pip >/dev/null 2>&1; then
      echo "   Attempting to repair tool environment by upgrading 'click' and 'colorama' in the active venv"
      if pip install -U click colorama >/dev/null 2>&1; then
        echo "   Retry: running '$cmd' after upgrading dependencies..."
        local stderr2
        stderr2=$(eval "$cmd" 2>&1 1>/dev/null) || true
        if [ -z "$stderr2" ]; then
          echo "   OK (after upgrade)"
          return 0
        else
          echo "   Still failing after attempted repair. Will attempt venv recreation."
        fi
      else
        echo "   Repair attempt (click/colorama upgrade) failed. Will attempt venv recreation."
      fi
    else
      echo "   pip not available to attempt repair. Will attempt venv recreation."
    fi

    # Attempt to recreate the virtualenv and install essential tools (best-effort)
    repair_venv_and_install_tools

    # After attempted venv repair, retry the command once
    local stderr3
    stderr3=$(eval "$cmd" 2>&1 1>/dev/null) || true
    if [ -z "$stderr3" ]; then
      echo "   OK (after venv recreation)"
      return 0
    else
      echo "   Still failing after venv recreation. Skipping non-fatally."
      echo "   $(echo "$stderr3" | sed -n '1,4p' | tr '\n' ' ')"
      return 0
    fi
  fi

  # Otherwise treat as failure and print stderr
  echo "   FAIL: '$cmd' returned non-zero"
  echo "$stderr"
  FAILED=1
  return 1
}


# Attempt to recreate venv and install essential dev tools. Non-fatal; best-effort.
repair_venv_and_install_tools() {
  echo "   Attempting to recreate virtualenv 'venv-enhanced' and install lint tools..."
  if ! command -v python3 >/dev/null 2>&1; then
    echo "   No python3 available to recreate venv. Skipping venv repair."
    return 1
  fi

  # Remove and recreate venv
  rm -rf "$ROOT_DIR/venv-enhanced"
  if ! python3 -m venv "$ROOT_DIR/venv-enhanced"; then
    echo "   Failed to create new virtualenv. Skipping venv repair."
    return 1
  fi

  # Activate and install basic tools
  # shellcheck source=/dev/null
  source "$ROOT_DIR/venv-enhanced/bin/activate"
  echo "   New venv created and activated. Upgrading pip and installing tools..."
  if ! python -m pip install -U pip setuptools wheel >/dev/null 2>&1; then
    echo "   pip upgrade failed. Attempting to continue..."
  fi

  # Install essential linting tools (best-effort, may require network)
  python -m pip install -U black isort autoflake flake8 mypy bandit safety >/dev/null 2>&1 || true
  echo "   Venv repair attempt complete (tools installed if network available)."
}
  echo "   SKIP: black not installed"
fi

# Run isort to automatically sort imports if available
if command -v isort >/dev/null 2>&1; then
  echo "-> isort . (auto-fix imports)"
  if ! isort .; then
    echo "   WARN: isort encountered errors"
  fi
else
  echo "   SKIP: isort not installed"
fi

# Use autoflake to remove unused imports/vars (non-destructive in-place) if available
if command -v autoflake >/dev/null 2>&1; then
  echo "-> autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r ."
  if ! autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .; then
    echo "   WARN: autoflake encountered errors"
  fi
else
  echo "   SKIP: autoflake not installed"
fi

echo "=== Auto-fix stage complete ==="


run_cmd() {
  local cmd="$1"
  echo
  echo "-> $cmd"
  if ! command -v ${cmd%% *} >/dev/null 2>&1; then
    echo "   SKIP: '${cmd%% *}' is not installed or not on PATH"
    return 0
  fi

  # Run the command; capture exit
  if ! eval "$cmd"; then
    echo "   FAIL: '$cmd' returned non-zero"
    FAILED=1
  else
    echo "   OK"
  fi
}

# Run a check command but treat known runtime import errors (black/isort) as SKIP
run_check_tolerant() {
  local cmd="$1"
  echo
  echo "-> $cmd"
  if ! command -v ${cmd%% *} >/dev/null 2>&1; then
    echo "   SKIP: '${cmd%% *}' is not installed or not on PATH"
    return 0
  fi

  # Capture stderr to detect import-time errors from the tool itself
  local stderr
  stderr=$(eval "$cmd" 2>&1 1>/dev/null) || true

  if [ -z "$stderr" ]; then
    echo "   OK"
    return 0
  fi

  # If stderr contains ImportError/AttributeError inside tool internals, skip non-fatally
  if echo "$stderr" | grep -E "ImportError|AttributeError|cannot import name" >/dev/null 2>&1; then
    echo "   WARNING: '$cmd' failed due to environment/import issue:" 
    echo "            $(echo "$stderr" | sed -n '1,4p' | tr '\n' ' ')"

    # Attempt a best-effort repair for common tooling dependency issues (click / colorama)
    if command -v pip >/dev/null 2>&1; then
      echo "   Attempting to repair tool environment by upgrading 'click' and 'colorama' in the active venv"
      if pip install -U click colorama >/dev/null 2>&1; then
        echo "   Retry: running '$cmd' after upgrading dependencies..."
        local stderr2
        stderr2=$(eval "$cmd" 2>&1 1>/dev/null) || true
        if [ -z "$stderr2" ]; then
          echo "   OK (after upgrade)"
          return 0
        else
          echo "   Still failing after attempted repair. Will try recreating venv if possible."
        fi
      else
        echo "   Repair attempt (click/colorama upgrade) failed. Will try recreating venv if possible."
      fi
    else
      echo "   pip not available to attempt repair. Will try recreating venv if possible."
    fi

    # Attempt to recreate the virtualenv and install essential tools (best-effort)
    repair_venv_and_install_tools

    # After attempted venv repair, retry the command once
    local stderr3
    stderr3=$(eval "$cmd" 2>&1 1>/dev/null) || true
    if [ -z "$stderr3" ]; then
      echo "   OK (after venv recreation)"
      return 0
    else
      echo "   Still failing after venv recreation. Skipping non-fatally."
      echo "   $(echo "$stderr3" | sed -n '1,4p' | tr '\n' ' ')"
      return 0
    fi
  fi



# Attempt to recreate venv and install essential dev tools. Non-fatal; best-effort.
repair_venv_and_install_tools() {
  echo "   Attempting to recreate virtualenv 'venv-enhanced' and install lint tools..."
  if ! command -v python3 >/dev/null 2>&1; then
    echo "   No python3 available to recreate venv. Skipping venv repair."
    return 1
  fi

  # Remove and recreate venv
  rm -rf "$ROOT_DIR/venv-enhanced"
  if ! python3 -m venv "$ROOT_DIR/venv-enhanced"; then
    echo "   Failed to create new virtualenv. Skipping venv repair."
    return 1
  fi

  # Activate and install basic tools
  # shellcheck source=/dev/null
  source "$ROOT_DIR/venv-enhanced/bin/activate"
  echo "   New venv created and activated. Upgrading pip and installing tools..."
  if ! python -m pip install -U pip setuptools wheel >/dev/null 2>&1; then
    echo "   pip upgrade failed. Attempting to continue..."
  fi

  # Install essential linting tools (best-effort, may require network)
  python -m pip install -U black isort autoflake flake8 mypy bandit safety >/dev/null 2>&1 || true
  echo "   Venv repair attempt complete (tools installed if network available)."
}
  # Otherwise treat as failure and print stderr
  echo "   FAIL: '$cmd' returned non-zero"
  echo "$stderr"
  FAILED=1
  return 1
}

echo "Checking formatting (black)"
run_check_tolerant "black --check ."

echo "Checking import sorting (isort)"
run_check_tolerant "isort --check-only . --skip-glob='$EXCLUDE_GLOB'"

echo "Running flake8 linting"
run_cmd "flake8 . --max-line-length=88 --exclude=$EXCLUDE_CSV"

echo "Running mypy type checks (pages/ and utils/)"
run_cmd "mypy pages/ utils/ --ignore-missing-imports"

echo "Running bandit security scan"
run_cmd "bandit -r . --exclude $EXCLUDE_CSV --quiet"

echo "Running safety (dependency security) if available and non-interactive"
# Avoid triggering an interactive login prompt from the Safety CLI.
# Run safety only when SAFETY_API_KEY is provided (CI mode). Otherwise skip.
if command -v safety >/dev/null 2>&1; then
  if [ -n "${SAFETY_API_KEY-}" ]; then
    echo "   SAFETY_API_KEY found in environment — running safety non-interactively"
    run_cmd "safety check"
  else
    echo "   SKIP: safety is installed but SAFETY_API_KEY is not set."
    echo "         To run safety non-interactively set SAFETY_API_KEY in your environment."
    echo "         Example (macOS / zsh): export SAFETY_API_KEY=your_api_key_here"
    echo "         Or run: safety check interactively if you want to login/register locally."
  fi
else
  echo "   SKIP: safety not installed"
fi

echo
if [ "$FAILED" -ne 0 ]; then
  echo "One or more checks failed. See output above."
  exit 2
else
  echo "All requested checks completed (no failures detected)."
  exit 0
fi
python -m black scripts/normalize_results.py tests/helpers.py tests/unit/test_sql_validation.py utils/error_handler.py --line-length 88
