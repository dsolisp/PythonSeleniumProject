"""
Test Reporter with comprehensive analytics and reporting capabilities.
Provides detailed test execution analysis and multiple report formats.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Represents a single test result with comprehensive metadata."""

    name: str
    status: str  # passed, failed, skipped
    duration: float
    start_time: datetime
    end_time: datetime
    error_message: str | None = None
    error_type: str | None = None
    browser: str | None = None
    environment: str | None = None
    screenshot_path: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TestSuite:
    """Represents a test suite with aggregated results."""

    name: str
    start_time: datetime
    end_time: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration: float
    success_rate: float
    tests: list[TestResult]


class TestReporter:
    """
    Comprehensive test reporter with analytics capabilities.

    Features:
    - JSON and HTML report generation
    - Test result aggregation and analysis
    - Performance tracking and trend analysis
    - Failure pattern identification
    """

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.test_results: list[TestResult] = []
        self.test_suites: list[TestSuite] = []
        self.current_suite: TestSuite | None = None

        self.logger = logging.getLogger(self.__class__.__name__)

    def add_test_result(self, result: TestResult) -> None:
        """Add a test result to the reporter."""
        self.test_results.append(result)
        self.logger.debug("Added test result: %s - %s", result.name, result.status)

    def start_test_suite(self, suite_name: str) -> None:
        """Start a new test suite."""
        self.current_suite = TestSuite(
            name=suite_name,
            start_time=datetime.now(UTC),
            end_time=datetime.now(UTC),  # Will be updated when finished
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            total_duration=0.0,
            success_rate=0.0,
            tests=[],
        )
        self.logger.info("Started test suite: %s", suite_name)

    def generate_json_report(self, filename: str | None = None) -> str:
        """Generate JSON format report."""
        if filename is None:
            filename = f"test_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"

        report_data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": sum(
                    1 for r in self.test_results if r.status == "passed"
                ),
                "failed_tests": sum(
                    1 for r in self.test_results if r.status == "failed"
                ),
                "skipped_tests": sum(
                    1 for r in self.test_results if r.status == "skipped"
                ),
                "success_rate": self._calculate_success_rate(),
                "total_duration": sum(r.duration for r in self.test_results),
            },
            "test_results": [asdict(result) for result in self.test_results],
            "test_suites": [asdict(suite) for suite in self.test_suites],
        }

        output_path = self.output_dir / filename
        with Path.open(output_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        self.logger.info("JSON report generated: %s", output_path)
        return str(output_path)

    def generate_html_report(self, filename: str | None = None) -> str:
        """Generate HTML format report."""
        if filename is None:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"

        html_content = self._generate_html_content()

        output_path = self.output_dir / filename
        with Path.open(output_path, "w") as f:
            f.write(html_content)

        self.logger.info("HTML report generated: %s", output_path)
        return str(output_path)

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.test_results:
            return 0.0

        passed_count = sum(1 for r in self.test_results if r.status == "passed")
        return passed_count / len(self.test_results)

    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        passed_count = sum(1 for r in self.test_results if r.status == "passed")
        failed_count = sum(1 for r in self.test_results if r.status == "failed")
        success_rate = self._calculate_success_rate()
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

        return (
            """<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
        .metrics {
            display: flex; justify-content: space-around; margin: 20px 0;
        }
        .metric {
            text-align: center; padding: 15px;
            background-color: #e9e9e9; border-radius: 5px;
        }
        .passed { background-color: #d4edda; }
        .failed { background-color: #f8d7da; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .status-passed { color: green; font-weight: bold; }
        .status-failed { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Execution Report</h1>
        <p>Generated on: """
            + current_time
            + """</p>
    </div>

    <div class="metrics">
        <div class="metric passed">
            <h3>"""
            + str(passed_count)
            + """</h3>
            <p>Passed</p>
        </div>
        <div class="metric failed">
            <h3>"""
            + str(failed_count)
            + """</h3>
            <p>Failed</p>
        </div>
        <div class="metric">
            <h3>"""
            + str(len(self.test_results))
            + """</h3>
            <p>Total</p>
        </div>
        <div class="metric">
            <h3>"""
            + f"{success_rate:.1%}"
            + """</h3>
            <p>Success Rate</p>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>Browser</th>
                <th>Error Message</th>
            </tr>
        </thead>
        <tbody>
            """
            + self._generate_test_rows()
            + """
        </tbody>
    </table>
</body>
</html>"""
        )

    def _generate_test_rows(self) -> str:
        """Generate HTML table rows for test results."""
        rows = []
        for result in self.test_results:
            status_class = f"status-{result.status}"
            error_msg = (
                result.error_message[:50] + "..."
                if result.error_message and len(result.error_message) > 50
                else (result.error_message or "")
            )

            row = f"""<tr>
                <td>{result.name}</td>
                <td class="{status_class}">{result.status.upper()}</td>
                <td>{result.duration:.2f}</td>
                <td>{result.browser or "N/A"}</td>
                <td>{error_msg}</td>
            </tr>"""
            rows.append(row)

        return "\n".join(rows)


# Legacy alias for backward compatibility
AdvancedTestReporter = TestReporter
