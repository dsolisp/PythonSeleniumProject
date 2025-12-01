"""
Test Analytics Engine - Statistical Analysis for Test Results

Analyzes historical test results using statistical methods to:
- Detect flaky tests (inconsistent pass/fail patterns)
- Identify performance anomalies (slow tests, outliers)
- Calculate test reliability scores
- Prioritize test execution based on risk

No ML dependencies - uses pandas/numpy for efficient statistical analysis.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TestStats:
    """Statistics for a single test."""

    name: str
    total_runs: int
    passed: int
    failed: int
    pass_rate: float
    avg_duration: float
    std_duration: float
    is_flaky: bool
    risk_score: float  # 0-1, higher = more risky


class TestAnalyzer:
    """Analyzes test results using statistical methods."""

    def __init__(self, results_dir: str = "data/results"):
        self.results_dir = Path(results_dir)
        self.df: Optional[pd.DataFrame] = None

    def load_results(self) -> pd.DataFrame:
        """Load test results from JSON files into DataFrame."""
        results = []
        for json_file in self.results_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                results.extend(self._parse_results(data))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Skipping {json_file.name}: {e}")

        if not results:
            logger.warning("No test results found")
            return pd.DataFrame()

        self.df = pd.DataFrame(results)
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"], errors="coerce")
        self.df["duration"] = pd.to_numeric(
            self.df["duration"], errors="coerce"
        ).fillna(0)
        logger.info(f"Loaded {len(self.df)} test records")
        return self.df

    def _parse_results(self, data: dict) -> list[dict]:
        """Parse JSON data into test records (supports multiple formats)."""
        records = []
        # Format 1: Custom framework format
        if "results" in data and "tests" in data.get("results", {}):
            for test in data["results"]["tests"]:
                records.append(
                    {
                        "test_name": test.get("name", "unknown"),
                        "status": test.get("status", "unknown"),
                        "duration": test.get("duration", 0),
                        "timestamp": data.get("timestamp"),
                        "environment": data.get("environment", "unknown"),
                    }
                )
        # Format 2: pytest-json-report format
        elif "tests" in data:
            for test in data["tests"]:
                records.append(
                    {
                        "test_name": test.get("nodeid", test.get("name", "unknown")),
                        "status": test.get("outcome", "unknown"),
                        "duration": test.get("duration", 0),
                        "timestamp": data.get("created"),
                        "environment": data.get("environment", "unknown"),
                    }
                )
        return records

    def detect_flaky_tests(self, min_runs: int = 3) -> pd.DataFrame:
        """Find tests with inconsistent pass/fail rates (0 < rate < 1)."""
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        stats = (
            self.df.groupby("test_name")
            .agg(
                total=("status", "count"),
                passed=("status", lambda x: (x == "passed").sum()),
                avg_duration=("duration", "mean"),
            )
            .reset_index()
        )

        stats["pass_rate"] = stats["passed"] / stats["total"]
        stats["is_flaky"] = (
            (stats["total"] >= min_runs)
            & (stats["pass_rate"] > 0)
            & (stats["pass_rate"] < 1)
        )

        flaky = stats[stats["is_flaky"]].sort_values("pass_rate")
        logger.info(f"Found {len(flaky)} flaky tests out of {len(stats)} unique tests")
        return flaky

    def find_slow_tests(self, std_threshold: float = 2.0) -> pd.DataFrame:
        """Find tests with duration > threshold standard deviations from mean."""
        if self.df is None or self.df.empty:
            return pd.DataFrame()

        mean_dur, std_dur = self.df["duration"].mean(), self.df["duration"].std()
        threshold = mean_dur + (std_threshold * std_dur)

        slow = self.df[self.df["duration"] > threshold].copy()
        slow["z_score"] = (slow["duration"] - mean_dur) / std_dur
        return slow.sort_values("duration", ascending=False)

    def get_reliability_scores(self) -> list[TestStats]:
        """Calculate reliability score for each test (pass_rate * consistency)."""
        if self.df is None or self.df.empty:
            return []

        stats = (
            self.df.groupby("test_name")
            .agg(
                total=("status", "count"),
                passed=("status", lambda x: (x == "passed").sum()),
                failed=("status", lambda x: (x == "failed").sum()),
                avg_dur=("duration", "mean"),
                std_dur=("duration", "std"),
            )
            .reset_index()
            .fillna(0)
        )

        results = []
        for _, row in stats.iterrows():
            pass_rate = row["passed"] / row["total"] if row["total"] > 0 else 0
            # Risk score: combines failure rate + duration variability
            duration_variance = row["std_dur"] / max(row["avg_dur"], 0.01)
            risk_score = min(1.0, (1 - pass_rate) + (duration_variance * 0.2))

            results.append(
                TestStats(
                    name=row["test_name"],
                    total_runs=int(row["total"]),
                    passed=int(row["passed"]),
                    failed=int(row["failed"]),
                    pass_rate=round(pass_rate, 3),
                    avg_duration=round(row["avg_dur"], 2),
                    std_duration=round(row["std_dur"], 2),
                    is_flaky=0 < pass_rate < 1 and row["total"] >= 3,
                    risk_score=round(risk_score, 3),
                )
            )
        return sorted(results, key=lambda x: x.risk_score, reverse=True)

    def prioritize_tests(self, test_names: list[str]) -> list[dict[str, Any]]:
        """Prioritize tests by risk score (high risk first for fast feedback)."""
        scores = {s.name: s for s in self.get_reliability_scores()}
        prioritized = []
        for name in test_names:
            stats = scores.get(name)
            prioritized.append(
                {
                    "test_name": name,
                    "risk_score": stats.risk_score if stats else 0.5,
                    "recommendation": self._get_recommendation(stats)
                    if stats
                    else "Unknown test",
                }
            )
        return sorted(prioritized, key=lambda x: x["risk_score"], reverse=True)

    def _get_recommendation(self, stats: TestStats) -> str:
        if stats.is_flaky:
            return f"⚠️ Flaky ({stats.pass_rate:.0%} pass rate) - investigate"
        if stats.risk_score > 0.5:
            return "🔴 High risk - run first"
        if stats.risk_score > 0.2:
            return "🟡 Medium risk - monitor"
        return "🟢 Low risk - stable"

    def generate_report(self) -> dict[str, Any]:
        """Generate summary report of test health."""
        if self.df is None:
            self.load_results()
        if self.df is None or self.df.empty:
            return {"error": "No data available"}

        flaky = self.detect_flaky_tests()
        slow = self.find_slow_tests()
        scores = self.get_reliability_scores()

        return {
            "summary": {
                "total_executions": len(self.df),
                "unique_tests": self.df["test_name"].nunique(),
                "overall_pass_rate": round((self.df["status"] == "passed").mean(), 3),
                "avg_duration": round(self.df["duration"].mean(), 2),
            },
            "flaky_tests": [
                {"name": r["test_name"], "pass_rate": r["pass_rate"]}
                for _, r in flaky.iterrows()
            ],
            "slow_tests": [
                {"name": r["test_name"], "duration": r["duration"]}
                for _, r in slow.head(5).iterrows()
            ],
            "high_risk_tests": [
                {"name": s.name, "risk": s.risk_score}
                for s in scores[:5]
                if s.risk_score > 0.3
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def main():
    """CLI entry point for test analysis."""
    print("=" * 60)
    print("TEST ANALYTICS ENGINE")
    print("=" * 60)

    analyzer = TestAnalyzer()
    df = analyzer.load_results()

    if df.empty:
        print("\n⚠️  No test data found in data/results/")
        print("Run tests with JSON export enabled first.")
        return

    print(f"\n📊 Loaded {len(df)} test executions")

    # Flaky tests
    flaky = analyzer.detect_flaky_tests()
    if not flaky.empty:
        print(f"\n⚠️  Flaky Tests ({len(flaky)}):")
        for _, t in flaky.head(5).iterrows():
            print(f"   • {t['test_name']}: {t['pass_rate']:.0%} pass rate")

    # Slow tests
    slow = analyzer.find_slow_tests()
    if not slow.empty:
        print(f"\n🐢 Slow Tests ({len(slow)}):")
        for _, t in slow.head(5).iterrows():
            print(f"   • {t['test_name']}: {t['duration']:.2f}s")

    # Reliability ranking
    scores = analyzer.get_reliability_scores()
    print("\n🏆 Test Reliability (Top 5 risks):")
    for s in scores[:5]:
        status = "⚠️ FLAKY" if s.is_flaky else f"Risk: {s.risk_score:.0%}"
        print(
            f"   • {s.name}: {s.pass_rate:.0%} pass, {s.avg_duration:.1f}s avg [{status}]"
        )

    print("\n" + "=" * 60)
    print("✅ Analysis complete!")


if __name__ == "__main__":
    main()
