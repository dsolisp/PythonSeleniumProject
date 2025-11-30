"""
Test Data Manager - Demonstrates multi-format data loading and generation.
Showcases: JSON/YAML/CSV support, environment configs, dynamic data generation.

Architecture follows SRP:
- FileLoader: Handles loading data from different file formats (JSON/YAML/CSV)
- TestDataGenerator: Handles generating dynamic test data (users, scenarios)
- DataManager: Coordinates the above (facade pattern)

Usage Examples:
    # Initialize with custom data directory
    from utils.test_data_manager import DataManager

    manager = DataManager("./test_data")

    # Load test data (auto-detects JSON/YAML/CSV)
    users = manager.load_test_data("users", environment="staging")

    # Load/create YAML configuration
    config = manager.load_yaml_config("browser", environment="ci")
    # Returns: {"test_environment": {...}, "browser_config": {...}}

    # Save test results to YAML
    results = {"total_tests": 50, "passed": 48, "failed": 2}
    manager.save_test_results_yaml(results, "regression_results.yml")

    # Generate dynamic test data
    user = manager.generate_user_data()  # Random user with email, name, etc.
    users = manager.generate_bulk_users(count=10)

YAML Config Structure Example (data/configs/browser_ci.yml):
    test_environment:
      name: ci
      base_url: https://ci.example.com
      timeout: 10
      retry_attempts: 3
    browser_config:
      default_browser: chrome
      headless: true
      window_size: [1920, 1080]
"""

import csv
import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, Union

import yaml

# === FILE LOADERS (SRP) ===


class FileLoader:
    """Handles loading data from different file formats. Follows SRP."""

    @staticmethod
    def load_json(path: Path) -> dict[str, Any]:
        """Load data from JSON file."""
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def load_yaml(path: Path) -> dict[str, Any]:
        """Load data from YAML file."""
        with open(path) as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def load_csv(path: Path) -> dict[str, Any]:
        """Load data from CSV file as list of dicts."""
        with open(path, newline="") as f:
            return {"data": list(csv.DictReader(f))}

    @classmethod
    def load(cls, path: Path) -> dict[str, Any]:
        """Auto-detect format and load file."""
        suffix = path.suffix.lower()
        if suffix == ".json":
            return cls.load_json(path)
        if suffix in (".yaml", ".yml"):
            return cls.load_yaml(path)
        if suffix == ".csv":
            return cls.load_csv(path)
        raise ValueError(f"Unsupported file format: {suffix}")


# === TEST DATA GENERATOR (SRP) ===


class TestDataGenerator:
    """Handles generating dynamic test data. Follows SRP."""

    FIRST_NAMES = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Davis"]
    DOMAINS = ["test.com", "example.org", "demo.net", "qa.io"]
    SEARCH_PREFIXES = ["automation", "testing", "selenium", "python", "qa"]
    SEARCH_CONTEXTS = ["best practices", "tutorial", "examples", "guide"]

    def generate_user(self, user_id: Optional[int] = None) -> dict[str, Any]:
        """Generate a random test user."""
        uid = user_id or random.randint(1000, 9999)
        first = random.choice(self.FIRST_NAMES)
        last = random.choice(self.LAST_NAMES)
        domain = random.choice(self.DOMAINS)
        return {
            "id": uid,
            "email": f"{first.lower()}.{last.lower()}{uid}@{domain}",
            "name": f"{first} {last}",
            "username": f"{first.lower()}{uid}",
            "created_at": (
                datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
            ).isoformat(),
            "role": random.choice(["user", "admin", "moderator"]),
            "is_active": random.choice([True, True, True, False]),  # 75% active
        }

    def generate_bulk_users(self, count: int = 10) -> list[dict[str, Any]]:
        """Generate multiple test users."""
        return [self.generate_user(i) for i in range(1, count + 1)]

    def generate_search_scenario(self) -> dict[str, Any]:
        """Generate a random search test scenario."""
        prefix = random.choice(self.SEARCH_PREFIXES)
        context = random.choice(self.SEARCH_CONTEXTS)
        return {
            "query": f"{prefix} {context}",
            "expected_min_results": random.randint(5, 50),
            "timeout": random.choice([5, 10, 15]),
            "filters": {
                "date_range": random.choice(["any", "past_week", "past_month"]),
                "sort_by": random.choice(["relevance", "date"]),
            },
        }


@dataclass
class DataSet:
    """Test data set with metadata."""

    name: str
    data: dict[str, Any]
    created_at: datetime
    environment: str
    tags: list[str] = field(default_factory=list)


class DataManager:
    """
    Multi-format test data manager with environment support.

    Coordinates:
    - FileLoader: File format handling
    - TestDataGenerator: Dynamic data generation
    """

    def __init__(self, data_directory: Optional[Union[str, Path]] = None):
        self.data_dir = (
            Path(data_directory)
            if data_directory
            else Path(__file__).parent.parent / "data"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Any] = {}
        self._file_loader = FileLoader()
        self._data_generator = TestDataGenerator()

    def load_test_data(
        self, filename: str, environment: str = "default"
    ) -> dict[str, Any]:
        """Load test data from JSON/YAML/CSV with environment support and caching."""
        key = f"{filename}_{environment}"
        if key in self._cache:
            return self._cache[key]

        for ext in [".json", ".yaml", ".yml", ".csv"]:
            path = self._get_env_path(filename, environment, ext)
            if path.exists():
                data = self._file_loader.load(path)
                self._cache[key] = data
                return data

        # Fallback to default environment
        if environment != "default":
            return self.load_test_data(filename, "default")
        return {}

    def load_yaml_config(
        self, config_name: str, environment: str = "default"
    ) -> dict[str, Any]:
        """Load YAML config, creating default if missing - demonstrates YAML integration."""
        path = self.data_dir / "configs" / f"{config_name}_{environment}.yml"
        path.parent.mkdir(exist_ok=True)

        if not path.exists():
            # Create default config
            default = {
                "test_environment": {
                    "name": environment,
                    "base_url": f"https://{environment}.example.com",
                    "timeout": 10,
                    "retry_attempts": 3,
                },
                "browser_config": {
                    "default_browser": "chrome",
                    "headless": True,
                    "window_size": [1920, 1080],
                },
            }
            with open(path, "w") as f:
                yaml.dump(default, f, default_flow_style=False, indent=2)

        with open(path) as f:
            return yaml.safe_load(f)

    def save_test_results_yaml(
        self, results: dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Save test results in YAML format."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.data_dir / "results" / (filename or f"results_{ts}.yml")
        path.parent.mkdir(exist_ok=True)
        data = {
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
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
        return str(path)

    # === DATA ACCESSORS ===

    def get_search_scenarios(
        self, environment: str = "default"
    ) -> list[dict[str, Any]]:
        """Get search test scenarios."""
        return self.load_test_data("test_data", environment).get("search_scenarios", [])

    def get_user_accounts(
        self, role: Optional[str] = None, environment: str = "default"
    ) -> list[dict[str, Any]]:
        """Get user accounts, optionally filtered by role."""
        accounts = self.load_test_data("test_data", environment).get(
            "user_accounts", []
        )
        return [a for a in accounts if a.get("role") == role] if role else accounts

    def get_api_endpoints(
        self, method: Optional[str] = None, environment: str = "default"
    ) -> list[dict[str, Any]]:
        """Get API endpoints, optionally filtered by HTTP method."""
        endpoints = self.load_test_data("test_data", environment).get(
            "api_endpoints", []
        )
        return (
            [e for e in endpoints if e.get("method", "").upper() == method.upper()]
            if method
            else endpoints
        )

    def get_browser_configurations(
        self,
        browser: Optional[str] = None,
        mobile: Optional[bool] = None,
        environment: str = "default",
    ) -> list[dict[str, Any]]:
        """Get browser configs with optional filters."""
        configs = self.load_test_data("test_data", environment).get(
            "browser_configurations", []
        )
        if browser:
            configs = [c for c in configs if c.get("browser") == browser]
        if mobile is not None:
            configs = [c for c in configs if c.get("mobile") == mobile]
        return configs

    # === DATA GENERATORS ===

    def generate_test_user(self, role: str = "standard") -> dict[str, Any]:
        """Generate dynamic test user data."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        uid = random.randint(1000, 9999)
        perms = {
            "admin": ["read", "write", "delete", "admin"],
            "standard": ["read", "write"],
            "readonly": ["read"],
        }
        return {
            "username": f"{role}_user_{uid}",
            "password": f"{role}_pass_{ts}",
            "email": f"{role}{uid}@testdomain.com",
            "role": role,
            "permissions": perms.get(role, ["read"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "user_id": uid,
        }

    def generate_search_data(self, count: int = 5) -> list[dict[str, Any]]:
        """Generate dynamic search test scenarios."""
        terms = [
            "Python automation",
            "Selenium WebDriver",
            "API testing",
            "CI/CD pipeline",
            "Performance testing",
        ]
        return [
            {
                "name": f"generated_search_{i + 1}",
                "search_term": random.choice(terms),
                "expected_results_count": random.randint(5, 15),
                "timeout": random.randint(10, 20),
                "expected_title_contains": random.choice(terms).split()[0],
                "generated": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            for i in range(count)
        ]

    # === RESULT SAVING ===

    def save_test_results(
        self, _test_name: str, _results: dict[str, Any], environment: str = "default"
    ) -> None:
        """Save test results (creates directory)."""
        (self.data_dir / "results" / environment).mkdir(parents=True, exist_ok=True)

    def save_test_results_json(
        self,
        test_name: str,
        results: list[dict[str, Any]],
        environment: str = "default",
    ) -> str:
        """Save test results in JSON format with metadata."""
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.data_dir / "results" / f"{test_name}_{ts}.json"
        path.parent.mkdir(exist_ok=True)
        data = {
            "test_name": test_name,
            "environment": environment,
            "timestamp": ts,
            "execution_time": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return str(path)

    def cleanup_old_results(self, days_to_keep: int = 30) -> None:
        """Clean up result files older than specified days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        results_dir = self.data_dir / "results"
        if not results_dir.exists():
            return
        for path in results_dir.rglob("*.json"):
            try:
                if (
                    datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                    < cutoff
                ):
                    path.unlink()
            except (OSError, ValueError):
                continue

    def validate_data_schema(self, data: dict[str, Any], schema_name: str) -> bool:
        """Validate data against predefined schemas."""
        schemas = {
            "search_scenario": ["name", "search_term"],
            "user_account": ["username", "password", "role"],
            "api_endpoint": ["name", "url", "method"],
        }
        if schema_name not in schemas:
            return False
        return all(f in data for f in schemas[schema_name])

    # === PRIVATE HELPERS ===

    def _get_env_path(self, filename: str, environment: str, ext: str) -> Path:
        """Get environment-specific file path."""
        if environment == "default":
            return self.data_dir / f"{filename}{ext}"
        return self.data_dir / environment / f"{filename}{ext}"


# Global instance
test_data_manager = DataManager()
