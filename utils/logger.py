"""
Enhanced logging configuration for the QA automation framework.
Provides structured logging with multiple outputs and security features.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import structlog
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from config.settings import settings


class SecurityFilter(logging.Filter):
    """Filter to mask sensitive information in logs."""
    
    SENSITIVE_PATTERNS = [
        'password', 'token', 'key', 'secret', 'credential',
        'auth', 'bearer', 'session', 'cookie'
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        if settings.mask_sensitive_logs:
            message = str(record.getMessage()).lower()
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern in message:
                    record.msg = self._mask_sensitive_data(record.msg)
        return True
    
    def _mask_sensitive_data(self, message: str) -> str:
        """Mask sensitive data in log messages."""
        # Simple masking - in production, use more sophisticated regex patterns
        return message.replace(message, "[MASKED SENSITIVE DATA]")


class TestLogger:
    """Enhanced logger for test automation framework."""
    
    def __init__(self):
        self.logger = None
        self._setup_logging()
        self._setup_sentry()
    
    def _setup_logging(self):
        """Configure structured logging with multiple handlers."""
        # Remove default loguru handler
        logger.remove()
        
        # Console handler with colors
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level=settings.log_level.value,
            colorize=True,
            enqueue=True
        )
        
        # File handler for all logs
        log_file = settings.logs_dir / "test_automation.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            enqueue=True
        )
        
        # Separate file for errors
        error_file = settings.logs_dir / "errors.log"
        logger.add(
            error_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            enqueue=True
        )
        
        # JSON file for structured logs (for log aggregation systems)
        json_file = settings.logs_dir / "structured.json"
        logger.add(
            json_file,
            format=lambda record: self._json_formatter(record),
            level="INFO",
            rotation="50 MB",
            retention="30 days",
            compression="zip",
            enqueue=True
        )
        
        self.logger = logger
    
    def _json_formatter(self, record) -> str:
        """Format log record as JSON."""
        import json
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "thread": record["thread"].name,
            "process": record["process"].name,
            "environment": settings.environment.value
        }
        
        # Add extra context if available
        if "extra" in record:
            log_entry.update(record["extra"])
        
        return json.dumps(log_entry)
    
    def _setup_sentry(self):
        """Configure Sentry for error tracking in non-local environments."""
        if settings.environment != "local" and os.getenv("SENTRY_DSN"):
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=os.getenv("SENTRY_DSN"),
                integrations=[sentry_logging],
                environment=settings.environment.value,
                traces_sample_rate=0.1,
                send_default_pii=False
            )
    
    def log_test_start(self, test_name: str, test_id: Optional[str] = None):
        """Log test execution start."""
        self.logger.info(
            "Test started",
            extra={
                "test_name": test_name,
                "test_id": test_id,
                "event_type": "test_start"
            }
        )
    
    def log_test_end(self, test_name: str, status: str, duration: float, test_id: Optional[str] = None):
        """Log test execution end."""
        self.logger.info(
            f"Test {status.lower()}",
            extra={
                "test_name": test_name,
                "test_id": test_id,
                "status": status,
                "duration": duration,
                "event_type": "test_end"
            }
        )
    
    def log_step(self, step_description: str, step_data: Optional[Dict[str, Any]] = None):
        """Log test step execution."""
        self.logger.info(
            f"Step: {step_description}",
            extra={
                "step_description": step_description,
                "step_data": step_data or {},
                "event_type": "test_step"
            }
        )
    
    def log_screenshot(self, screenshot_path: str, test_name: str):
        """Log screenshot capture."""
        self.logger.info(
            "Screenshot captured",
            extra={
                "screenshot_path": screenshot_path,
                "test_name": test_name,
                "event_type": "screenshot"
            }
        )
    
    def log_api_request(self, method: str, url: str, status_code: int, response_time: float):
        """Log API request details."""
        self.logger.info(
            f"API Request: {method} {url}",
            extra={
                "method": method,
                "url": url,
                "status_code": status_code,
                "response_time": response_time,
                "event_type": "api_request"
            }
        )
    
    def log_database_operation(self, operation: str, table: str, duration: float):
        """Log database operation."""
        self.logger.info(
            f"Database operation: {operation} on {table}",
            extra={
                "operation": operation,
                "table": table,
                "duration": duration,
                "event_type": "database_operation"
            }
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        self.logger.error(
            f"Error occurred: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
                "event_type": "error"
            }
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log performance metrics."""
        self.logger.info(
            f"Performance metric: {metric_name} = {value}{unit}",
            extra={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "event_type": "performance_metric"
            }
        )


# Global logger instance
test_logger = TestLogger()

# Convenience functions
def log_test_start(test_name: str, test_id: Optional[str] = None):
    test_logger.log_test_start(test_name, test_id)

def log_test_end(test_name: str, status: str, duration: float, test_id: Optional[str] = None):
    test_logger.log_test_end(test_name, status, duration, test_id)

def log_step(step_description: str, step_data: Optional[Dict[str, Any]] = None):
    test_logger.log_step(step_description, step_data)

def log_screenshot(screenshot_path: str, test_name: str):
    test_logger.log_screenshot(screenshot_path, test_name)

def log_api_request(method: str, url: str, status_code: int, response_time: float):
    test_logger.log_api_request(method, url, status_code, response_time)

def log_database_operation(operation: str, table: str, duration: float):
    test_logger.log_database_operation(operation, table, duration)

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    test_logger.log_error(error, context)

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    test_logger.log_performance_metric(metric_name, value, unit)