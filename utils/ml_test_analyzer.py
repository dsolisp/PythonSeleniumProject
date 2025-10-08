"""
ML-Powered Test Intelligence Analyzer

Analyzes historical test results to:
- Predict test failures
- Detect flaky tests
- Identify performance anomalies
- Optimize test execution order
"""

import json
import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from utils.structured_logger import get_logger

# Suppress only sklearn UndefinedMetricWarning for cleaner output
# Initialize logger
logger = get_logger("MLTestAnalyzer")


class MLTestAnalyzer:
    """Analyzes test results using machine learning techniques."""

    def __init__(self, results_dir: str = "data/results"):
        """
        Initialize the analyzer.

        Args:
            results_dir: Path to test results directory
        """
        self.results_dir = Path(results_dir)
        self.df = None
        self.model = None
        self.label_encoders = {}

    def load_historical_data(self) -> pd.DataFrame:
        """
        Load all historical test results from JSON files.

        Returns:
            DataFrame with test execution history
        """
        print("📂 Loading historical test results...")

        results = []
        json_files = list(self.results_dir.rglob("*.json"))

        if not json_files:
            print("⚠️  No test result files found in data/results/")
            return pd.DataFrame()

        for json_file in json_files:
            try:
                with open(json_file) as f:
                    data = json.load(f)

                    # Extract test details if available
                    if "results" in data:
                        results_data = data["results"]
                        if isinstance(results_data, dict) and "tests" in results_data:
                            for test in results_data["tests"]:
                                test_record = {
                                    "test_name": test.get("name", "unknown"),
                                    "status": test.get("status", "unknown"),
                                    "duration": test.get("duration", 0),
                                    "environment": data.get("environment", "unknown"),
                                    "timestamp": data.get("timestamp", "unknown"),
                                    "browser": results_data.get("browser", "unknown"),
                                    "headless": results_data.get("headless", False),
                                }
                                results.append(test_record)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"⚠️  Skipping {json_file.name}: {e}")
                continue

        if not results:
            print("⚠️  No valid test data found in JSON files")
            return pd.DataFrame()

        self.df = pd.DataFrame(results)
        print(f"✅ Loaded {len(self.df)} test records from {len(json_files)} files")

        return self.df

    def detect_flaky_tests(self, min_runs: int = 3) -> pd.DataFrame:
        """
        Identify tests that fail inconsistently (flaky tests).

        Args:
            min_runs: Minimum number of runs to consider

        Returns:
            DataFrame with flaky test analysis
        """
        print("\n🔍 Detecting flaky tests...")

        if self.df is None or self.df.empty:
            print("⚠️  No data loaded. Run load_historical_data() first.")
            return pd.DataFrame()

        # Group by test name and calculate pass rate
        flaky_analysis = (
            self.df.groupby("test_name")
            .agg(
                {
                    "status": ["count", lambda x: (x == "passed").sum()],
                    "duration": "mean",
                }
            )
            .reset_index()
        )

        flaky_analysis.columns = [
            "test_name",
            "total_runs",
            "passed_runs",
            "avg_duration",
        ]
        flaky_analysis["pass_rate"] = (
            flaky_analysis["passed_runs"] / flaky_analysis["total_runs"]
        )
        flaky_analysis["failed_runs"] = (
            flaky_analysis["total_runs"] - flaky_analysis["passed_runs"]
        )

        # Filter for flaky tests (not 0% or 100% pass rate, min runs)
        flaky_tests = flaky_analysis[
            (flaky_analysis["total_runs"] >= min_runs)
            & (flaky_analysis["pass_rate"] > 0)
            & (flaky_analysis["pass_rate"] < 1.0)
        ].sort_values("pass_rate")

        if flaky_tests.empty:
            print("✅ No flaky tests detected!")
        else:
            print(f"⚠️  Found {len(flaky_tests)} flaky tests:")
            for _, test in flaky_tests.iterrows():
                print(
                    f"   • {test['test_name']}: "
                    f"{test['pass_rate']:.1%} pass rate "
                    f"({test['passed_runs']}/{test['total_runs']} passed)"
                )

        return flaky_tests

    def analyze_performance_trends(self) -> Dict[str, Any]:
        """
        Analyze performance trends and detect anomalies.

        Returns:
            Dictionary with performance insights
        """
        print("\n📊 Analyzing performance trends...")

        if self.df is None or self.df.empty:
            print("⚠️  No data loaded. Run load_historical_data() first.")
            return {}

        # Overall statistics
        stats = {
            "avg_duration": self.df["duration"].mean(),
            "median_duration": self.df["duration"].median(),
            "std_duration": self.df["duration"].std(),
            "min_duration": self.df["duration"].min(),
            "max_duration": self.df["duration"].max(),
        }

        # Detect outliers (tests taking unusually long)
        z_scores = np.abs(
            (self.df["duration"] - stats["avg_duration"]) / stats["std_duration"]
        )
        outliers = self.df[z_scores > 2].copy()

        print("\n📈 Performance Statistics:")
        print(f"   Average duration: {stats['avg_duration']:.2f}s")
        print(f"   Median duration:  {stats['median_duration']:.2f}s")
        print(f"   Std deviation:    {stats['std_duration']:.2f}s")
        print(
            f"   Range:            {stats['min_duration']:.2f}s - "
            f"{stats['max_duration']:.2f}s"
        )

        if not outliers.empty:
            print(f"\n⚠️  Found {len(outliers)} performance outliers:")
            for _, test in outliers.nlargest(5, "duration").iterrows():
                print(
                    f"   • {test['test_name']}: {test['duration']:.2f}s "
                    f"(environment: {test['environment']})"
                )

        stats["outliers"] = outliers
        return stats

    def get_test_statistics(self) -> pd.DataFrame:
        """
        Get comprehensive statistics for all tests.

        Returns:
            DataFrame with test statistics
        """
        print("\n📋 Generating test statistics...")

        if self.df is None or self.df.empty:
            print("⚠️  No data loaded. Run load_historical_data() first.")
            return pd.DataFrame()

        stats = (
            self.df.groupby("test_name")
            .agg(
                {
                    "status": [
                        "count",
                        lambda x: (x == "passed").sum(),
                        lambda x: (x == "failed").sum(),
                    ],
                    "duration": ["mean", "min", "max", "std"],
                }
            )
            .reset_index()
        )

        stats.columns = [
            "test_name",
            "total_runs",
            "passed",
            "failed",
            "avg_duration",
            "min_duration",
            "max_duration",
            "std_duration",
        ]

        stats["pass_rate"] = stats["passed"] / stats["total_runs"]
        stats["reliability_score"] = stats["pass_rate"] * (
            1 - stats["std_duration"] / stats["avg_duration"].clip(lower=0.01)
        )

        # Sort by reliability (most reliable first)
        stats = stats.sort_values("reliability_score", ascending=False)

        print("\n🏆 Most Reliable Tests (Top 5):")
        for _, test in stats.head(5).iterrows():
            print(
                f"   • {test['test_name']}: "
                f"{test['pass_rate']:.1%} pass rate, "
                f"{test['avg_duration']:.2f}s avg"
            )

        if len(stats) > 5:
            print("\n⚠️  Least Reliable Tests (Bottom 5):")
            for _, test in stats.tail(5).iterrows():
                print(
                    f"   • {test['test_name']}: "
                    f"{test['pass_rate']:.1%} pass rate, "
                    f"{test['avg_duration']:.2f}s avg"
                )

        return stats

    def train_failure_predictor(self) -> Tuple[float, Any]:
        """
        Train ML model to predict test failures.

        Returns:
            Tuple of (accuracy, model)
        """
        print("\n🤖 Training failure prediction model...")

        if self.df is None or self.df.empty:
            print("⚠️  No data loaded. Run load_historical_data() first.")
            return 0.0, None

        # Prepare features
        df_ml = self.df.copy()

        # Encode categorical variables
        for col in ["test_name", "environment", "browser"]:
            if col in df_ml.columns:
                le = LabelEncoder()
                df_ml[f"{col}_encoded"] = le.fit_transform(df_ml[col].astype(str))
                self.label_encoders[col] = le

        # Features for prediction
        feature_cols = [col for col in df_ml.columns if col.endswith("_encoded")] + [
            "duration"
        ]
        if "headless" in df_ml.columns:
            df_ml["headless_int"] = df_ml["headless"].astype(int)
            feature_cols.append("headless_int")

        X = df_ml[feature_cols]
        y = (df_ml["status"] == "failed").astype(int)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        # Evaluate
        accuracy = self.model.score(X_test, y_test)

        print(f"✅ Model trained with {accuracy:.1%} accuracy")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Test samples: {len(X_test)}")

        # Feature importance
        feature_importance = pd.DataFrame(
            {"feature": feature_cols, "importance": self.model.feature_importances_}
        ).sort_values("importance", ascending=False)

        print("\n🎯 Most Important Features:")
        for _, row in feature_importance.head(3).iterrows():
            print(f"   • {row['feature']}: {row['importance']:.3f}")

        return accuracy, self.model

    def predict_test_failures(
        self, upcoming_tests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Predict which tests are likely to fail.

        Args:
            upcoming_tests: List of test configurations

        Returns:
            List of predictions with failure probabilities
        """
        if self.model is None:
            print("⚠️  Model not trained. Run train_failure_predictor() first.")
            return []

        print("\n🔮 Predicting test failures...")

        predictions = []

        for test in upcoming_tests:
            # Encode features
            features = {}
            for col, encoder in self.label_encoders.items():
                if col in test:
                    try:
                        features[f"{col}_encoded"] = encoder.transform([test[col]])[0]
                    except ValueError:
                        features[f"{col}_encoded"] = 0  # Unknown value

            features["duration"] = test.get("duration", self.df["duration"].mean())
            if "headless" in test:
                features["headless_int"] = int(test["headless"])

            # Predict
            X = pd.DataFrame([features])
            proba = self.model.predict_proba(X)[0]

            # Handle case where model only learned one class (all pass or all fail)
            if len(proba) == 1:
                prob = 0.0 if self.model.classes_[0] == 0 else 1.0
            else:
                prob = proba[1]  # Probability of failure

            predictions.append(
                {
                    "test_name": test.get("test_name", "unknown"),
                    "failure_probability": prob,
                    "recommendation": (
                        "High risk - run first"
                        if prob > 0.7
                        else (
                            "Medium risk - monitor"
                            if prob > 0.4
                            else "Low risk - standard execution"
                        )
                    ),
                }
            )

        # Sort by failure probability
        predictions.sort(key=lambda x: x["failure_probability"], reverse=True)

        print("\n📊 Failure Predictions (Top 5 risks):")
        for pred in predictions[:5]:
            print(
                f"   • {pred['test_name']}: "
                f"{pred['failure_probability']:.1%} failure risk - "
                f"{pred['recommendation']}"
            )

        return predictions

    def generate_report(self, output_file: str = "reports/ml_analysis_report.txt"):
        """
        Generate comprehensive analysis report.

        Args:
            output_file: Path to output report file
        """
        print("\n📝 Generating comprehensive report...")

        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("ML TEST ANALYSIS REPORT")
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("=" * 70)
        report_lines.append("")

        # Load data
        df = self.load_historical_data()

        if df.empty:
            report_lines.append("⚠️  No test data available for analysis")
        else:
            # Basic statistics
            report_lines.append("📊 Dataset Overview:")
            report_lines.append(f"   Total test executions: {len(df)}")
            report_lines.append(f"   Unique tests: {df['test_name'].nunique()}")
            report_lines.append(f"   Environments: {df['environment'].nunique()}")
            report_lines.append(
                f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}"
            )
            report_lines.append("")

            # Flaky tests
            flaky = self.detect_flaky_tests()
            if not flaky.empty:
                report_lines.append(f"⚠️  Flaky Tests Detected: {len(flaky)}")
                for _, test in flaky.iterrows():
                    test_name = test["test_name"]
                    pass_rate = test["pass_rate"]
                    report_lines.append(f"   • {test_name}: {pass_rate:.1%} pass rate")
                report_lines.append("")

            # Performance trends
            perf = self.analyze_performance_trends()
            report_lines.append("📈 Performance Summary:")
            avg_dur = perf["avg_duration"]
            med_dur = perf["median_duration"]
            report_lines.append(f"   Average duration: {avg_dur:.2f}s")
            report_lines.append(f"   Median duration: {med_dur:.2f}s")
            report_lines.append("")

            # Test statistics
            stats = self.get_test_statistics()
            report_lines.append("🏆 Test Reliability Ranking:")
            for i, (_, test) in enumerate(stats.head(10).iterrows(), start=1):
                report_lines.append(
                    f"   {i}. {test['test_name']}: "
                    f"{test['pass_rate']:.1%} pass rate, "
                    f"{test['avg_duration']:.2f}s avg"
                )
            report_lines.append("")

            # ML predictions
            accuracy, _ = self.train_failure_predictor()
            report_lines.append("🤖 ML Model Performance:")
            report_lines.append(f"   Prediction accuracy: {accuracy:.1%}")
            report_lines.append("")

        report_lines.append("=" * 70)

        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("\n".join(report_lines))

        print(f"✅ Report saved to: {output_path}")

        # Also print to console
        print("\n" + "\n".join(report_lines))


def main():
    """Main execution function."""
    print("=" * 70)
    print("ML-POWERED TEST INTELLIGENCE ANALYZER")
    print("=" * 70)

    analyzer = MLTestAnalyzer()

    # Load historical data
    df = analyzer.load_historical_data()

    if df.empty:
        print("\n⚠️  No test data found!")
        print("\nTo use this analyzer:")
        print("1. Run tests with export enabled")
        print("2. Test results will be saved to data/results/")
        print("3. Run this analyzer to get insights")
        print("\nExample:")
        print("  python examples/export_test_results_example.py")
        print("  python utils/ml_test_analyzer.py")
        return

    # Run analyses
    analyzer.detect_flaky_tests()
    analyzer.analyze_performance_trends()
    analyzer.get_test_statistics()

    # Train ML model
    analyzer.train_failure_predictor()

    # Example prediction
    upcoming_tests = [
        {
            "test_name": df["test_name"].iloc[0],
            "environment": "staging",
            "browser": "chrome",
            "duration": df["duration"].mean(),
            "headless": False,
        }
    ]
    analyzer.predict_test_failures(upcoming_tests)

    # Generate report
    analyzer.generate_report()

    print("\n" + "=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
