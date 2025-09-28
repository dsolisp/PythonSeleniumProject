"""
Enhanced WebDriver Factory with support for multiple browsers,
cloud providers, mobile testing, and advanced configuration.
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
import time

from config.settings import settings, BrowserType, get_browser_options
from utils.logger import test_logger
from utils.sql_connection import DatabaseManager


class CloudProvider(str, Enum):
    BROWSERSTACK = "browserstack"
    SAUCE_LABS = "sauce_labs"
    LOCAL = "local"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class WebDriverFactory:
    """Enhanced WebDriver factory with comprehensive browser and device support."""
    
    def __init__(self):
        self.drivers: List[webdriver.Remote] = []
        self.db_manager = DatabaseManager()
        
    def create_driver(
        self,
        browser: BrowserType = None,
        cloud_provider: CloudProvider = CloudProvider.LOCAL,
        capabilities: Optional[Dict[str, Any]] = None,
        device_type: DeviceType = DeviceType.DESKTOP
    ) -> Tuple[webdriver.Remote, DatabaseManager]:
        """Create a WebDriver instance with specified configuration."""
        
        browser = browser or settings.default_browser
        start_time = time.time()
        
        try:
            if cloud_provider == CloudProvider.LOCAL:
                driver = self._create_local_driver(browser, capabilities)
            elif cloud_provider == CloudProvider.BROWSERSTACK:
                driver = self._create_browserstack_driver(browser, capabilities)
            elif cloud_provider == CloudProvider.SAUCE_LABS:
                driver = self._create_saucelabs_driver(browser, capabilities)
            else:
                raise ValueError(f"Unsupported cloud provider: {cloud_provider}")
            
            # Configure driver
            self._configure_driver(driver, device_type)
            
            # Track driver instance
            self.drivers.append(driver)
            
            # Connect to database
            db_connection = self.db_manager.get_connection()
            
            creation_time = time.time() - start_time
            test_logger.log_performance_metric(
                "driver_creation_time", 
                creation_time * 1000, 
                "ms"
            )
            
            test_logger.logger.info(
                f"WebDriver created successfully",
                extra={
                    "browser": browser.value,
                    "cloud_provider": cloud_provider.value,
                    "device_type": device_type.value,
                    "creation_time": creation_time
                }
            )
            
            return driver, db_connection
            
        except Exception as e:
            test_logger.log_error(e, {
                "browser": browser.value,
                "cloud_provider": cloud_provider.value,
                "operation": "driver_creation"
            })
            raise
    
    def _create_local_driver(
        self, 
        browser: BrowserType, 
        capabilities: Optional[Dict[str, Any]] = None
    ) -> webdriver.Remote:
        """Create a local WebDriver instance."""
        
        if browser == BrowserType.CHROME:
            return self._create_chrome_driver(capabilities)
        elif browser == BrowserType.FIREFOX:
            return self._create_firefox_driver(capabilities)
        elif browser == BrowserType.SAFARI:
            return self._create_safari_driver(capabilities)
        elif browser == BrowserType.EDGE:
            return self._create_edge_driver(capabilities)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
    
    def _create_chrome_driver(self, capabilities: Optional[Dict[str, Any]] = None) -> webdriver.Chrome:
        """Create Chrome WebDriver with enhanced options."""
        options = ChromeOptions()
        
        # Basic options
        if settings.headless:
            options.add_argument("--headless=new")
        
        # Performance and stability options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")
        
        # Window size
        if not settings.headless:
            options.add_argument("--start-maximized")
        else:
            options.add_argument("--window-size=1920,1080")
        
        # Logging
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Custom capabilities
        if capabilities:
            for key, value in capabilities.items():
                options.set_capability(key, value)
        
        # Create service
        service = ChromeService(ChromeDriverManager().install())
        
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self, capabilities: Optional[Dict[str, Any]] = None) -> webdriver.Firefox:
        """Create Firefox WebDriver with enhanced options."""
        options = FirefoxOptions()
        
        if settings.headless:
            options.add_argument("--headless")
        
        # Performance options
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("media.volume_scale", "0.0")
        
        # Custom capabilities
        if capabilities:
            for key, value in capabilities.items():
                options.set_capability(key, value)
        
        service = FirefoxService(GeckoDriverManager().install())
        
        return webdriver.Firefox(service=service, options=options)
    
    def _create_safari_driver(self, capabilities: Optional[Dict[str, Any]] = None) -> webdriver.Safari:
        """Create Safari WebDriver."""
        options = SafariOptions()
        
        if capabilities:
            for key, value in capabilities.items():
                options.set_capability(key, value)
        
        return webdriver.Safari(options=options)
    
    def _create_edge_driver(self, capabilities: Optional[Dict[str, Any]] = None) -> webdriver.Edge:
        """Create Edge WebDriver with enhanced options."""
        options = EdgeOptions()
        
        if settings.headless:
            options.add_argument("--headless=new")
        
        # Use Chrome-like options for Edge
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if capabilities:
            for key, value in capabilities.items():
                options.set_capability(key, value)
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        return webdriver.Edge(service=service, options=options)
    
    def _create_browserstack_driver(
        self, 
        browser: BrowserType, 
        capabilities: Optional[Dict[str, Any]] = None
    ) -> webdriver.Remote:
        """Create BrowserStack remote WebDriver."""
        
        if not settings.browserstack_username or not settings.browserstack_access_key:
            raise ValueError("BrowserStack credentials not configured")
        
        bs_capabilities = {
            "browserName": browser.value,
            "browserVersion": "latest",
            "os": "Windows",
            "osVersion": "11",
            "resolution": "1920x1080",
            "name": "Automated Test",
            "build": f"Build-{int(time.time())}",
            "project": "QA Automation Framework"
        }
        
        if capabilities:
            bs_capabilities.update(capabilities)
        
        hub_url = f"https://{settings.browserstack_username}:{settings.browserstack_access_key}@hub-cloud.browserstack.com/wd/hub"
        
        return webdriver.Remote(
            command_executor=hub_url,
            desired_capabilities=bs_capabilities
        )
    
    def _create_saucelabs_driver(
        self, 
        browser: BrowserType, 
        capabilities: Optional[Dict[str, Any]] = None
    ) -> webdriver.Remote:
        """Create Sauce Labs remote WebDriver."""
        
        if not settings.sauce_labs_username or not settings.sauce_labs_access_key:
            raise ValueError("Sauce Labs credentials not configured")
        
        sauce_capabilities = {
            "browserName": browser.value,
            "browserVersion": "latest",
            "platformName": "Windows 11",
            "sauce:options": {
                "name": "Automated Test",
                "build": f"Build-{int(time.time())}"
            }
        }
        
        if capabilities:
            sauce_capabilities.update(capabilities)
        
        hub_url = f"https://{settings.sauce_labs_username}:{settings.sauce_labs_access_key}@ondemand.us-west-1.saucelabs.com:443/wd/hub"
        
        return webdriver.Remote(
            command_executor=hub_url,
            desired_capabilities=sauce_capabilities
        )
    
    def create_mobile_driver(
        self,
        platform: str,
        device_name: str,
        app_path: Optional[str] = None,
        capabilities: Optional[Dict[str, Any]] = None
    ) -> Tuple[webdriver.Remote, DatabaseManager]:
        """Create mobile WebDriver for iOS or Android."""
        
        if platform.lower() == "android":
            options = UiAutomator2Options()
            options.device_name = device_name
            options.platform_name = "Android"
            
            if app_path:
                options.app = app_path
            else:
                options.browser_name = "Chrome"
            
        elif platform.lower() == "ios":
            options = XCUITestOptions()
            options.device_name = device_name
            options.platform_name = "iOS"
            
            if app_path:
                options.app = app_path
            else:
                options.browser_name = "Safari"
        else:
            raise ValueError(f"Unsupported mobile platform: {platform}")
        
        if capabilities:
            for key, value in capabilities.items():
                options.set_capability(key, value)
        
        driver = appium_webdriver.Remote(
            settings.appium_server_url,
            options=options
        )
        
        self.drivers.append(driver)
        db_connection = self.db_manager.get_connection()
        
        return driver, db_connection
    
    def _configure_driver(self, driver: webdriver.Remote, device_type: DeviceType):
        """Configure WebDriver with common settings."""
        
        # Set timeouts
        driver.set_page_load_timeout(settings.page_load_timeout)
        driver.implicitly_wait(settings.implicit_wait)
        
        # Window management for desktop browsers
        if device_type == DeviceType.DESKTOP and settings.window_maximize:
            try:
                driver.maximize_window()
            except Exception as e:
                test_logger.logger.warning(f"Could not maximize window: {e}")
    
    def quit_all_drivers(self):
        """Quit all active WebDriver instances."""
        for driver in self.drivers:
            try:
                driver.quit()
            except Exception as e:
                test_logger.logger.warning(f"Error quitting driver: {e}")
        
        self.drivers.clear()
        
        # Close database connections
        self.db_manager.close_all_connections()
    
    def get_driver_info(self, driver: webdriver.Remote) -> Dict[str, Any]:
        """Get information about the WebDriver instance."""
        try:
            capabilities = driver.capabilities
            return {
                "browser_name": capabilities.get("browserName"),
                "browser_version": capabilities.get("browserVersion"),
                "platform": capabilities.get("platformName"),
                "session_id": driver.session_id
            }
        except Exception as e:
            test_logger.log_error(e, {"operation": "get_driver_info"})
            return {}


# Global factory instance
webdriver_factory = WebDriverFactory()

# Convenience functions
def get_driver(
    browser: BrowserType = None,
    cloud_provider: CloudProvider = CloudProvider.LOCAL,
    capabilities: Optional[Dict[str, Any]] = None
) -> Tuple[webdriver.Remote, DatabaseManager]:
    """Get a WebDriver instance with database connection."""
    return webdriver_factory.create_driver(browser, cloud_provider, capabilities)

def get_mobile_driver(
    platform: str,
    device_name: str,
    app_path: Optional[str] = None,
    capabilities: Optional[Dict[str, Any]] = None
) -> Tuple[webdriver.Remote, DatabaseManager]:
    """Get a mobile WebDriver instance with database connection."""
    return webdriver_factory.create_mobile_driver(platform, device_name, app_path, capabilities)

def quit_all_drivers():
    """Quit all active WebDriver instances."""
    webdriver_factory.quit_all_drivers()