"""
Advanced Test Reporter - Demonstrates analytics and reporting patterns.
Showcases: pandas/numpy analytics, trend analysis, multi-format export.

Architecture follows SRP:
- Result/Suite: Data classes for test results
- ReportExporter: Handles JSON/HTML/JUnit/CSV export
- TestAnalytics: Handles trend analysis and performance metrics
- AdvancedTestReporter: Coordinates the above (facade pattern)
"""

import json
import statistics
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

import numpy as np
import pandas as pd

# Import ErrorClassifier for centralized error classification
# Import is here to avoid circular imports (error_handler imports from here)
from utils.error_handler import ErrorClassifier

if TYPE_CHECKING:
    from utils.test_reporter import Result, Suite, TestTrend

# === DATA CLASSES ===


@dataclass
class Result:
    """Test result with metadata."""

    test_name: str
    status: str  # PASSED, FAILED, SKIPPED, ERROR
    duration: float
    timestamp: datetime
    environment: str
    browser: str
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    stack_trace: Optional[str] = None
    retries: int = 0
    tags: list[str] = field(default_factory=list)


@dataclass
class Suite:
    """Test suite summary."""

    suite_name: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total_duration: float = 0.0
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    environment: str = "local"
    browser: str = "chrome"


@dataclass
class TestTrend:
    """Trend data point."""

    date: str
    pass_rate: float
    total_tests: int
    avg_duration: float
    failed_tests: list[str] = field(default_factory=list)


# === REPORT EXPORTER (SRP) ===


class ReportExporter(ABC):
    """Abstract base for report exporters. Follows SRP."""

    @abstractmethod
    def export(self, data: dict[str, Any], path: Path) -> str:
        """Export report to the specified path."""


class JsonReportExporter(ReportExporter):
    """Exports reports to JSON format."""

    def export(self, data: dict[str, Any], path: Path) -> str:
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return str(path)


class JunitReportExporter(ReportExporter):
    """Exports reports to JUnit XML format."""

    def __init__(self, test_results: list[Result], suite: Suite):
        self.test_results = test_results
        self.suite = suite

    def export(self, data: dict[str, Any], path: Path) -> str:
        xml_content = self._generate_junit_xml()
        with open(path, "w") as f:
            f.write(xml_content)
        return str(path)

    def _generate_junit_xml(self) -> str:
        """Generate JUnit XML format."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append(
            f'<testsuite name="{self.suite.suite_name}" '
            f'tests="{self.suite.total_tests}" '
            f'failures="{self.suite.failed}" '
            f'errors="{self.suite.errors}" '
            f'time="{self.suite.total_duration:.2f}">'
        )
        for r in self.test_results:
            lines.append(f'  <testcase name="{r.test_name}" time="{r.duration:.2f}">')
            if r.status == "FAILED":
                lines.append(
                    f"    <failure>{r.error_message or 'Test failed'}</failure>"
                )
            elif r.status == "ERROR":
                lines.append(f"    <error>{r.error_message or 'Test error'}</error>")
            elif r.status == "SKIPPED":
                lines.append("    <skipped/>")
            lines.append("  </testcase>")
        lines.append("</testsuite>")
        return "\n".join(lines)


# === TEST ANALYTICS (SRP) ===


class TestAnalytics:
    """Handles test result analytics. Follows SRP."""

    @staticmethod
    def calculate_trend(values: list[float]) -> str:
        """Calculate trend direction from values."""
        if len(values) < 2:
            return "insufficient_data"
        recent = values[-5:]
        older = values[:-5] if len(values) > 5 else values[:1]
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        diff = avg_recent - avg_older
        if diff > 5:
            return "improving"
        if diff < -5:
            return "declining"
        return "stable"

    @staticmethod
    def calculate_stability_score(rates: list[float]) -> float:
        """Calculate stability score (0-100) based on pass rate consistency."""
        if len(rates) < 2:
            return 100.0
        variance = statistics.variance(rates)
        return round(max(0, 100 - variance), 2)

    @staticmethod
    def calculate_performance_score(durations: list[float]) -> float:
        """Calculate performance score based on duration trends."""
        if not durations:
            return 100.0
        recent = durations[-5:] if len(durations) >= 5 else durations
        avg = sum(recent) / len(recent)
        return round(max(0, 100 - (avg / 10)), 2)


# === ADVANCED TEST REPORTER ===


class AdvancedTestReporter:
    """
    Test reporting with analytics - facade coordinating specialized components.

    Coordinates:
    - JsonReportExporter: JSON export
    - JunitReportExporter: JUnit XML export
    - TestAnalytics: Trend and performance analysis
    """

    def __init__(self, reports_dir: Optional[Union[str, Path]] = None):
        self.reports_dir = (
            Path(reports_dir)
            if reports_dir
            else Path(__file__).parent.parent / "reports"
        )
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        for subdir in ["json", "html", "trends", "analytics"]:
            (self.reports_dir / subdir).mkdir(exist_ok=True)
        self.current_suite: Optional[Suite] = None
        self.test_results: list[Result] = []
        self._analytics = TestAnalytics()
        self._json_exporter = JsonReportExporter()

    def load_json_report(self, file_path: Union[str, Path]) -> None:
        """Load test results from JSON (pytest-json-report or custom format)."""
        with open(file_path) as f:
            data = json.load(f)

        tests = data.get("tests", data.get("test_results", []))
        for t in tests:
            try:
                ts = t.get(
                    "timestamp", t.get("start", datetime.now(timezone.utc).isoformat())
                )
                if isinstance(ts, str):
                    ts = datetime.fromisoformat(ts)
                self.test_results.append(
                    Result(
                        test_name=t.get(
                            "nodeid", t.get("test_name", t.get("name", "unknown"))
                        ),
                        status=t.get("outcome", t.get("status", "unknown")).upper(),
                        duration=float(t.get("duration", 0)),
                        timestamp=ts,
                        environment=t.get("environment", "unknown"),
                        browser=t.get("browser", "unknown"),
                        error_message=t.get("longrepr", t.get("error_message")),
                        stack_trace=t.get("longrepr", t.get("stack_trace")),
                        retries=int(t.get("rerun", t.get("retries", 0))),
                        tags=t.get("keywords", t.get("tags", [])),
                    )
                )
            except Exception:
                continue

    def start_test_suite(
        self, suite_name: str, environment: str = "local", browser: str = "chrome"
    ) -> None:
        """Start tracking a new test suite."""
        self.current_suite = Suite(
            suite_name=suite_name, environment=environment, browser=browser
        )
        self.test_results.clear()

    def add_test_result(self, result: Result) -> None:
        """Add a test result to the current suite."""
        if not self.current_suite:
            raise ValueError("No active test suite. Call start_test_suite() first.")
        self.test_results.append(result)
        self.current_suite.total_tests += 1
        self.current_suite.total_duration += result.duration
        status_map = {
            "PASSED": "passed",
            "FAILED": "failed",
            "SKIPPED": "skipped",
            "ERROR": "errors",
        }
        if result.status in status_map:
            setattr(
                self.current_suite,
                status_map[result.status],
                getattr(self.current_suite, status_map[result.status]) + 1,
            )

    def end_test_suite(self) -> Suite:
        """End the current test suite and return summary."""
        if not self.current_suite:
            raise ValueError("No active test suite.")
        self.current_suite.end_time = datetime.now(timezone.utc)
        return self.current_suite

    def _get_metrics(self) -> tuple[float, float]:
        """Calculate pass rate and average duration."""
        if not self.current_suite or self.current_suite.total_tests == 0:
            return 0.0, 0.0
        rate = self.current_suite.passed / self.current_suite.total_tests * 100
        avg = self.current_suite.total_duration / self.current_suite.total_tests
        return round(rate, 2), round(avg, 2)

    def generate_json_report(self, filename: Optional[str] = None) -> str:
        """Generate comprehensive JSON report."""
        if not self.current_suite:
            raise ValueError("No test suite data available.")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / "json" / (filename or f"test_report_{ts}.json")
        rate, avg = self._get_metrics()
        data = {
            "suite_summary": asdict(self.current_suite),
            "metrics": {
                "pass_rate": rate,
                "failure_rate": round(100 - rate, 2),
                "avg_duration": avg,
                "total_time": round(self.current_suite.total_duration, 2),
            },
            "test_results": [asdict(r) for r in self.test_results],
            "failure_analysis": self._analyze_failures(),
            "performance_analysis": self._analyze_performance(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return str(path)

    def generate_html_report(self, filename: Optional[str] = None) -> str:
        """Generate interactive HTML report."""
        if not self.current_suite:
            raise ValueError("No test suite data available.")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / "html" / (filename or f"test_report_{ts}.html")
        rate, _ = self._get_metrics()
        with open(path, "w") as f:
            f.write(self._generate_html_template(rate))
        return str(path)

    def generate_trend_analysis(self, days: int = 30) -> dict[str, Any]:
        """Generate trend analysis for the specified period."""
        trends = self._load_historical_data(days)
        if not trends:
            return {"message": "No historical data available"}
        rates = [t.pass_rate for t in trends]
        durs = [t.avg_duration for t in trends]
        analysis = {
            "period_days": days,
            "total_executions": len(trends),
            "average_pass_rate": round(statistics.mean(rates), 2),
            "pass_rate_trend": self._analytics.calculate_trend(rates),
            "duration_trend": self._analytics.calculate_trend(durs),
            "most_common_failures": self._get_common_failures(trends),
            "stability_score": self._analytics.calculate_stability_score(rates),
            "performance_score": self._analytics.calculate_performance_score(durs),
            "recommendations": self._generate_recommendations(trends),
        }
        path = (
            self.reports_dir
            / "trends"
            / f"trend_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
        )
        with open(path, "w") as f:
            json.dump(analysis, f, indent=2, default=str)
        return analysis

    def generate_analytics_dashboard(self) -> str:
        """Generate analytics dashboard with charts."""
        path = self.reports_dir / "analytics" / "dashboard.html"
        with open(path, "w") as f:
            f.write(self._generate_dashboard_template(self.generate_trend_analysis()))
        return str(path)

    def export_to_junit(self, filename: Optional[str] = None) -> str:
        """Export results to JUnit XML format for CI/CD."""
        if not self.current_suite:
            raise ValueError("No test suite data available.")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.reports_dir / "xml" / (filename or f"junit_{ts}.xml")
        path.parent.mkdir(exist_ok=True)
        exporter = JunitReportExporter(self.test_results, self.current_suite)
        return exporter.export({}, path)

    def get_failure_patterns(self) -> dict[str, Any]:
        """Analyze failure patterns and provide insights."""
        failed = [r for r in self.test_results if r.status in ["FAILED", "ERROR"]]
        if not failed:
            return {"message": "No failures to analyze"}

        patterns = Counter()
        classifier = ErrorClassifier()

        for t in failed:
            if not t.error_message:
                continue
            # Use centralized error classification
            classification = classifier.classify_error(Exception(t.error_message))
            error_category = classification["classification"]["category"]
            patterns[error_category] += 1

        return {
            "total_failures": len(failed),
            "error_patterns": dict(patterns),
            "most_failing_tests": [
                t for t, _ in Counter([t.test_name for t in failed]).most_common(5)
            ],
            "failure_rate_by_browser": dict(Counter([t.browser for t in failed])),
        }

    def _analyze_failures(self) -> dict[str, Any]:
        """Analyze failure patterns in current results."""
        failed = [r for r in self.test_results if r.status in ["FAILED", "ERROR"]]
        if not failed:
            return {"total_failures": 0}
        return {
            "total_failures": len(failed),
            "failed_tests": [t.test_name for t in failed],
            "distribution": dict(Counter([t.test_name for t in failed])),
        }

    def _analyze_performance(self) -> dict[str, Any]:
        """Analyze performance metrics."""
        durs = [r.duration for r in self.test_results]
        if not durs:
            return {"message": "No data"}
        return {
            "avg": round(statistics.mean(durs), 2),
            "median": round(statistics.median(durs), 2),
            "min": min(durs),
            "max": max(durs),
            "std": round(statistics.stdev(durs) if len(durs) > 1 else 0, 2),
            "distribution": {
                "fast": sum(1 for d in durs if d < 5),
                "medium": sum(1 for d in durs if 5 <= d < 15),
                "slow": sum(1 for d in durs if d >= 15),
            },
        }

    def _load_historical_data(self, _days: int) -> list[TestTrend]:
        """Load historical data (placeholder)."""
        return []

    def _calculate_trend(self, values: list[float]) -> str:
        """Calculate trend direction."""
        if len(values) < 2:
            return "stable"
        mid = len(values) // 2
        avg1, avg2 = statistics.mean(values[:mid]), statistics.mean(values[mid:])
        if avg2 > avg1 * 1.05:
            return "improving"
        if avg2 < avg1 * 0.95:
            return "declining"
        return "stable"

    def _calculate_stability_score(self, rates: list[float]) -> float:
        """Calculate stability score."""
        if not rates:
            return 0.0
        avg = statistics.mean(rates)
        std = statistics.stdev(rates) if len(rates) > 1 else 0
        return round((avg / 100) * (1 - min(std / 100, 1)) * 100, 2)

    def _calculate_performance_score(self, durs: list[float]) -> float:
        """Calculate performance score."""
        if not durs:
            return 0.0
        return round(max(0, 100 - (statistics.mean(durs) / 30 * 100)), 2)

    def _generate_recommendations(self, trends: list[TestTrend]) -> list[str]:
        """Generate recommendations based on trends."""
        if not trends:
            return ["Collect more data"]
        recs = []
        rates = [t.pass_rate for t in trends[-7:]]
        durs = [t.avg_duration for t in trends[-7:]]
        avg_rate, avg_dur = statistics.mean(rates), statistics.mean(durs)
        if avg_rate < 80:
            recs.append("Focus on stability - pass rate below 80%")
        if avg_rate < 90:
            recs.append("Review frequently failing tests")
        if avg_dur > 15:
            recs.append("Optimize execution time")
        if avg_dur > 30:
            recs.append("Consider parallelization")
        return recs

    def _get_common_failures(self, trends: list[TestTrend]) -> list[str]:
        """Get most common failing tests."""
        all_fails = [t for trend in trends for t in trend.failed_tests]
        return [t for t, _ in Counter(all_fails).most_common(5)]

    def _get_most_failing_tests(self, failed: list[Result]) -> list[str]:
        return [t for t, _ in Counter([r.test_name for r in failed]).most_common(5)]

    def _analyze_failures_by_browser(self, failed: list[Result]) -> dict[str, int]:
        return dict(Counter([t.browser for t in failed]))

    def _get_failure_recommendations(self, patterns: Counter) -> list[str]:
        recs = []
        if patterns.get("timeout", 0) > 2:
            recs.append("Increase timeouts or optimize page loads")
        if patterns.get("element_not_found", 0) > 2:
            recs.append("Review locators and add explicit waits")
        if patterns.get("connection", 0) > 2:
            recs.append("Check network and server stability")
        return recs

    # === HTML TEMPLATES (kept minimal for showcase) ===

    def _generate_html_template(self, pass_rate: float) -> str:
        """Generate HTML report template."""
        rows = "".join(
            f"<tr><td>{r.test_name}</td><td class='status-{r.status.lower()}'>{r.status}</td>"
            f"<td>{r.duration:.2f}s</td><td>{r.error_message or ''}</td></tr>"
            for r in self.test_results
        )
        return f"""<!DOCTYPE html><html><head><title>Test Execution Report</title>
<style>body{{font-family:Arial;margin:20px}}.header{{background:#f4f4f4;padding:20px;border-radius:5px}}
.metrics{{display:flex;justify-content:space-around;margin:20px 0}}.metric{{text-align:center;padding:15px;background:#e9e9e9;border-radius:5px}}
.passed{{background:#d4edda}}.failed{{background:#f8d7da}}table{{width:100%;border-collapse:collapse}}
th,td{{border:1px solid #ddd;padding:8px}}.status-passed{{color:green;font-weight:bold}}.status-failed{{color:red;font-weight:bold}}</style></head>
<body><div class="header"><h1>Test Execution Report</h1><p>Suite: {self.current_suite.suite_name}</p>
<p>Env: {self.current_suite.environment} | Browser: {self.current_suite.browser}</p></div>
<div class="metrics"><div class="metric passed"><h3>Passed</h3><p>{self.current_suite.passed}</p></div>
<div class="metric failed"><h3>Failed</h3><p>{self.current_suite.failed}</p></div>
<div class="metric"><h3>Rate</h3><p>{pass_rate:.1f}%</p></div></div>
<h2>Results</h2><table><tr><th>Test</th><th>Status</th><th>Duration</th><th>Error</th></tr>{rows}</table></body></html>"""

    def _generate_dashboard_template(self, data: dict[str, Any]) -> str:
        """Generate dashboard template."""
        recs = "".join(f"<li>{r}</li>" for r in data.get("recommendations", []))
        fails = "".join(f"<li>{f}</li>" for f in data.get("most_common_failures", []))
        return f"""<!DOCTYPE html><html><head><title>Dashboard</title>
<style>body{{font-family:Arial;margin:20px}}.dashboard{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
.widget{{background:#f9f9f9;padding:20px;border-radius:5px}}</style></head>
<body><h1>Analytics Dashboard</h1><div class="dashboard">
<div class="widget"><h2>Metrics</h2><p>Pass Rate: {data.get("average_pass_rate", "N/A")}%</p>
<p>Stability: {data.get("stability_score", "N/A")}</p></div>
<div class="widget"><h2>Trends</h2><p>Rate: {data.get("pass_rate_trend", "N/A")}</p>
<p>Duration: {data.get("duration_trend", "N/A")}</p></div>
<div class="widget"><h2>Recommendations</h2><ul>{recs}</ul></div>
<div class="widget"><h2>Common Failures</h2><ul>{fails}</ul></div></div></body></html>"""

    # === PANDAS/NUMPY ANALYTICS (Showcase Section) ===

    def generate_dataframe_analytics(self) -> Optional[dict[str, Any]]:
        """Generate DataFrame analytics - demonstrates pandas/numpy integration."""
        if not self.test_results:
            return None
        data = [
            {
                "test_name": r.test_name,
                "status": r.status,
                "duration": r.duration,
                "timestamp": r.timestamp,
                "browser": r.browser,
                "environment": r.environment,
                "error_type": r.error_message or "none",
                "day_of_week": r.timestamp.strftime("%A"),
                "hour": r.timestamp.hour,
            }
            for r in self.test_results
        ]
        df = pd.DataFrame(data)
        # Add computed columns using numpy
        std = df["duration"].std()
        df["duration_zscore"] = (
            np.abs((df["duration"] - df["duration"].mean()) / std) if std > 0 else 0
        )
        df["is_outlier"] = df["duration_zscore"] > 2
        df["success"] = df["status"].str.upper() == "PASSED"
        return df.to_dict("records")

    def get_performance_insights(self) -> dict[str, Any]:
        """Generate performance insights using pandas."""
        data = self.generate_dataframe_analytics()
        if not data:
            return {"insights": "No data"}
        df = pd.DataFrame(data)
        return {
            "execution_stats": {
                "avg": float(df["duration"].mean()),
                "median": float(df["duration"].median()),
                "std": float(df["duration"].std()),
                "slowest": df.nlargest(3, "duration")[
                    ["test_name", "duration"]
                ].to_dict("records"),
            },
            "success_patterns": {
                "rate": float(df["success"].mean()),
                "by_browser": df.groupby("browser")["success"].mean().to_dict(),
                "by_hour": df.groupby("hour")["success"].mean().to_dict(),
            },
            "anomalies": {
                "outliers": int(df["is_outlier"].sum()),
                "tests": df[df["is_outlier"]]["test_name"].tolist(),
            },
        }

    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """Export to CSV using pandas."""
        data = self.generate_dataframe_analytics()
        if not data:
            return "No data"
        df = pd.DataFrame(data)
        path = self.reports_dir / (
            filename
            or f"results_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        )
        df.to_csv(path, index=False)
        return str(path)


# Global instance
test_reporter = AdvancedTestReporter()
