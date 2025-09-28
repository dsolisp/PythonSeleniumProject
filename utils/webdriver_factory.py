"""
Enhanced WebDriver Factory with comprehensive browser support and configuration.
"""

import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import utils.sql_connection as sql_util

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_driver(browser='chrome', headless=False, window_size=None, download_dir=None):
    """
    Enhanced driver factory with comprehensive configuration options.
    
    Args:
        browser (str): Browser type ('chrome', 'firefox', 'edge')
        headless (bool): Run browser in headless mode
        window_size (tuple): Window size as (width, height)
        download_dir (str): Custom download directory
    
    Returns:
        tuple: (WebDriver instance, Database connection)
    """
    logger.info(f"Initializing {browser} driver with headless={headless}")
    
    try:
        if browser.lower() == 'chrome':
            driver = _create_chrome_driver(headless, window_size, download_dir)
        elif browser.lower() == 'firefox':
            driver = _create_firefox_driver(headless, window_size, download_dir)
        elif browser.lower() == 'edge':
            driver = _create_edge_driver(headless, window_size, download_dir)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        # Configure driver settings
        if not headless:
            driver.maximize_window()
        
        # Set custom window size if provided
        if window_size:
            driver.set_window_size(window_size[0], window_size[1])
            logger.info(f"Window size set to: {window_size}")
        
        # Set implicit wait
        implicit_wait = int(os.getenv('IMPLICIT_WAIT', '10'))
        driver.implicitly_wait(implicit_wait)
        
        # Navigate to initial URL
        initial_url = os.getenv('BASE_URL', 'https://www.google.com/')
        driver.get(initial_url)
        logger.info(f"Navigated to: {initial_url}")
        
        # Connect to database
        db_connection = connect_to_db()
        
        return driver, db_connection
        
    except Exception as e:
        logger.error(f"Failed to create {browser} driver: {str(e)}")
        raise


def _create_chrome_driver(headless=False, window_size=None, download_dir=None):
    """Create Chrome WebDriver with enhanced options."""
    options = ChromeOptions()
    
    # Performance optimizations
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # Faster loading
    
    # Security and privacy
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-certificate-errors')
    
    if headless:
        options.add_argument('--headless=new')  # Use new headless mode
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
    
    # Custom download directory
    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
    
    # Create service with automatic driver management
    service = ChromeService(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=options)


def _create_firefox_driver(headless=False, window_size=None, download_dir=None):
    """Create Firefox WebDriver with enhanced options."""
    options = FirefoxOptions()
    
    if headless:
        options.add_argument('--headless')
    
    # Custom download directory
    if download_dir:
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                             "application/octet-stream,application/pdf")
    
    # Performance optimizations
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("media.volume_scale", "0.0")
    
    service = FirefoxService(GeckoDriverManager().install())
    
    return webdriver.Firefox(service=service, options=options)


def _create_edge_driver(headless=False, window_size=None, download_dir=None):
    """Create Edge WebDriver with enhanced options."""
    options = EdgeOptions()
    
    # Similar to Chrome options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    if headless:
        options.add_argument('--headless')
    
    # Custom download directory
    if download_dir:
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
        }
        options.add_experimental_option("prefs", prefs)
    
    service = EdgeService(EdgeChromiumDriverManager().install())
    
    return webdriver.Edge(service=service, options=options)


def connect_to_db():
    """Enhanced database connection with better error handling."""
    try:
        db_file = os.getenv('DB_PATH', 'resources/chinook.db')
        
        if not os.path.exists(db_file):
            logger.warning(f"Database file not found: {db_file}")
            return None
            
        connection = sql_util.get_connection(db_file)
        logger.info(f"Database connection established: {db_file}")
        return connection
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        return None


def create_headless_driver(browser='chrome'):
    """Convenience method for creating headless drivers."""
    return get_driver(browser=browser, headless=True)


def create_mobile_driver(browser='chrome', device='iPhone 12'):
    """Create driver with mobile device emulation."""
    if browser.lower() != 'chrome':
        raise ValueError("Mobile emulation currently only supported for Chrome")
    
    options = ChromeOptions()
    mobile_emulation = {"deviceName": device}
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    logger.info(f"Mobile driver created with device emulation: {device}")
    return driver, connect_to_db()


def quit_driver_safely(driver):
    """Safely quit driver with proper cleanup."""
    try:
        if driver:
            driver.quit()
            logger.info("Driver quit successfully")
    except Exception as e:
        logger.error(f"Error quitting driver: {str(e)}")


# Environment-based configuration
def get_driver_from_env():
    """Create driver based on environment variables."""
    browser = os.getenv('BROWSER', 'chrome').lower()
    headless = os.getenv('HEADLESS', 'false').lower() == 'true'
    
    window_width = os.getenv('WINDOW_WIDTH')
    window_height = os.getenv('WINDOW_HEIGHT')
    window_size = None
    
    if window_width and window_height:
        window_size = (int(window_width), int(window_height))
    
    download_dir = os.getenv('DOWNLOAD_DIR')
    
    return get_driver(
        browser=browser,
        headless=headless,
        window_size=window_size,
        download_dir=download_dir
    )
