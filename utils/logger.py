import logging
import sys
from datetime import datetime
from config.settings import settings

class TestLogger:
    def __init__(self, name: str = "TestFramework"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            self._setup_handlers()
        # Override the logger's addHandler method to auto-format new handlers
        original_addHandler = self.logger.addHandler
        def auto_format_addHandler(handler):
            if handler.formatter is None:
                handler.setFormatter(self._get_default_formatter())
            return original_addHandler(handler)
        self.logger.addHandler = auto_format_addHandler

    def _setup_handlers(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S")
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        log_file = settings.LOGS_DIR / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
    def _get_default_formatter(self):
        """Get default formatter for new handlers."""
        return logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def test_start(self, test_name: str):
        self.info(f"🚀 STARTING TEST: {test_name}")

    def test_end(self, test_name: str, status: str, duration: float):
        emoji = "✅" if status == "PASSED" else "❌"
        self.info(f"{emoji} TEST COMPLETED: {test_name} | Status: {status} | Duration: {duration:.2f}s")

    def step(self, description: str):
        self.info(f"  📋 STEP: {description}")

    def separator(self):
        self.info("=" * 80)

    def exception(self, message: str, exception: Exception):
        self.logger.exception(f"{message}: {str(exception)}")

    def screenshot(self, path: str):
        self.info(f"Screenshot saved: {path}")

    def api_call(self, method: str, url: str, status_code: int):
        self.info(f"API {method} {url} -> {status_code}")

    def database_query(self, query_type: str, table: str = ""):
        table_info = f" on {table}" if table else ""
        self.info(f"Database {query_type}{table_info}")

logger = TestLogger()

def info(message: str):
    logger.info(message)

def debug(message: str):
    logger.debug(message)

def warning(message: str):
    logger.warning(message)

def error(message: str):
    logger.error(message)

def test_start(test_name: str):
    logger.test_start(test_name)

def test_end(test_name: str, status: str, duration: float):
    logger.test_end(test_name, status, duration)

def step(description: str):
    logger.step(description)

def separator():
    logger.separator()

def exception(message: str, exc: Exception):
    logger.exception(message, exc)

def screenshot(path: str):
    logger.screenshot(path)

def api_call(method: str, url: str, status_code: int):
    logger.api_call(method, url, status_code)

def database_query(query_type: str, table: str = ""):
    logger.database_query(query_type, table)
