#!/usr/bin/env python3
"""
Test Runner Script for Python Selenium Test Automation Framework

Provides easy commands to run different types of tests with automatic
test result export to YAML/JSON and ML-powered analysis.

Test Categories (256 total tests):
  - API tests (5): REST API validation with conditional Allure
  - Unit tests (229): Core functionality, library integrations, settings
  - Integration tests (19): Framework core, page integration, image diff
  - Performance tests (3): Benchmarking and monitoring
  - Web tests: Selenium & Playwright UI automation

Features:
  - Automatic test result export to data/results/
  - ML-powered analysis for flaky test detection & predictions
  - Performance tracking and anomaly detection
  - Comprehensive reporting
"""

import argparse
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from utils.test_data_manager import DataManager


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"🧪 {description}")
    print("=" * 60)

    try:
        # Convert string command to list for safer execution (no shell=True)
        # nosec B603 - Command constructed from trusted internal sources
        command_list = shlex.split(command) if isinstance(command, str) else command

        result = subprocess.run(
            command_list,
            shell=False,  # Security: Avoid shell injection
            check=True,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print(f"✅ {description} - PASSED")
    except subprocess.CalledProcessError as e:
        print(e.stdout if e.stdout else "")
        print(e.stderr if e.stderr else "", file=sys.stderr)
        print(f"❌ {description} - FAILED with exit code {e.returncode}")
        return False, e
    else:
        return True, result


def export_test_results(*, test_type: str, success: bool, duration: float):
    """
    Export test results to YAML for ML analysis.

    Args:
        test_type: Type of tests run (unit, integration, etc.)
        success: Whether tests passed
        duration: Test execution duration in seconds
    """
    try:
        # Import here to avoid dependency issues
        sys.path.insert(0, str(Path.cwd()))

        manager = DataManager()

        # Prepare results data
        results = {
            "test_run_type": test_type,
            "total_tests": "N/A",  # Will be populated from pytest output
            "passed": "N/A",
            "failed": "N/A",
            "success": success,
            "duration": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": os.getenv("TEST_ENV", "local"),
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
        }

        # Export to YAML
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"test_run_{test_type}_{timestamp}.yml"
        yaml_file = manager.save_test_results_yaml(results, filename=filename)

        print(f"\n📊 Test results exported to: {yaml_file}")
    except (OSError, ValueError) as e:
        print(f"⚠️  Failed to export test results: {e}")
        return None
    else:
        return yaml_file


def run_ml_analysis():
    """Run ML-powered test analysis on historical data."""
    print(f"\n{'=' * 60}")
    print("🤖 Running ML-Powered Test Analysis")
    print("=" * 60)

    try:
        # Check if we have test result data
        results_dir = Path("data/results")
        if not results_dir.exists() or not any(results_dir.rglob("*.json")):
            print("⚠️  No historical test data found for ML analysis")
            print("   Test data will accumulate over multiple runs")
            return

        # Run the ML analyzer
        analyzer_script = Path("utils/ml_test_analyzer.py")
        if not analyzer_script.exists():
            print("⚠️  ML analyzer script not found")
            return

        result = subprocess.run(
            [sys.executable, str(analyzer_script)],
            check=False,
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=60,
        )

        print(result.stdout)
        if result.stderr and "warning" not in result.stderr.lower():
            print(result.stderr, file=sys.stderr)

        # Check if report was generated
        report_path = Path("reports/ml_analysis_report.txt")
        if report_path.exists():
            print(f"\n✅ ML analysis complete! Report: {report_path}")
            print("\n📋 Quick Summary:")
            with Path.open(report_path) as f:
                lines = f.readlines()
                # Print first 20 lines of report
                for line in lines[:20]:
                    print(line.rstrip())

    except subprocess.TimeoutExpired:
        print("⚠️  ML analysis timed out (>60s)")
    except (OSError, RuntimeError) as e:
        print(f"⚠️  ML analysis failed: {e}")
        print("   Continuing without analysis...")


def main():
    parser = argparse.ArgumentParser(
        description="Test runner with automatic result export and ML analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --type api -v              # Run API tests with verbose output
  python run_tests.py --type unit --coverage     # Run unit tests with coverage
  python run_tests.py --type all                 # Run all test suites (~256 tests)
  python run_tests.py --type regression          # Quick smoke test
  python run_tests.py --type api --no-ml         # Skip ML analysis

Test Counts:
  api         : 5 tests (REST API with conditional Allure)
  unit        : 229 tests (core, libraries, settings, etc.)
  integration : 19 tests (framework core, page integration)
  performance : 3 tests (benchmarking, monitoring)
  web         : Multiple (Selenium & Playwright UI tests)
  all         : ~256 tests (comprehensive suite)
  regression  : Quick smoke test
        """,
    )
    parser.add_argument(
        "--type",
        choices=[
            "unit",
            "integration",
            "regression",
            "all",
            "api",
            "web",
            "performance",
        ],
        default="regression",
        help="Type of tests to run (default: regression)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Run tests with verbose output",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report",
    )
    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip test result export and ML analysis",
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help="Skip ML analysis (still exports results)",
    )

    args = parser.parse_args()

    # Track start time
    start_time = datetime.now(timezone.utc)

    # Build base command
    base_cmd = "python -m pytest"
    if args.verbose:
        base_cmd += " -v"
    if args.coverage:
        base_cmd += " --cov=. --cov-report=html --cov-report=term"

    success = True
    test_runs = []

    # Run tests based on type
    if args.type == "unit":
        # Run all unit tests (229 tests)
        success_result, _ = run_command(
            f"{base_cmd} tests/unit/ --maxfail=10",
            "Unit Tests (229 tests: core, features, libraries, settings, etc.)",
        )
        success &= success_result
        test_runs.append(("unit", success_result))

    elif args.type == "integration":
        # Run integration tests (19 tests)
        success_result, _ = run_command(
            f"{base_cmd} tests/integration/",
            "Integration Tests (19 tests: framework core, "
            "page integration, image diff)",
        )
        success &= success_result
        test_runs.append(("integration", success_result))

    elif args.type == "regression":
        # Quick regression check
        success_result, _ = run_command(
            f"{base_cmd} tests/unit/test_regression_protection.py",
            "Regression Protection Tests (quick smoke test)",
        )
        success &= success_result
        test_runs.append(("regression", success_result))

    elif args.type == "api":
        # Run API tests (5 tests with conditional Allure)
        success_result, _ = run_command(
            f"{base_cmd} tests/api/test_api.py",
            "API Tests (5 tests: GET, POST, performance with conditional Allure)",
        )
        success &= success_result
        test_runs.append(("api", success_result))

    elif args.type == "web":
        # Run web UI tests
        success_result, _ = run_command(
            f"{base_cmd} tests/web/",
            "Web UI Tests (Selenium & Playwright: search engine, sauce demo)",
        )
        success &= success_result
        test_runs.append(("web", success_result))

    elif args.type == "performance":
        # Run performance benchmarks (3 tests)
        success_result, _ = run_command(
            f"{base_cmd} tests/performance/test_benchmarks.py",
            "Performance Tests (3 tests: benchmarking and monitoring)",
        )
        success &= success_result
        test_runs.append(("performance", success_result))

    elif args.type == "all":
        # Run comprehensive test suite (256+ tests)
        print("\n🎯 Running COMPREHENSIVE Test Suite (~256 tests)")
        print("   This will take several minutes...\n")

        for test_type, cmd, desc in [
            ("api", f"{base_cmd} tests/api/test_api.py", "API Tests (5)"),
            (
                "unit",
                f"{base_cmd} tests/unit/ --maxfail=10",
                "Unit Tests (229)",
            ),
            (
                "integration",
                f"{base_cmd} tests/integration/",
                "Integration Tests (19)",
            ),
            (
                "performance",
                f"{base_cmd} tests/performance/test_benchmarks.py",
                "Performance Tests (3)",
            ),
        ]:
            success_result, _ = run_command(cmd, desc)
            success &= success_result
            test_runs.append((test_type, success_result))

    # Calculate duration
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    # Export results (unless disabled)
    if not args.no_export:
        print(f"\n{'=' * 60}")
        print("📊 Exporting Test Results")
        print("=" * 60)

        for test_type, test_success in test_runs:
            export_test_results(
                test_type=test_type,
                success=test_success,
                duration=duration,
            )

    # Run ML analysis (unless disabled)
    if not args.no_export and not args.no_ml:
        run_ml_analysis()

    # Summary
    print(f"\n{'=' * 60}")
    print("📋 TEST RUN SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total duration: {duration:.2f}s")
    print(f"🧪 Tests run: {', '.join([t[0] for t in test_runs])}")

    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Framework is protected against regression during refactoring")
    else:
        print("\n💥 SOME TESTS FAILED!")
        print("⚠️  Framework may have regressions - check before refactoring")

    if not args.no_export:
        print("\n📊 Test results exported for historical tracking")
        if not args.no_ml:
            print("🤖 ML analysis completed - check reports/ml_analysis_report.txt")

    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
