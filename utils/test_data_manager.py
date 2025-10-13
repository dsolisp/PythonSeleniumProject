"""
Test Data Manager for comprehensive data-driven testing.
Supports multiple data formats and environments for robust test automation.
"""

import csv
import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, Union

import yaml


@dataclass
class DataSet:
    """Represents a complete test data set with metadata."""

    name: str
    data: dict[str, Any]
    created_at: datetime
    environment: str
    tags: list[str]


class DataManager:
    """
    Comprehensive test data manager supporting multiple formats and environments.

    Features:
    - JSON, CSV, YAML data source support
    - Environment-specific data sets
    - Dynamic data generation
    - Data validation and cleanup
    - Test data versioning
    """

    def __init__(self, data_directory: Optional[Union[str, Path]] = None):
        """Initialize test data manager."""
        self.data_dir = (
            Path(data_directory)
            if data_directory
            else Path(__file__).parent.parent / "data"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        self._generators = self._setup_generators()

    def load_test_data(
        self,
        filename: str,
        environment: str = "default",
    ) -> dict[str, Any]:
        """
        Load test data from file with environment support.

        Args:
            filename: Name of the data file (without extension)
            environment: Environment-specific data (default, dev, qa, prod)

        Returns:
            Dictionary containing test data
        """
        cache_key = f"{filename}_{environment}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Try different file formats
        for ext in [".json", ".yaml", ".yml", ".csv"]:
            file_path = self._get_env_file_path(filename, environment, ext)
            if file_path.exists():
                data = self._load_file(file_path)
                self._cache[cache_key] = data
                return data

        # Fallback to default environment
        if environment != "default":
            return self.load_test_data(filename, "default")

        # Return empty dict if no file found instead of raising error
        return {}

    def load_yaml_config(
        self,
        config_name: str,
        environment: str = "default",
    ) -> dict[str, Any]:
        """
        Load YAML configuration files for complex test setups.
        Demonstrates meaningful YAML integration for configuration management.

        Args:
            config_name: Name of the config file (without extension)
            environment: Environment-specific config to load

        Returns:
            Dictionary containing configuration data
        """
        config_file = f"{config_name}_{environment}.yml"
        config_path = self.data_dir / "configs" / config_file

        # Create configs directory if it doesn't exist
        config_path.parent.mkdir(exist_ok=True)

        if not config_path.exists():
            # Create default config if it doesn't exist
            default_config = {
                "test_environment": {
                    "name": environment,
                    "base_url": f"https://{environment}.example.com",
                    "timeout": 10,
                    "retry_attempts": 3,
                },
                "test_data": {
                    "user_pools": [
                        {"role": "admin", "count": 2},
                        {"role": "standard", "count": 5},
                        {"role": "readonly", "count": 3},
                    ],
                    "test_scenarios": [
                        {
                            "name": "login_flow",
                            "priority": "high",
                            "data_set": "admin_users",
                        },
                        {
                            "name": "search_functionality",
                            "priority": "medium",
                            "data_set": "search_queries",
                        },
                        {
                            "name": "user_management",
                            "priority": "high",
                            "data_set": "user_accounts",
                        },
                    ],
                },
                "browser_config": {
                    "default_browser": "chrome",
                    "headless": True,
                    "window_size": [1920, 1080],
                    "wait_timeout": 10,
                },
            }

            with Path.open(config_path, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)

        # Load and return the YAML config
        with config_path.open() as f:
            return yaml.safe_load(f)

    def save_test_results_yaml(
        self,
        results: dict[str, Any],
        filename: Optional[str] = None,
    ) -> str:
        """
        Save test results in YAML format for human-readable reports.
        Demonstrates YAML output functionality.
        """
        if filename is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.yml"

        filepath = self.data_dir / "results" / filename
        filepath.parent.mkdir(exist_ok=True)

        # Format results for YAML output
        yaml_results = {
            "test_execution": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_tests": results.get("total_tests", 0),
                "passed": results.get("passed", 0),
                "failed": results.get("failed", 0),
                "success_rate": f"{results.get('success_rate', 0):.2%}",
            },
            "test_details": results.get("test_details", []),
            "performance_metrics": results.get("performance_metrics", {}),
            "environment_info": results.get("environment_info", {}),
        }

        with filepath.open("w") as f:
            yaml.dump(yaml_results, f, default_flow_style=False, indent=2)

        return str(filepath)

    def get_search_scenarios(
        self,
        environment: str = "default",
    ) -> list[dict[str, Any]]:
        """Get search test scenarios."""
        data = self.load_test_data("test_data", environment)
        return data.get("search_scenarios", [])

    def get_user_accounts(
        self,
        role: Optional[str] = None,
        environment: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Get user account data, optionally filtered by role.

        Args:
            role: Filter by user role (admin, standard, readonly)
            environment: Environment to load data from

        Returns:
            List of user account dictionaries
        """
        data = self.load_test_data("test_data", environment)
        accounts = data.get("user_accounts", [])

        if role:
            accounts = [acc for acc in accounts if acc.get("role") == role]

        return accounts

    def get_api_endpoints(
        self,
        method: Optional[str] = None,
        environment: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Get API endpoint configurations.

        Args:
            method: Filter by HTTP method (GET, POST, PUT, DELETE)
            environment: Environment to load data from

        Returns:
            List of API endpoint configurations
        """
        data = self.load_test_data("test_data", environment)
        endpoints = data.get("api_endpoints", [])

        if method:
            endpoints = [
                ep for ep in endpoints if ep.get("method", "").upper() == method.upper()
            ]

        return endpoints

    def get_browser_configurations(
        *,
        self,
        browser: Optional[str] = None,
        mobile: Optional[bool] = None,
        environment: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Get browser configuration data.

        Args:
            browser: Filter by browser type (chrome, firefox, edge)
            mobile: Filter by mobile capability
            environment: Environment to load data from

        Returns:
            List of browser configuration dictionaries
        """
        data = self.load_test_data("test_data", environment)
        configs = data.get("browser_configurations", [])

        if browser:
            configs = [cfg for cfg in configs if cfg.get("browser") == browser]
        if mobile is not None:
            configs = [cfg for cfg in configs if cfg.get("mobile") == mobile]

        return configs

    def generate_test_user(self, role: str = "standard") -> dict[str, Any]:
        """
        Generate dynamic test user data.

        Args:
            role: User role (admin, standard, readonly)

        Returns:
            Dictionary with generated user data
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        user_id = random.randint(1000, 9999)

        base_permissions = {
            "admin": ["read", "write", "delete", "admin"],
            "standard": ["read", "write"],
            "readonly": ["read"],
        }

        return {
            "username": f"{role}_user_{user_id}",
            "password": f"{role}_pass_{timestamp}",
            "email": f"{role}{user_id}@testdomain.com",
            "role": role,
            "permissions": base_permissions.get(role, ["read"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "user_id": user_id,
        }

    def generate_search_data(self, count: int = 5) -> list[dict[str, Any]]:
        """
        Generate dynamic search test data.

        Args:
            count: Number of search scenarios to generate

        Returns:
            List of generated search scenarios
        """
        search_terms = [
            "Python automation testing",
            "Selenium WebDriver tutorial",
            "Playwright vs Selenium",
            "Test automation best practices",
            "API testing with Python",
            "Database testing strategies",
            "Visual regression testing",
            "CI/CD pipeline automation",
            "Performance testing tools",
            "Mobile automation testing",
        ]

        scenarios = []
        for i in range(count):
            term = random.choice(search_terms)
            scenarios.append(
                {
                    "name": f"generated_search_{i + 1}",
                    "search_term": term,
                    "expected_results_count": random.randint(5, 15),
                    "expected_title_contains": term.split()[0],
                    "timeout": random.randint(10, 20),
                    "generated": True,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        return scenarios

    def save_test_results(
        self,
        _test_name: str,
        _results: dict[str, Any],
        environment: str = "default",
    ) -> None:
        """
        Save test execution results for analysis.

        Args:
            test_name: Name of the test
            results: Test results dictionary
            environment: Environment where test was executed
        """
        results_dir = self.data_dir / "results" / environment
        results_dir.mkdir(parents=True, exist_ok=True)

    def save_test_results_json(
        self,
        test_name: str,
        results: list[dict[str, Any]],
        environment: str = "default",
    ) -> str:
        """
        Save test results in JSON format.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{timestamp}.json"
        results_dir = self.data_dir / "results"
        results_dir.mkdir(exist_ok=True)
        file_path = results_dir / filename

        # Add metadata
        results_with_metadata = {
            "test_name": test_name,
            "environment": environment,
            "timestamp": timestamp,
            "execution_time": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }

        with file_path.open("w") as f:
            json.dump(results_with_metadata, f, indent=2, default=str)
        return str(file_path)

    def cleanup_old_results(self, days_to_keep: int = 30) -> None:
        """
        Clean up old test result files.

        Args:
            days_to_keep: Number of days to keep results (default: 30)
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        results_dir = self.data_dir / "results"

        if not results_dir.exists():
            return

        for file_path in results_dir.rglob("*.json"):
            try:
                file_date = datetime.fromtimestamp(
                    file_path.stat().st_mtime,
                    tz=timezone.utc,
                )
            except (OSError, ValueError):
                continue
            if file_date < cutoff_date:
                try:
                    file_path.unlink()
                except (OSError, ValueError):
                    continue

    def validate_data_schema(self, data: dict[str, Any], schema_name: str) -> bool:
        """
        Validate test data against predefined schemas.

        Args:
            data: Data to validate
            schema_name: Name of the schema to validate against

        Returns:
            True if data is valid, False otherwise
        """
        schemas = {
            "search_scenario": {
                "required": ["name", "search_term"],
                "optional": [
                    "expected_results_count",
                    "timeout",
                    "expected_title_contains",
                ],
            },
            "user_account": {
                "required": ["username", "password", "role"],
                "optional": ["email", "permissions", "active"],
            },
            "api_endpoint": {
                "required": ["name", "url", "method"],
                "optional": ["expected_status", "expected_count", "headers"],
            },
        }

        schema = schemas.get(schema_name)
        if not schema:
            return False

        # Check required fields
        return all(field in data for field in schema["required"])

    def _get_env_file_path(
        self,
        filename: str,
        environment: str,
        extension: str,
    ) -> Path:
        """Get environment-specific file path."""
        if environment == "default":
            return self.data_dir / f"{filename}{extension}"
        return self.data_dir / environment / f"{filename}{extension}"

    def _load_file(self, file_path: Path) -> dict[str, Any]:
        """Load data from file based on extension."""
        if file_path.suffix.lower() == ".json":
            with file_path.open() as f:
                return json.load(f)
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            with file_path.open() as f:
                return yaml.safe_load(f) or {}
        elif file_path.suffix.lower() == ".csv":
            return self._load_csv(file_path)
        else:
            msg = f"Unsupported file format: {file_path.suffix}"
            raise ValueError(msg)

    def _load_csv(self, file_path: Path) -> dict[str, list[dict[str, Any]]]:
        """Load CSV file and convert to dictionary format."""
        with file_path.open() as f:
            reader = csv.DictReader(f)
            data = list(reader)

        # Group by first column if it looks like a category
        if data and len(data[0]) > 1:
            first_key = next(iter(data[0].keys()))
            return {first_key: data}
        return {"data": data}

    def _setup_generators(self) -> dict[str, Any]:
        """Setup data generators for dynamic content."""
        return {
            "email": lambda: f"user{random.randint(1000, 9999)}@testdomain.com",
            "phone": lambda: (
                f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-"
                f"{random.randint(1000, 9999)}"
            ),
            "url": lambda: f"https://example{random.randint(1, 100)}.com",
            "user_agent": lambda: random.choice(
                [
                    ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
                    (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36"
                    ),
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                ],
            ),
        }


# Global test data manager instance
test_data_manager = DataManager()
