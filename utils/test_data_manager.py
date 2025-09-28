"""
Test data management system with factories, fixtures, and secure handling.
"""

import json
import yaml
import csv
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import faker
import factory
from factory import fuzzy
import secrets
from cryptography.fernet import Fernet
import base64
from datetime import datetime, timedelta

from config.settings import settings


@dataclass
class TestUser:
    """Test user data structure."""
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    phone: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    role: str = "user"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestProduct:
    """Test product data structure."""
    name: str
    description: str
    price: float
    category: str
    sku: str
    stock_quantity: int = 10
    is_available: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data by identifier."""
        pass
    
    @abstractmethod
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data with identifier."""
        pass


class JSONDataSource(DataSource):
    """JSON file data source."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        file_path = self.data_dir / f"{identifier}.json"
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON data from {file_path}: {e}")
            return {}
    
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file."""
        file_path = self.data_dir / f"{identifier}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON data to {file_path}: {e}")
            return False


class YAMLDataSource(DataSource):
    """YAML file data source."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data from YAML file."""
        file_path = self.data_dir / f"{identifier}.yaml"
        if not file_path.exists():
            # Try .yml extension
            file_path = self.data_dir / f"{identifier}.yml"
            if not file_path.exists():
                return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading YAML data from {file_path}: {e}")
            return {}
    
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to YAML file."""
        file_path = self.data_dir / f"{identifier}.yaml"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, indent=2, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving YAML data to {file_path}: {e}")
            return False


class CSVDataSource(DataSource):
    """CSV file data source."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, identifier: str) -> Dict[str, Any]:
        """Load data from CSV file."""
        file_path = self.data_dir / f"{identifier}.csv"
        if not file_path.exists():
            return {}
        
        try:
            data = {"rows": []}
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data["headers"] = reader.fieldnames
                data["rows"] = list(reader)
            return data
        except Exception as e:
            print(f"Error loading CSV data from {file_path}: {e}")
            return {}
    
    def save_data(self, identifier: str, data: Dict[str, Any]) -> bool:
        """Save data to CSV file."""
        file_path = self.data_dir / f"{identifier}.csv"
        
        try:
            if "rows" not in data or not data["rows"]:
                return False
            
            fieldnames = data.get("headers") or data["rows"][0].keys()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data["rows"])
            return True
        except Exception as e:
            print(f"Error saving CSV data to {file_path}: {e}")
            return False


class SecureDataManager:
    """Secure data manager for sensitive test data."""
    
    def __init__(self, key: Optional[bytes] = None):
        if key:
            self.cipher = Fernet(key)
        else:
            # Generate a key from environment or create new one
            key_str = settings.encrypt_sensitive_data
            if isinstance(key_str, str) and key_str.lower() == 'true':
                # In real implementation, this should come from secure key management
                key = Fernet.generate_key()
                self.cipher = Fernet(key)
            else:
                self.cipher = None
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.cipher:
            return data
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.cipher:
            return encrypted_data
        
        try:
            decoded = base64.b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return encrypted_data


class TestDataFactory:
    """Factory for generating test data."""
    
    def __init__(self):
        self.fake = faker.Faker()
        self.secure_manager = SecureDataManager()
    
    def create_user(self, **kwargs) -> TestUser:
        """Create a test user with random or specified data."""
        defaults = {
            'username': self.fake.user_name(),
            'email': self.fake.email(),
            'password': self.fake.password(length=12),
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'phone': self.fake.phone_number(),
            'address': self.fake.address(),
            'city': self.fake.city(),
            'country': self.fake.country(),
        }
        defaults.update(kwargs)
        
        # Encrypt sensitive data
        if self.secure_manager.cipher:
            defaults['password'] = self.secure_manager.encrypt_data(defaults['password'])
        
        return TestUser(**defaults)
    
    def create_product(self, **kwargs) -> TestProduct:
        """Create a test product with random or specified data."""
        defaults = {
            'name': self.fake.catch_phrase(),
            'description': self.fake.text(max_nb_chars=200),
            'price': round(self.fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2),
            'category': self.fake.word(),
            'sku': self.fake.uuid4()[:8].upper(),
            'stock_quantity': self.fake.random_int(min=1, max=100),
        }
        defaults.update(kwargs)
        
        return TestProduct(**defaults)
    
    def create_users_batch(self, count: int, **common_attrs) -> List[TestUser]:
        """Create a batch of test users."""
        return [self.create_user(**common_attrs) for _ in range(count)]
    
    def create_products_batch(self, count: int, **common_attrs) -> List[TestProduct]:
        """Create a batch of test products."""
        return [self.create_product(**common_attrs) for _ in range(count)]


class TestDataManager:
    """Central test data management system."""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or settings.test_data_dir
        self.data_sources = {
            'json': JSONDataSource(self.data_dir / 'json'),
            'yaml': YAMLDataSource(self.data_dir / 'yaml'),
            'csv': CSVDataSource(self.data_dir / 'csv'),
        }
        self.factory = TestDataFactory()
        self.cache = {}
    
    def load_test_data(
        self, 
        identifier: str, 
        source_type: str = 'json',
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Load test data from specified source."""
        cache_key = f"{source_type}:{identifier}"
        
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        if source_type not in self.data_sources:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        data = self.data_sources[source_type].load_data(identifier)
        
        if use_cache:
            self.cache[cache_key] = data
        
        return data
    
    def save_test_data(
        self, 
        identifier: str, 
        data: Dict[str, Any], 
        source_type: str = 'json'
    ) -> bool:
        """Save test data to specified source."""
        if source_type not in self.data_sources:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        success = self.data_sources[source_type].save_data(identifier, data)
        
        if success:
            cache_key = f"{source_type}:{identifier}"
            self.cache[cache_key] = data
        
        return success
    
    def get_user_data(self, user_type: str = 'default') -> TestUser:
        """Get user data by type."""
        user_data = self.load_test_data(f'users_{user_type}')
        
        if not user_data:
            # Generate new user data
            return self.factory.create_user()
        
        # Decrypt password if encrypted
        if 'password' in user_data:
            user_data['password'] = self.factory.secure_manager.decrypt_data(user_data['password'])
        
        return TestUser(**user_data)
    
    def get_product_data(self, product_type: str = 'default') -> TestProduct:
        """Get product data by type."""
        product_data = self.load_test_data(f'products_{product_type}')
        
        if not product_data:
            # Generate new product data
            return self.factory.create_product()
        
        return TestProduct(**product_data)
    
    def get_test_credentials(self, environment: str = None) -> Dict[str, str]:
        """Get test credentials for specific environment."""
        env = environment or settings.environment.value
        credentials = self.load_test_data(f'credentials_{env}')
        
        # Decrypt credentials if encrypted
        secure_manager = self.factory.secure_manager
        if secure_manager.cipher:
            for key, value in credentials.items():
                if 'password' in key.lower() or 'secret' in key.lower():
                    credentials[key] = secure_manager.decrypt_data(value)
        
        return credentials
    
    def get_api_test_data(self, endpoint: str) -> Dict[str, Any]:
        """Get API test data for specific endpoint."""
        return self.load_test_data(f'api_{endpoint}')
    
    def clear_cache(self):
        """Clear the data cache."""
        self.cache.clear()
    
    def cleanup_generated_data(self, older_than_days: int = 7):
        """Clean up old generated test data files."""
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        for source_type, source in self.data_sources.items():
            data_dir = source.data_dir
            
            for file_path in data_dir.glob("generated_*"):
                if file_path.stat().st_mtime < cutoff_date.timestamp():
                    try:
                        file_path.unlink()
                        print(f"Cleaned up old test data file: {file_path}")
                    except Exception as e:
                        print(f"Error cleaning up {file_path}: {e}")


# Factory Boy factories for more complex data generation
class UserFactory(factory.Factory):
    """Factory Boy factory for test users."""
    
    class Meta:
        model = TestUser
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password', length=12)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    city = factory.Faker('city')
    country = factory.Faker('country')
    role = fuzzy.FuzzyChoice(['user', 'admin', 'moderator'])
    is_active = True


class ProductFactory(factory.Factory):
    """Factory Boy factory for test products."""
    
    class Meta:
        model = TestProduct
    
    name = factory.Faker('catch_phrase')
    description = factory.Faker('text', max_nb_chars=200)
    price = fuzzy.FuzzyFloat(1.0, 1000.0, precision=2)
    category = fuzzy.FuzzyChoice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'])
    sku = factory.LazyFunction(lambda: secrets.token_hex(4).upper())
    stock_quantity = fuzzy.FuzzyInteger(1, 100)
    is_available = True


# Global test data manager instance
test_data_manager = TestDataManager()

# Convenience functions
def get_user_data(user_type: str = 'default') -> TestUser:
    """Get user test data."""
    return test_data_manager.get_user_data(user_type)

def get_product_data(product_type: str = 'default') -> TestProduct:
    """Get product test data."""
    return test_data_manager.get_product_data(product_type)

def get_credentials(environment: str = None) -> Dict[str, str]:
    """Get test credentials."""
    return test_data_manager.get_test_credentials(environment)

def get_api_data(endpoint: str) -> Dict[str, Any]:
    """Get API test data."""
    return test_data_manager.get_api_test_data(endpoint)

def create_random_user() -> TestUser:
    """Create a random test user."""
    return UserFactory()

def create_random_product() -> TestProduct:
    """Create a random test product."""
    return ProductFactory()