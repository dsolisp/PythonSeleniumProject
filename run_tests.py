#!/usr/bin/env python3
"""
Test runner script for the test automation framework.
Provides easy commands to run different types of tests.
"""

import argparse
import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print("=" * 60)

    try:
        subprocess.run(command, shell=True, check=True, cwd=os.getcwd())
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test runner for automation framework")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "regression", "all"],
        default="regression",
        help="Type of tests to run (default: regression)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run tests with verbose output"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )

    args = parser.parse_args()

    # Build base command
    base_cmd = "python -m pytest"
    if args.verbose:
        base_cmd += " -v"
    if args.coverage:
        base_cmd += " --cov=. --cov-report=html --cov-report=term"

    success = True

    if args.type == "unit":
        success &= run_command(
            f"{base_cmd} tests/unit/test_regression_protection.py",
            "Unit Tests (Core Regression Protection)",
        )
    elif args.type == "integration":
        success &= run_command(f"{base_cmd} tests/integration/", "Integration Tests")
    elif args.type == "regression":
        success &= run_command(
            f"{base_cmd} tests/unit/test_regression_protection.py",
            "Regression Protection Tests",
        )
    elif args.type == "all":
        success &= run_command(
            f"{base_cmd} tests/unit/test_regression_protection.py",
            "Unit Tests (Regression Protection)",
        )
        success &= run_command(f"{base_cmd} tests/integration/", "Integration Tests")

    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Framework is protected against regression during refactoring")
    else:
        print("💥 SOME TESTS FAILED!")
        print("⚠️  Framework may have regressions - check before refactoring")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
