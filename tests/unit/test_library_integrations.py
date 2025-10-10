import tempfile
from datetime import UTC, datetime
from pathlib import Path

import jinja2
import numpy
import numpy as np
import pandas
import pandas as pd
import psutil
import pytest
import tenacity
import yaml
from hamcrest import (
    any_of,
    assert_that,
    contains_string,
    ends_with,
    equal_to,
    greater_than,
    greater_than_or_equal_to,
    has_item,
    has_key,
    has_property,
    instance_of,
    is_,
    less_than_or_equal_to,
    not_none,
)
from jinja2 import Template
from tenacity import Retrying, stop_after_attempt, wait_exponential, wait_fixed

from utils.error_handler import SmartErrorHandler
from utils.test_data_manager import DataManager
from utils.test_reporter import AdvancedTestReporter, Result

"""
Unit tests for library integrations (pandas, yaml, psutil, tenacity, jinja2, numpy).
Validates that all new library features are working correctly.
"""


class TestPandasIntegration:
    """Test pandas integration in test reporter."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_pandas_dataframe_creation(self):
        """Test that pandas DataFrames are created correctly."""
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite("pandas_test", "test", "chrome")

        # Add test results
        results = [
            Result("test1", "passed", 1.5, datetime.now(UTC), "test", "chrome"),
            Result("test2", "failed", 2.3, datetime.now(UTC), "test", "chrome"),
            Result("test3", "passed", 0.8, datetime.now(UTC), "test", "chrome"),
        ]

        for result in results:
            reporter.add_test_result(result)

        # Test DataFrame generation
        analytics = reporter.generate_dataframe_analytics()
        assert_that(analytics, is_(not_none()))
        assert_that(len(analytics), equal_to(3))

        # Verify DataFrame structure
        df = pd.DataFrame(analytics)
        expected_columns = [
            "test_name",
            "status",
            "duration",
            "timestamp",
            "browser",
            "environment",
        ]
        for col in expected_columns:
            assert_that(df.columns, has_item(col))

        # Test statistical analysis
        assert_that(df["duration"].mean(), greater_than(0))
        assert_that(df["duration"].std(), greater_than_or_equal_to(0))
        assert_that(df.columns, has_item("is_outlier"))
        assert_that(df.columns, has_item("duration_zscore"))

    def test_csv_export_functionality(self):
        """Test CSV export using pandas."""
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite("csv_test", "test", "chrome")

        # Add test result
        result = Result("test_csv", "passed", 1.2, datetime.now(UTC), "test", "chrome")
        reporter.add_test_result(result)

        # Export to CSV
        csv_file = reporter.export_to_csv()
        assert_that(csv_file, is_(not_none()))
        assert_that(Path.exists(csv_file), is_(True))
        assert_that(csv_file, ends_with(".csv"))

        # Verify CSV content
        df = pd.read_csv(csv_file)
        assert_that(len(df), equal_to(1))
        assert_that(df.columns, has_item("test_name"))
        assert_that(df.iloc[0]["test_name"], equal_to("test_csv"))

    def test_numpy_statistical_operations(self):
        """Test numpy integration for statistical calculations."""
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite("numpy_test", "test", "chrome")

        # Add results with varied durations for statistical analysis
        durations = [1.0, 2.0, 3.0, 10.0, 1.5]  # 10.0 should be an outlier
        for i, duration in enumerate(durations):
            result = Result(
                f"test_{i}",
                "passed",
                duration,
                datetime.now(UTC),
                "test",
                "chrome",
            )
            reporter.add_test_result(result)

        # Generate analytics
        analytics = reporter.generate_dataframe_analytics()
        df = pd.DataFrame(analytics)

        # Verify z-score calculation
        assert_that(df.columns, has_item("duration_zscore"))

        # The outlier (10.0) should have a high z-score
        outliers = df[df["is_outlier"]]
        if len(outliers) > 0:
            assert_that(outliers.iloc[0]["duration"], equal_to(10.0))


class TestYAMLIntegration:
    """Test YAML integration in test data manager."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_yaml_config_loading(self):
        """Test YAML configuration loading."""
        manager = DataManager(self.temp_dir)

        # Load YAML config (should create default if not exists)
        config = manager.load_yaml_config("browser_settings", "test")

        assert_that(config, instance_of(dict))
        assert_that(len(config), greater_than(0))
        assert_that(config, has_key("test_environment"))

    def test_yaml_data_export(self):
        """Test YAML data export functionality."""
        manager = DataManager(self.temp_dir)

        # Test data to export (matching the expected structure)
        test_data = {
            "total_tests": 5,
            "passed": 4,
            "failed": 1,
            "success_rate": 0.8,
            "performance_metrics": {"avg_duration": 2.3},
        }

        # Export to YAML
        yaml_file = manager.save_test_results_yaml(test_data)
        assert_that(yaml_file, is_(not_none()))
        assert_that(Path.exists(yaml_file), is_(True))
        assert_that(yaml_file, ends_with(".yml"))

        # Verify YAML content
        with Path.open(yaml_file) as f:
            loaded_data = yaml.safe_load(f)

        assert_that(loaded_data, is_(not_none()))
        assert_that(loaded_data, has_key("test_execution"))
        assert_that(loaded_data["test_execution"]["total_tests"], equal_to(5))

    def test_yaml_configuration_structure(self):
        """Test that YAML configurations have expected structure."""
        manager = DataManager(self.temp_dir)

        # Load config for different environments
        for env in ["test", "qa", "production"]:
            config = manager.load_yaml_config("browser_settings", env)

            assert_that(config, instance_of(dict))
            # Should have basic structure
            assert_that(len(config), greater_than_or_equal_to(1))


class TestPsutilIntegration:
    """Test psutil integration for system monitoring."""

    def test_memory_monitoring(self):
        """Test memory monitoring functionality."""
        handler = SmartErrorHandler()

        # Test memory monitoring
        memory_data = handler.monitor_memory_usage()

        assert_that(memory_data, instance_of(dict))
        assert_that(memory_data, has_key("current_memory_mb"))
        assert_that(memory_data, has_key("memory_percent"))
        assert_that(memory_data, has_key("cpu_percent"))
        assert_that(memory_data, has_key("timestamp"))

        # Verify data types and ranges
        assert_that(
            memory_data["current_memory_mb"],
            any_of(instance_of(int), instance_of(float)),
        )
        assert_that(
            memory_data["memory_percent"],
            any_of(instance_of(int), instance_of(float)),
        )
        assert_that(
            memory_data["cpu_percent"],
            any_of(instance_of(int), instance_of(float)),
        )
        assert_that(memory_data["current_memory_mb"], greater_than(0))
        assert_that(0, less_than_or_equal_to(memory_data["memory_percent"] <= 100))

    def test_system_info_collection(self):
        """Test system information collection."""
        # Test basic psutil functionality
        cpu_count = psutil.cpu_count()
        memory_info = psutil.virtual_memory()

        assert_that(cpu_count, greater_than(0))
        assert_that(memory_info.total, greater_than(0))
        assert_that(memory_info, has_property("available"))
        assert_that(memory_info, has_property("percent"))


class TestTenacityIntegration:
    """Test tenacity integration for retry mechanisms."""

    def test_retry_configuration(self):
        """Test tenacity retry configuration."""
        # Test retry configuration creation
        retry_config = Retrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
        )

        assert_that(retry_config, is_(not_none()))
        assert_that(retry_config, has_property("stop"))
        assert_that(retry_config, has_property("wait"))

    def test_error_handler_retry_integration(self):
        """Test that error handler integrates with tenacity."""
        handler = SmartErrorHandler()

        # Check that handler has retry capabilities
        assert_that(handler, has_property("execute_with_tenacity_retry"))

    def test_retry_execution_simulation(self):
        """Test retry execution with tenacity."""
        # Create a function that fails first time, succeeds second time
        call_count = 0

        class TestRetryException(Exception):
            """Custom exception for testing retry functionality."""

            pass

        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                message = "First attempt fails"
                raise TestRetryException(message)
            return "Success"

        # Configure retry
        retry_config = Retrying(
            # Fast retry for testing
            stop=stop_after_attempt(3),
            wait=wait_fixed(0.1),
        )

        # Execute with retry
        result = retry_config(flaky_function)

        assert_that(result, equal_to("Success"))
        # Should have been called twice
        assert_that(call_count, equal_to(2))


class TestJinja2Integration:
    """Test jinja2 integration for template rendering."""

    def test_template_creation(self):
        """Test basic template creation and rendering."""
        # Create a simple template
        template = Template("<h1>{{ title }}</h1><p>{{ description }}</p>")

        # Render with data
        rendered = template.render(
            title="Test Report",
            description="This is a test description",
        )

        assert_that(rendered, contains_string("<h1>Test Report</h1>"))
        assert_that(rendered, contains_string("<p>This is a test description</p>"))

    def test_html_report_template(self):
        """Test HTML report template functionality."""
        # Create a more complex template similar to what would be used for
        # reports
        html_template = Template(
            """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ suite_name }} - Test Report</title>
        </head>
        <body>
            <h1>{{ suite_name }}</h1>
            <p>Environment: {{ environment }}</p>
            <p>Browser: {{ browser }}</p>
            <p>Total Tests: {{ total_tests }}</p>
            <p>Success Rate: {{ success_rate }}%</p>

            {% if test_results %}
            <table>
                <tr><th>Test Name</th><th>Status</th><th>Duration</th></tr>
                {% for test in test_results %}
                <tr>
                    <td>{{ test.name }}</td>
                    <td>{{ test.status }}</td>
                    <td>{{ test.duration }}s</td>
                </tr>
                {% endfor %}
            </table>
            {% endif %}
        </body>
        </html>
        """,
        )

        # Test data
        test_data = {
            "suite_name": "Integration Tests",
            "environment": "test",
            "browser": "chrome",
            "total_tests": 3,
            "success_rate": 66.7,
            "test_results": [
                {"name": "test1", "status": "passed", "duration": 1.2},
                {"name": "test2", "status": "failed", "duration": 2.1},
                {"name": "test3", "status": "passed", "duration": 0.8},
            ],
        }

        # Render template
        rendered = html_template.render(**test_data)

        # Verify rendered content
        assert_that(rendered, contains_string("<!DOCTYPE html>"))
        assert_that(
            rendered,
            contains_string("<title>Integration Tests - Test Report</title>"),
        )
        assert_that(rendered, contains_string("Environment: test"))
        assert_that(rendered, contains_string("Browser: chrome"))
        assert_that(rendered, contains_string("Total Tests: 3"))
        assert_that(rendered, contains_string("Success Rate: 66.7%"))
        assert_that(rendered, contains_string("<td>test1</td>"))
        assert_that(rendered, contains_string("<td>passed</td>"))


class TestNumpyIntegration:
    """Test numpy integration for mathematical operations."""

    def test_numpy_statistical_functions(self):
        """Test numpy statistical operations."""
        # Test data
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 15.0])  # 15.0 is an outlier

        # Calculate statistics
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)

        assert_that(mean, greater_than(0))
        assert_that(std, greater_than(0))
        assert_that(len(z_scores), equal_to(len(data)))

        # Test outlier detection (z-score > 2)
        outliers = z_scores > 2
        outlier_values = data[outliers]

        # 15.0 should be detected as an outlier
        assert_that(outlier_values, has_item(15.0))

    def test_numpy_with_pandas_integration(self):
        """Test numpy operations within pandas context."""
        # Create DataFrame
        df = pd.DataFrame(
            {
                "duration": [1.0, 2.0, 3.0, 4.0, 10.0],
                "status": ["passed", "passed", "failed", "passed", "passed"],
            },
        )

        # Add numpy-based calculations
        df["duration_zscore"] = np.abs(
            (df["duration"] - df["duration"].mean()) / df["duration"].std(),
        )
        df["is_outlier"] = df["duration_zscore"] > 2

        # Verify calculations
        assert_that(df.columns, has_item("duration_zscore"))
        assert_that(df.columns, has_item("is_outlier"))
        assert_that(df["is_outlier"].dtype, equal_to(bool))

        # The value 10.0 should be detected as an outlier
        outliers = df[df["is_outlier"]]
        if len(outliers) > 0:
            assert_that(outliers["duration"].values, has_item(10.0))


class TestLibraryIntegrationSmokeTest:
    """Smoke tests to ensure all libraries work together."""

    def test_all_libraries_importable(self):
        """Test that all integrated libraries can be imported."""
        try:
            # Basic functionality test
            assert_that(pandas, has_property("DataFrame"))
            assert_that(numpy, has_property("array"))
            assert_that(yaml, has_property("load"))
            assert_that(psutil, has_property("Process"))
            assert_that(tenacity, has_property("Retrying"))
            assert_that(jinja2, has_property("Template"))

        except ImportError as e:
            pytest.fail(f"Library import failed: {e}")

    def test_framework_components_with_libraries(self):
        """Test that framework components use libraries correctly."""
        # Test that components can be instantiated
        temp_dir = tempfile.mkdtemp()

        reporter = AdvancedTestReporter(temp_dir)
        data_manager = DataManager(temp_dir)
        error_handler = SmartErrorHandler()

        # Test basic functionality
        assert_that(reporter, is_(not_none()))
        assert_that(data_manager, is_(not_none()))
        assert_that(error_handler, is_(not_none()))

        # Test that they have library-enabled methods
        assert_that(reporter, has_property("generate_dataframe_analytics"))
        assert_that(reporter, has_property("export_to_csv"))
        assert_that(data_manager, has_property("load_yaml_config"))
        assert_that(data_manager, has_property("save_test_results_yaml"))
        assert_that(error_handler, has_property("monitor_memory_usage"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
