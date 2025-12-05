#!/usr/bin/env python3
"""
Test Runner Script for Python Selenium Test Automation Framework

Provides easy commands to run different types of tests with automatic
test result export and historical tracking.

Test Categories (256 total tests):
  - API tests (5): REST API validation with conditional Allure
  - Unit tests (229): Core functionality, library integrations, settings
  - Integration tests (19): Framework core, page integration, image diff
  - Performance tests (3): Benchmarking and monitoring
  - Web tests: Selenium & Playwright UI automation

Features:
  - Automatic test result export to data/results/
  - Historical test tracking via pytest-history (SQLite-based)
  - Flaky test detection: run `pytest-history flakes` or use --flaky flag
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
    Export test results to YAML for archiving.

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


def main():
    parser = argparse.ArgumentParser(
        description="Test runner with automatic result export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --type api -v              # Run API tests with verbose output
  python run_tests.py --type unit --coverage     # Run unit tests with coverage
  python run_tests.py --type all                 # Run all test suites (~256 tests)
  python run_tests.py --type regression          # Quick smoke test

Test Counts:
  api         : 5 tests (REST API with conditional Allure)
  unit        : ~180 tests (core, libraries, settings, etc.)
  integration : 19 tests (framework core, page integration)
  performance : 3 tests (benchmarking, monitoring)
  web         : Multiple (Selenium & Playwright UI tests)
  all         : ~200 tests (comprehensive suite)
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
        help="Skip test result export",
    )
    parser.add_argument(
        "--flaky",
        action="store_true",
        help="Show flaky tests summary after run (uses pytest-history)",
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

    # Show flaky tests if requested
    if args.flaky:
        print(f"\n{'=' * 60}")
        print("🔍 FLAKY TEST ANALYSIS (pytest-history)")
        print("=" * 60)
        try:
            flaky_result = subprocess.run(
                ["pytest-history", "flakes"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                check=False,
            )
            if flaky_result.stdout.strip():
                print(flaky_result.stdout)
            else:
                print("No flaky tests detected yet.")
                print("Run more tests to build history for flaky detection.")
        except FileNotFoundError:
            print(
                "⚠️  pytest-history CLI not found. Install: pip install pytest-history"
            )

    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
