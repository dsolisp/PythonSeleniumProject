"""
Advanced Test Reporter
Comprehensive test reporting with analytics and trend analysis capabilities.
Integrates pandas for data analysis and numpy for statistical computations.
"""

import json
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from jinja2 import Template


@dataclass
class Result:
    """Detailed test result with comprehensive metadata."""

    test_name: str
    status: str  # PASSED, FAILED, SKIPPED, ERROR
    duration: float
    timestamp: datetime
    environment: str
    browser: str
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, float]] = None
    retries: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class Suite:
    """Test suite execution summary."""

    suite_name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    total_duration: float
    start_time: datetime
    end_time: datetime
    environment: str
    browser: str


@dataclass
class TestTrend:
    """Test execution trend data."""

    date: str
    pass_rate: float
    total_tests: int
    avg_duration: float
    failed_tests: List[str]


class AdvancedTestReporter:
    """
    Advanced test reporting system with analytics and insights.

    Features:
    - Detailed test result tracking
    - Performance metrics collection
    - Trend analysis and reporting
    - Failure pattern detection
    - Custom dashboard generation
    - Integration with external tools
    """

    def __init__(self, reports_dir: Union[str, Path] = None):
        """Initialize the advanced test reporter."""
        self.reports_dir = (
            Path(reports_dir)
            if reports_dir
            else Path(__file__).parent.parent / "reports"
        )
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.reports_dir / "json").mkdir(exist_ok=True)
        (self.reports_dir / "html").mkdir(exist_ok=True)
        (self.reports_dir / "trends").mkdir(exist_ok=True)
        (self.reports_dir / "analytics").mkdir(exist_ok=True)

        self.current_suite: Optional[Suite] = None
        self.test_results: List[Result] = []

    def start_test_suite(
        self,
        suite_name: str,
        environment: str = "local",
        browser: str = "chrome",
    ) -> None:
        """Start tracking a new test suite."""
        self.current_suite = Suite(
            suite_name=suite_name,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            total_duration=0.0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            environment=environment,
            browser=browser,
        )
        self.test_results.clear()

    def add_test_result(self, result: Result) -> None:
        """Add a test result to the current suite."""
        if not self.current_suite:
            raise ValueError("No active test suite. Call start_test_suite() first.")

        self.test_results.append(result)
        self.current_suite.total_tests += 1
        self.current_suite.total_duration += result.duration

        # Update counters
        if result.status == "PASSED":
            self.current_suite.passed += 1
        elif result.status == "FAILED":
            self.current_suite.failed += 1
        elif result.status == "SKIPPED":
            self.current_suite.skipped += 1
        elif result.status == "ERROR":
            self.current_suite.errors += 1

    def end_test_suite(self) -> Suite:
        """End the current test suite and return summary."""
        if not self.current_suite:
            raise ValueError("No active test suite.")

        self.current_suite.end_time = datetime.now()
        return self.current_suite

    def generate_json_report(self, filename: str = None) -> str:
        """
        Generate comprehensive JSON report.

        Args:
            filename: Custom filename (optional)

        Returns:
            Path to generated report file
        """
        if not self.current_suite:
            raise ValueError("No test suite data available.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"test_report_{timestamp}.json"
        file_path = self.reports_dir / "json" / filename

        # Calculate additional metrics
        pass_rate = (
            (self.current_suite.passed / self.current_suite.total_tests * 100)
            if self.current_suite.total_tests > 0
            else 0
        )
        avg_duration = (
            self.current_suite.total_duration / self.current_suite.total_tests
            if self.current_suite.total_tests > 0
            else 0
        )

        report_data = {
            "suite_summary": asdict(self.current_suite),
            "metrics": {
                "pass_rate": round(pass_rate, 2),
                "failure_rate": round(100 - pass_rate, 2),
                "average_test_duration": round(avg_duration, 2),
                "total_execution_time": round(self.current_suite.total_duration, 2),
            },
            "test_results": [asdict(result) for result in self.test_results],
            "failure_analysis": self._analyze_failures(),
            "performance_analysis": self._analyze_performance(),
            "generated_at": datetime.now().isoformat(),
        }

        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        return str(file_path)

    def generate_html_report(self, filename: str = None) -> str:
        """
        Generate interactive HTML report.

        Args:
            filename: Custom filename (optional)

        Returns:
            Path to generated HTML report
        """
        if not self.current_suite:
            raise ValueError("No test suite data available.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"test_report_{timestamp}.html"
        file_path = self.reports_dir / "html" / filename

        # Calculate metrics
        pass_rate = (
            (self.current_suite.passed / self.current_suite.total_tests * 100)
            if self.current_suite.total_tests > 0
            else 0
        )

        html_content = self._generate_html_template(pass_rate)

        with open(file_path, "w") as f:
            f.write(html_content)

        return str(file_path)

    def generate_trend_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Generate trend analysis for the specified period.

        Args:
            days: Number of days to analyze (default: 30)

        Returns:
            Dictionary containing trend analysis data
        """
        trends = self._load_historical_data(days)

        if not trends:
            return {"message": "No historical data available"}

        # Calculate trend metrics
        pass_rates = [t.pass_rate for t in trends]
        durations = [t.avg_duration for t in trends]

        analysis = {
            "period_days": days,
            "total_executions": len(trends),
            "average_pass_rate": round(statistics.mean(pass_rates), 2),
            "pass_rate_trend": self._calculate_trend(pass_rates),
            "duration_trend": self._calculate_trend(durations),
            "most_common_failures": self._get_common_failures(trends),
            "stability_score": self._calculate_stability_score(pass_rates),
            "performance_score": self._calculate_performance_score(durations),
            "recommendations": self._generate_recommendations(trends),
        }

        # Save trend analysis
        trend_file = (
            self.reports_dir
            / "trends"
            / f"trend_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(trend_file, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        return analysis

    def generate_analytics_dashboard(self) -> str:
        """
        Generate analytics dashboard with charts and insights.

        Returns:
            Path to generated dashboard HTML file
        """
        dashboard_path = self.reports_dir / "analytics" / "dashboard.html"

        # Get trend data
        trend_data = self.generate_trend_analysis()

        # Generate dashboard HTML with charts
        dashboard_html = self._generate_dashboard_template(trend_data)

        with open(dashboard_path, "w") as f:
            f.write(dashboard_html)

        return str(dashboard_path)

    def export_to_junit(self, filename: str = None) -> str:
        """
        Export results to JUnit XML format for CI/CD integration.

        Args:
            filename: Custom filename (optional)

        Returns:
            Path to generated JUnit XML file
        """
        if not self.current_suite:
            raise ValueError("No test suite data available.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"junit_report_{timestamp}.xml"
        file_path = self.reports_dir / "xml" / filename

        # Create XML directory if it doesn't exist
        file_path.parent.mkdir(exist_ok=True)

        junit_xml = self._generate_junit_xml()

        with open(file_path, "w") as f:
            f.write(junit_xml)

        return str(file_path)

    def get_failure_patterns(self) -> Dict[str, Any]:
        """
        Analyze failure patterns and provide insights.

        Returns:
            Dictionary containing failure pattern analysis
        """
        failed_tests = [r for r in self.test_results if r.status in ["FAILED", "ERROR"]]

        if not failed_tests:
            return {"message": "No failures to analyze"}

        # Analyze error patterns
        error_messages = [t.error_message for t in failed_tests if t.error_message]
        error_patterns = Counter()

        for error in error_messages:
            # Extract key error patterns
            if "timeout" in error.lower():
                error_patterns["timeout_errors"] += 1
            elif "element not found" in error.lower():
                error_patterns["element_not_found"] += 1
            elif "connection" in error.lower():
                error_patterns["connection_errors"] += 1
            elif "permission" in error.lower():
                error_patterns["permission_errors"] += 1
            else:
                error_patterns["other_errors"] += 1

        return {
            "total_failures": len(failed_tests),
            "error_patterns": dict(error_patterns),
            "most_failing_tests": self._get_most_failing_tests(failed_tests),
            "failure_rate_by_browser": self._analyze_failures_by_browser(failed_tests),
            "recommendations": self._get_failure_recommendations(error_patterns),
        }

    def _analyze_failures(self) -> Dict[str, Any]:
        """Analyze failure patterns in current results."""
        failed_tests = [r for r in self.test_results if r.status in ["FAILED", "ERROR"]]

        if not failed_tests:
            return {"total_failures": 0}

        return {
            "total_failures": len(failed_tests),
            "failed_test_names": [t.test_name for t in failed_tests],
            "common_errors": self._extract_common_errors(failed_tests),
            "failure_distribution": self._get_failure_distribution(failed_tests),
        }

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics from current results."""
        durations = [r.duration for r in self.test_results]

        if not durations:
            return {"message": "No performance data available"}

        return {
            "average_duration": round(statistics.mean(durations), 2),
            "median_duration": round(statistics.median(durations), 2),
            "fastest_test": min(durations),
            "slowest_test": max(durations),
            "duration_std_dev": round(
                statistics.stdev(durations) if len(durations) > 1 else 0, 2
            ),
            "performance_distribution": self._get_performance_distribution(durations),
        }

    def _extract_common_errors(self, failed_tests: List[Result]) -> List[str]:
        """Extract common error patterns from failed tests."""
        error_messages = [t.error_message for t in failed_tests if t.error_message]

        # Simple pattern extraction
        common_patterns = []
        for error in error_messages:
            if "timeout" in error.lower():
                common_patterns.append("Timeout errors")
            elif "element" in error.lower():
                common_patterns.append("Element interaction errors")
            elif "connection" in error.lower():
                common_patterns.append("Connection errors")

        return list(set(common_patterns))

    def _get_failure_distribution(self, failed_tests: List[Result]) -> Dict[str, int]:
        """Get distribution of failures by test name."""
        return dict(Counter([t.test_name for t in failed_tests]))

    def _get_performance_distribution(self, durations: List[float]) -> Dict[str, int]:
        """Get performance distribution categorization."""
        fast = sum(1 for d in durations if d < 5)
        medium = sum(1 for d in durations if 5 <= d < 15)
        slow = sum(1 for d in durations if d >= 15)

        return {"fast_tests": fast, "medium_tests": medium, "slow_tests": slow}

    def _load_historical_data(self, days: int) -> List[TestTrend]:
        """Load historical test data for trend analysis."""
        # Placeholder for loading historical data
        # In real implementation, this would load from database or files
        return []

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "stable"

        # Simple linear trend calculation
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        if avg_second > avg_first * 1.05:
            return "improving"
        elif avg_second < avg_first * 0.95:
            return "declining"
        else:
            return "stable"

    def _calculate_stability_score(self, pass_rates: List[float]) -> float:
        """Calculate stability score based on pass rate consistency."""
        if not pass_rates:
            return 0.0

        avg_rate = statistics.mean(pass_rates)
        std_dev = statistics.stdev(pass_rates) if len(pass_rates) > 1 else 0

        # Higher average and lower standard deviation = higher stability
        stability = (avg_rate / 100) * (1 - min(std_dev / 100, 1))
        return round(stability * 100, 2)

    def _calculate_performance_score(self, durations: List[float]) -> float:
        """Calculate performance score based on execution times."""
        if not durations:
            return 0.0

        avg_duration = statistics.mean(durations)
        # Score based on how fast tests execute (lower duration = higher score)
        # Normalize to 0-100 scale assuming 30s is baseline
        score = max(0, 100 - (avg_duration / 30 * 100))
        return round(score, 2)

    def _generate_recommendations(self, trends: List[TestTrend]) -> List[str]:
        """Generate actionable recommendations based on trends."""
        recommendations = []

        if not trends:
            return ["Collect more test execution data for better insights"]

        # Analyze pass rates
        # Last 7 executions
        recent_pass_rates = [t.pass_rate for t in trends[-7:]]
        avg_pass_rate = statistics.mean(recent_pass_rates)

        if avg_pass_rate < 80:
            recommendations.append("Focus on test stability - pass rate below 80%")
        if avg_pass_rate < 90:
            recommendations.append("Review and fix frequently failing tests")

        # Analyze duration trends
        recent_durations = [t.avg_duration for t in trends[-7:]]
        avg_duration = statistics.mean(recent_durations)

        if avg_duration > 15:
            recommendations.append(
                "Optimize test execution time - average duration > 15s"
            )
        if avg_duration > 30:
            recommendations.append("Consider parallelization for faster execution")

        return recommendations

    def _get_common_failures(self, trends: List[TestTrend]) -> List[str]:
        """Get most common failing tests across trends."""
        all_failures = []
        for trend in trends:
            all_failures.extend(trend.failed_tests)

        return [test for test, count in Counter(all_failures).most_common(5)]

    def _get_most_failing_tests(self, failed_tests: List[Result]) -> List[str]:
        """Get tests that fail most frequently."""
        return [
            test
            for test, count in Counter([t.test_name for t in failed_tests]).most_common(
                5
            )
        ]

    def _analyze_failures_by_browser(
        self, failed_tests: List[Result]
    ) -> Dict[str, int]:
        """Analyze failure distribution by browser."""
        return dict(Counter([t.browser for t in failed_tests]))

    def _get_failure_recommendations(self, error_patterns: Counter) -> List[str]:
        """Generate recommendations based on error patterns."""
        recommendations = []

        if error_patterns.get("timeout_errors", 0) > 2:
            recommendations.append(
                "Consider increasing timeout values or optimizing page load times"
            )
        if error_patterns.get("element_not_found", 0) > 2:
            recommendations.append("Review element locators and add explicit waits")
        if error_patterns.get("connection_errors", 0) > 2:
            recommendations.append("Check network connectivity and server stability")

        return recommendations

    def _generate_html_template(self, pass_rate: float) -> str:
        """Generate HTML template for test report."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Execution Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 15px; background-color: #e9e9e9; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .test-results {{ margin-top: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-passed {{ color: green; font-weight: bold; }}
        .status-failed {{ color: red; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Execution Report</h1>
        <p>Suite: {self.current_suite.suite_name}</p>
        <p>Environment: {self.current_suite.environment}</p>
        <p>Browser: {self.current_suite.browser}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="metrics">
        <div class="metric passed">
            <h3>Passed</h3>
            <p>{self.current_suite.passed}</p>
        </div>
        <div class="metric failed">
            <h3>Failed</h3>
            <p>{self.current_suite.failed}</p>
        </div>
        <div class="metric">
            <h3>Pass Rate</h3>
            <p>{pass_rate:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Duration</h3>
            <p>{self.current_suite.total_duration:.2f}s</p>
        </div>
    </div>
    
    <div class="test-results">
        <h2>Test Results</h2>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Error Message</th>
            </tr>
            {''.join([
            f'<tr><td>{r.test_name}</td>'
            f'<td class="status-{r.status.lower()}">{r.status}</td>'
            f'<td>{r.duration:.2f}s</td>'
            f'<td>{r.error_message or ""}</td></tr>'
            for r in self.test_results
        ])}
        </table>
    </div>
</body>
</html>
        """

    def _generate_dashboard_template(self, trend_data: Dict[str, Any]) -> str:
        """Generate dashboard HTML template with analytics."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .widget {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
        .metric {{ text-align: center; margin: 10px 0; }}
        .metric h3 {{ margin: 5px 0; color: #333; }}
        .metric p {{ font-size: 24px; font-weight: bold; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>Test Analytics Dashboard</h1>
    
    <div class="dashboard">
        <div class="widget">
            <h2>Current Metrics</h2>
            <div class="metric">
                <h3>Average Pass Rate</h3>
                <p>{trend_data.get('average_pass_rate', 'N/A')}%</p>
            </div>
            <div class="metric">
                <h3>Stability Score</h3>
                <p>{trend_data.get('stability_score', 'N/A')}</p>
            </div>
        </div>
        
        <div class="widget">
            <h2>Trends</h2>
            <p>Pass Rate Trend: {trend_data.get('pass_rate_trend', 'N/A')}</p>
            <p>Duration Trend: {trend_data.get('duration_trend', 'N/A')}</p>
        </div>
        
        <div class="widget">
            <h2>Recommendations</h2>
            <ul>
                {''.join([f'<li>{rec}</li>' for rec in trend_data.get('recommendations', [])])}
            </ul>
        </div>
        
        <div class="widget">
            <h2>Common Failures</h2>
            <ul>
                {''.join([
            f'<li>{failure}</li>'
            for failure in trend_data.get('most_common_failures', [])
        ])}
            </ul>
        </div>
    </div>
</body>
</html>
        """

    def _generate_junit_xml(self) -> str:
        """Generate JUnit XML format report."""
        self.current_suite.total_duration
        test_cases = []

        for result in self.test_results:
            case_xml = (
                f'    <testcase name="{result.test_name}" ' f'time="{result.duration}"'
            )

            if result.status == "FAILED":
                err_msg = result.error_message or "Test failed"
                stack = result.stack_trace or ""
                case_xml += (
                    f'>\n      <failure message="{err_msg}">'
                    f"{stack}</failure>\n    </testcase>"
                )
            elif result.status == "ERROR":
                err_msg = result.error_message or "Test error"
                stack = result.stack_trace or ""
                case_xml += (
                    f'>\n      <error message="{err_msg}">'
                    f"{stack}</error>\n    </testcase>"
                )
            elif result.status == "SKIPPED":
                case_xml += ">\n      <skipped/>\n    </testcase>"
            else:
                case_xml += "/>"

            test_cases.append(case_xml)

    def generate_dataframe_analytics(self) -> Optional[Dict[str, Any]]:
        """
        Generate pandas DataFrame for advanced analytics.
        Leverages pandas for statistical analysis and numpy for computations.
        """
        if not self.test_results:
            return None

        # Convert test results to structured data
        data = []
        for result in self.test_results:
            data.append(
                {
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": result.duration,
                    "timestamp": result.timestamp,
                    "browser": result.browser,
                    "environment": result.environment,
                    "error_type": result.error_message or "none",
                    "day_of_week": result.timestamp.strftime("%A"),
                    "hour": result.timestamp.hour,
                }
            )

        df = pd.DataFrame(data)

        # Add computed columns using numpy
        df["duration_zscore"] = np.abs(
            (df["duration"] - df["duration"].mean()) / df["duration"].std()
        )
        df["is_outlier"] = df["duration_zscore"] > 2
        df["success"] = df["status"] == "passed"

        return df.to_dict("records")  # Return as dict for serialization

    def get_performance_insights(self) -> Dict[str, Any]:
        """
        Generate performance insights using pandas analytics.
        """
        df_data = self.generate_dataframe_analytics()
        if df_data is None or not df_data:
            return {"insights": "No data available for analysis"}

        # Create DataFrame from data
        df = pd.DataFrame(df_data)

        insights = {
            "execution_stats": {
                "avg_duration": float(df["duration"].mean()),
                "median_duration": float(df["duration"].median()),
                "std_duration": float(df["duration"].std()),
                "slowest_tests": df.nlargest(3, "duration")[
                    ["test_name", "duration"]
                ].to_dict("records"),
            },
            "success_patterns": {
                "overall_success_rate": float(df["success"].mean()),
                "success_by_browser": df.groupby("browser")["success"].mean().to_dict(),
                "success_by_hour": df.groupby("hour")["success"].mean().to_dict(),
                "success_by_day": df.groupby("day_of_week")["success"].mean().to_dict(),
            },
            "anomaly_detection": {
                "performance_outliers": int(df["is_outlier"].sum()),
                "outlier_tests": df[df["is_outlier"]]["test_name"].tolist(),
            },
        }

        return insights

    def export_to_csv(self, filename: str = None) -> str:
        """
        Export test results to CSV using pandas for efficient processing.
        """
        df_data = self.generate_dataframe_analytics()
        if df_data is None:
            return "No data to export"

        df = pd.DataFrame(df_data)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.csv"

        filepath = self.reports_dir / filename
        df.to_csv(filepath, index=False)
        return str(filepath)


# Global reporter instance
test_reporter = AdvancedTestReporter()
