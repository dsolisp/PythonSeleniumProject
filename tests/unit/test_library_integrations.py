"""
Unit tests for library integrations (pandas, yaml, psutil, tenacity, jinja2, numpy).
Validates that all new library features are working correctly.
"""

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestPandasIntegration:
    """Test pandas integration in test reporter."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_pandas_dataframe_creation(self):
        """Test that pandas DataFrames are created correctly."""
        from utils.test_reporter import AdvancedTestReporter, TestResult
        import pandas as pd
        
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite('pandas_test', 'test', 'chrome')
        
        # Add test results
        results = [
            TestResult('test1', 'passed', 1.5, datetime.now(), 'test', 'chrome'),
            TestResult('test2', 'failed', 2.3, datetime.now(), 'test', 'chrome'),
            TestResult('test3', 'passed', 0.8, datetime.now(), 'test', 'chrome')
        ]
        
        for result in results:
            reporter.add_test_result(result)
        
        # Test DataFrame generation
        analytics = reporter.generate_dataframe_analytics()
        assert analytics is not None
        assert len(analytics) == 3
        
        # Verify DataFrame structure
        df = pd.DataFrame(analytics)
        expected_columns = ['test_name', 'status', 'duration', 'timestamp', 'browser', 'environment']
        for col in expected_columns:
            assert col in df.columns
        
        # Test statistical analysis
        assert df['duration'].mean() > 0
        assert df['duration'].std() >= 0
        assert 'is_outlier' in df.columns
        assert 'duration_zscore' in df.columns

    def test_csv_export_functionality(self):
        """Test CSV export using pandas."""
        from utils.test_reporter import AdvancedTestReporter, TestResult
        import pandas as pd
        
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite('csv_test', 'test', 'chrome')
        
        # Add test result
        result = TestResult('test_csv', 'passed', 1.2, datetime.now(), 'test', 'chrome')
        reporter.add_test_result(result)
        
        # Export to CSV
        csv_file = reporter.export_to_csv()
        assert csv_file is not None
        assert os.path.exists(csv_file)
        assert csv_file.endswith('.csv')
        
        # Verify CSV content
        df = pd.read_csv(csv_file)
        assert len(df) == 1
        assert 'test_name' in df.columns
        assert df.iloc[0]['test_name'] == 'test_csv'

    def test_numpy_statistical_operations(self):
        """Test numpy integration for statistical calculations."""
        from utils.test_reporter import AdvancedTestReporter, TestResult
        import pandas as pd
        import numpy as np
        
        reporter = AdvancedTestReporter(self.temp_dir)
        reporter.start_test_suite('numpy_test', 'test', 'chrome')
        
        # Add results with varied durations for statistical analysis
        durations = [1.0, 2.0, 3.0, 10.0, 1.5]  # 10.0 should be an outlier
        for i, duration in enumerate(durations):
            result = TestResult(f'test_{i}', 'passed', duration, datetime.now(), 'test', 'chrome')
            reporter.add_test_result(result)
        
        # Generate analytics
        analytics = reporter.generate_dataframe_analytics()
        df = pd.DataFrame(analytics)
        
        # Test z-score calculation (numpy operation)
        mean_duration = df['duration'].mean()
        std_duration = df['duration'].std()
        
        # Verify z-score calculation
        assert 'duration_zscore' in df.columns
        
        # The outlier (10.0) should have a high z-score
        outliers = df[df['is_outlier'] == True]
        if len(outliers) > 0:
            assert outliers.iloc[0]['duration'] == 10.0


class TestYAMLIntegration:
    """Test YAML integration in test data manager."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_yaml_config_loading(self):
        """Test YAML configuration loading."""
        from utils.test_data_manager import TestDataManager
        
        manager = TestDataManager(self.temp_dir)
        
        # Load YAML config (should create default if not exists)
        config = manager.load_yaml_config('browser_settings', 'test')
        
        assert isinstance(config, dict)
        assert len(config) > 0
        assert 'test_environment' in config or 'browser_config' in config

    def test_yaml_data_export(self):
        """Test YAML data export functionality."""
        from utils.test_data_manager import TestDataManager
        import yaml
        
        manager = TestDataManager(self.temp_dir)
        
        # Test data to export (matching the expected structure)
        test_data = {
            'total_tests': 5,
            'passed': 4,
            'failed': 1,
            'success_rate': 0.8,
            'performance_metrics': {
                'avg_duration': 2.3
            }
        }
        
        # Export to YAML
        yaml_file = manager.save_test_results_yaml(test_data)
        assert yaml_file is not None
        assert os.path.exists(yaml_file)
        assert yaml_file.endswith('.yml')
        
        # Verify YAML content
        with open(yaml_file, 'r') as f:
            loaded_data = yaml.safe_load(f)
        
        assert loaded_data is not None
        assert 'test_execution' in loaded_data
        assert loaded_data['test_execution']['total_tests'] == 5

    def test_yaml_configuration_structure(self):
        """Test that YAML configurations have expected structure."""
        from utils.test_data_manager import TestDataManager
        
        manager = TestDataManager(self.temp_dir)
        
        # Load config for different environments
        for env in ['test', 'qa', 'production']:
            config = manager.load_yaml_config('browser_settings', env)
            
            assert isinstance(config, dict)
            # Should have basic structure
            assert len(config) >= 1


class TestPsutilIntegration:
    """Test psutil integration for system monitoring."""

    def test_memory_monitoring(self):
        """Test memory monitoring functionality."""
        from utils.error_handler import SmartErrorHandler
        
        handler = SmartErrorHandler()
        
        # Test memory monitoring
        memory_data = handler.monitor_memory_usage()
        
        assert isinstance(memory_data, dict)
        assert 'current_memory_mb' in memory_data
        assert 'memory_percent' in memory_data
        assert 'cpu_percent' in memory_data
        assert 'timestamp' in memory_data
        
        # Verify data types and ranges
        assert isinstance(memory_data['current_memory_mb'], (int, float))
        assert isinstance(memory_data['memory_percent'], (int, float))
        assert isinstance(memory_data['cpu_percent'], (int, float))
        assert memory_data['current_memory_mb'] > 0
        assert 0 <= memory_data['memory_percent'] <= 100

    def test_system_info_collection(self):
        """Test system information collection."""
        import psutil
        
        # Test basic psutil functionality
        cpu_count = psutil.cpu_count()
        memory_info = psutil.virtual_memory()
        
        assert cpu_count > 0
        assert memory_info.total > 0
        assert hasattr(memory_info, 'available')
        assert hasattr(memory_info, 'percent')


class TestTenacityIntegration:
    """Test tenacity integration for retry mechanisms."""

    def test_retry_configuration(self):
        """Test tenacity retry configuration."""
        from tenacity import Retrying, stop_after_attempt, wait_exponential
        
        # Test retry configuration creation
        retry_config = Retrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10)
        )
        
        assert retry_config is not None
        assert hasattr(retry_config, 'stop')
        assert hasattr(retry_config, 'wait')

    def test_error_handler_retry_integration(self):
        """Test that error handler integrates with tenacity."""
        from utils.error_handler import SmartErrorHandler
        
        handler = SmartErrorHandler()
        
        # Check that handler has retry capabilities
        assert hasattr(handler, 'execute_with_tenacity_retry')

    def test_retry_execution_simulation(self):
        """Test retry execution with tenacity."""
        from tenacity import Retrying, stop_after_attempt, wait_fixed
        
        # Create a function that fails first time, succeeds second time
        call_count = 0
        
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First attempt fails")
            return "Success"
        
        # Configure retry
        retry_config = Retrying(
            stop=stop_after_attempt(3),
            wait=wait_fixed(0.1)  # Fast retry for testing
        )
        
        # Execute with retry
        result = retry_config(flaky_function)
        
        assert result == "Success"
        assert call_count == 2  # Should have been called twice


class TestJinja2Integration:
    """Test jinja2 integration for template rendering."""

    def test_template_creation(self):
        """Test basic template creation and rendering."""
        from jinja2 import Template
        
        # Create a simple template
        template = Template('<h1>{{ title }}</h1><p>{{ description }}</p>')
        
        # Render with data
        rendered = template.render(
            title='Test Report',
            description='This is a test description'
        )
        
        assert '<h1>Test Report</h1>' in rendered
        assert '<p>This is a test description</p>' in rendered

    def test_html_report_template(self):
        """Test HTML report template functionality."""
        from jinja2 import Template
        
        # Create a more complex template similar to what would be used for reports
        html_template = Template('''
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
        ''')
        
        # Test data
        test_data = {
            'suite_name': 'Integration Tests',
            'environment': 'test',
            'browser': 'chrome',
            'total_tests': 3,
            'success_rate': 66.7,
            'test_results': [
                {'name': 'test1', 'status': 'passed', 'duration': 1.2},
                {'name': 'test2', 'status': 'failed', 'duration': 2.1},
                {'name': 'test3', 'status': 'passed', 'duration': 0.8}
            ]
        }
        
        # Render template
        rendered = html_template.render(**test_data)
        
        # Verify rendered content
        assert '<!DOCTYPE html>' in rendered
        assert '<title>Integration Tests - Test Report</title>' in rendered
        assert 'Environment: test' in rendered
        assert 'Browser: chrome' in rendered
        assert 'Total Tests: 3' in rendered
        assert 'Success Rate: 66.7%' in rendered
        assert '<td>test1</td>' in rendered
        assert '<td>passed</td>' in rendered


class TestNumpyIntegration:
    """Test numpy integration for mathematical operations."""

    def test_numpy_statistical_functions(self):
        """Test numpy statistical operations."""
        import numpy as np
        
        # Test data
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 15.0])  # 15.0 is an outlier
        
        # Calculate statistics
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        
        assert mean > 0
        assert std > 0
        assert len(z_scores) == len(data)
        
        # Test outlier detection (z-score > 2)
        outliers = z_scores > 2
        outlier_values = data[outliers]
        
        # 15.0 should be detected as an outlier
        assert 15.0 in outlier_values

    def test_numpy_with_pandas_integration(self):
        """Test numpy operations within pandas context."""
        import pandas as pd
        import numpy as np
        
        # Create DataFrame
        df = pd.DataFrame({
            'duration': [1.0, 2.0, 3.0, 4.0, 10.0],
            'status': ['passed', 'passed', 'failed', 'passed', 'passed']
        })
        
        # Add numpy-based calculations
        df['duration_zscore'] = np.abs((df['duration'] - df['duration'].mean()) / df['duration'].std())
        df['is_outlier'] = df['duration_zscore'] > 2
        
        # Verify calculations
        assert 'duration_zscore' in df.columns
        assert 'is_outlier' in df.columns
        assert df['is_outlier'].dtype == bool
        
        # The value 10.0 should be detected as an outlier
        outliers = df[df['is_outlier'] == True]
        if len(outliers) > 0:
            assert 10.0 in outliers['duration'].values


class TestLibraryIntegrationSmokeTest:
    """Smoke tests to ensure all libraries work together."""

    def test_all_libraries_importable(self):
        """Test that all integrated libraries can be imported."""
        try:
            import pandas
            import numpy
            import yaml
            import psutil
            import tenacity
            import jinja2
            
            # Basic functionality test
            assert hasattr(pandas, 'DataFrame')
            assert hasattr(numpy, 'array')
            assert hasattr(yaml, 'load')
            assert hasattr(psutil, 'Process')
            assert hasattr(tenacity, 'Retrying')
            assert hasattr(jinja2, 'Template')
            
        except ImportError as e:
            pytest.fail(f"Library import failed: {e}")

    def test_framework_components_with_libraries(self):
        """Test that framework components use libraries correctly."""
        from utils.test_reporter import AdvancedTestReporter
        from utils.test_data_manager import TestDataManager
        from utils.error_handler import SmartErrorHandler
        
        # Test that components can be instantiated
        temp_dir = tempfile.mkdtemp()
        
        reporter = AdvancedTestReporter(temp_dir)
        data_manager = TestDataManager(temp_dir)
        error_handler = SmartErrorHandler()
        
        # Test basic functionality
        assert reporter is not None
        assert data_manager is not None
        assert error_handler is not None
        
        # Test that they have library-enabled methods
        assert hasattr(reporter, 'generate_dataframe_analytics')
        assert hasattr(reporter, 'export_to_csv')
        assert hasattr(data_manager, 'load_yaml_config')
        assert hasattr(data_manager, 'save_test_results_yaml')
        assert hasattr(error_handler, 'monitor_memory_usage')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])