#!/usr/bin/env python3
"""
Integrated QA Automation Workflow Script

- Prepares environment (cleans old results, sets up directories)
- Runs all web and API tests
- Exports results for reporting
- Runs flaky test detection via pytest-history
- Prints clear output/report locations
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# --- VIRTUAL ENVIRONMENT DETECTION ---
VENV_DIR = Path(__file__).parent / "venv-enhanced"
VENV_PYTHON = VENV_DIR / "bin" / "python"
SETUP_SCRIPT = Path(__file__).parent / "setup_env.sh"


def ensure_venv():
    if not VENV_PYTHON.exists():
        print(
            f"[WARN] Virtual environment not found at {VENV_PYTHON}. "
            "Running setup_env.sh...",
        )
        if not SETUP_SCRIPT.exists():
            print("[ERROR] setup_env.sh not found! Please create it.")
            sys.exit(1)
        # Run the setup script
        result = subprocess.run(["bash", str(SETUP_SCRIPT)], check=False)
        if result.returncode != 0 or not VENV_PYTHON.exists():
            print("[ERROR] Failed to create virtual environment. Exiting.")
            sys.exit(1)
        print("[INFO] Virtual environment created.")


ensure_venv()

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).parent
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
REPORTS_DIR = PROJECT_ROOT / "reports"
WEB_TESTS = PROJECT_ROOT / "tests" / "web"
API_TESTS = PROJECT_ROOT / "tests" / "api"


# --- PRE-TEST: CLEANUP & SETUP ---
def clean_results():
    print("[PRE] Cleaning old reports (not results)...")
    # Do NOT delete data/results/ (preserve historical data)
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if REPORTS_DIR.exists():
        for f in REPORTS_DIR.glob("*.html"):
            f.unlink()
        for f in REPORTS_DIR.glob("*.csv"):
            f.unlink()
        for f in REPORTS_DIR.glob("*.json"):
            f.unlink()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[PRE] Results dir: {RESULTS_DIR}")
    print(f"[PRE] Reports dir: {REPORTS_DIR}")


def validate_environment():
    """Validate required packages are installed."""
    print("[PRE] Validating environment...")
    required_packages = [
        "selenium",
        "pytest",
        "pandas",
        "numpy",
        "structlog",
        "hamcrest",
        "tenacity",
        "psutil",
    ]
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print("Please install requirements.txt: pip install -r requirements.txt")
        sys.exit(1)
    print(f"[PRE] All {len(required_packages)} required packages found.")


# --- TEST EXECUTION ---
def run_pytest(test_path, label):
    print(f"[TEST] Running {label} tests: {test_path}")
    # Ensure results dir exists and create a timestamped json-report
    # directly in data/results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_file = RESULTS_DIR / f"test_results_{label}_{timestamp}.json"
    result = subprocess.run(
        [
            str(VENV_PYTHON),
            "-m",
            "pytest",
            str(test_path),
            "-v",
            "--json-report",
            f"--json-report-file={json_file}",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(f"[TEST] {label} tests failed. See output above.")
    else:
        print(f"[TEST] {label} tests completed successfully.")


def export_results():
    print("[POST] Exporting test results for reporting...")
    # If any json reports were created in reports/, copy them to
    # data/results for completeness.
    for f in REPORTS_DIR.glob("test_results_*.json"):
        dest = RESULTS_DIR / f.name
        shutil.copy2(f, dest)
        print(f"[POST] Exported: {dest}")

    # Also list json reports already in data/results (pytest now writes there directly)
    for f in RESULTS_DIR.glob("test_results_*.json"):
        print(f"[POST] Found result: {f}")


# --- POST-TEST: ANALYTICS & REPORTING ---
def run_analytics():
    print("[POST] Running analytics (CSV export)...")
    try:
        # Load all results from JSON files in data/results/
        all_results = []
        for f in RESULTS_DIR.glob("*.json"):
            with open(f) as fp:
                data = json.load(fp)
                tests = data.get("tests", data.get("test_results", []))
                all_results.extend(tests)

        if all_results:
            df = pd.DataFrame(all_results)
            csv_path = REPORTS_DIR / "analytics_summary.csv"
            df.to_csv(csv_path, index=False)
            print(f"[POST] Analytics CSV: {csv_path}")
        else:
            print("[POST] No test results found to analyze.")
    except (OSError, ValueError, RuntimeError) as e:
        print(f"[ERROR] Analytics failed: {e}")


def run_flaky_detection():
    print("[POST] Running flaky test detection (pytest-history)...")
    result = subprocess.run(
        [str(VENV_PYTHON), "-m", "pytest_history", "flakes"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip():
        print(result.stdout)
    else:
        print("[POST] No flaky tests detected yet. Run more tests to build history.")
    if result.returncode != 0 and result.stderr:
        print(f"[WARN] Flaky detection issue: {result.stderr}")


def archive_old_results(max_reports=30):
    print(f"[ARCHIVE] Checking for more than {max_reports} result files to keep...")
    result_files = sorted(RESULTS_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)
    if len(result_files) > max_reports:
        to_remove = result_files[:-max_reports]
        for f in to_remove:
            f.unlink()
            print(f"[ARCHIVE] Removed old result: {f}")
    else:
        print("[ARCHIVE] No removal needed.")


# --- MAIN WORKFLOW ---
def main():
    clean_results()
    validate_environment()
    run_pytest(WEB_TESTS, "web")
    run_pytest(API_TESTS, "api")
    export_results()
    run_analytics()
    run_flaky_detection()
    archive_old_results(max_reports=30)
    print(
        "\n[COMPLETE] Full workflow finished. See reports/ and "
        "data/results/ for outputs.",
    )


if __name__ == "__main__":
    main()
