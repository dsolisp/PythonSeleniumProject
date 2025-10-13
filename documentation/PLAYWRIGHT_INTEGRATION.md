# Playwright Integration Guide

## Overview

Modern async browser automation with **Playwright** for cross-browser testing, mobile emulation, and network interception.

## 🎯 When to Use

- **Modern web apps**: Testing SPAs and PWAs
- **Mobile testing**: Device emulation without physical devices
- **Network testing**: Intercept and mock network requests
- **Multi-browser**: Test across Chromium, Firefox, WebKit
- **Performance**: Faster execution with async/await patterns
- **Auto-waiting**: Built-in smart waiting for elements

## 🔧 Setup

### Installation

```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browsers (one-time setup)
playwright install

# Install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
```

## 🚀 Basic Usage

### Simple Test

```python
import pytest
from playwright.sync_api import Page, expect

def test_basic_navigation(page: Page):
    """Basic Playwright test."""
    page.goto("https://example.com")
    
    # Auto-waiting built-in
    expect(page).to_have_title("Example Domain")
    
    # Find and interact with elements
    heading = page.locator("h1")
    expect(heading).to_have_text("Example Domain")
```

### Async Pattern

```python
import pytest
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_async_navigation():
    """Async Playwright test for faster execution."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        
        title = await page.title()
        assert "Example" in title
        
        await browser.close()
```

## 🎨 Key Features

### 1. Auto-Waiting

**No explicit waits needed** - Playwright automatically waits for elements:

```python
def test_auto_waiting(page: Page):
    page.goto("https://example.com")
    
    # Automatically waits for element to be:
    # - Attached to DOM
    # - Visible
    # - Stable
    # - Enabled
    # - Not covered by other elements
    page.locator("#submit-button").click()
```

### 2. Mobile Device Emulation

```python
import pytest
from playwright.sync_api import sync_playwright

def test_mobile_emulation():
    """Test on iPhone 12."""
    with sync_playwright() as p:
        # Launch with device emulation
        iphone = p.devices['iPhone 12']
        browser = p.chromium.launch()
        context = browser.new_context(**iphone)
        page = context.new_page()
        
        page.goto("https://example.com")
        
        # Test mobile-specific features
        assert page.viewport_size == {'width': 390, 'height': 844}
        
        browser.close()

# Available devices
devices = [
    'iPhone 12',
    'iPhone 12 Pro',
    'Pixel 5',
    'Galaxy S9+',
    'iPad Pro',
    # ... and many more
]
```

### 3. Network Interception

```python
def test_network_interception(page: Page):
    """Intercept and mock network requests."""
    
    # Mock API response
    def handle_route(route):
        if 'api/users' in route.request.url:
            route.fulfill(
                status=200,
                body='{"users": [{"name": "Test User"}]}'
            )
        else:
            route.continue_()
    
    page.route('**/*', handle_route)
    
    page.goto("https://example.com")
    
    # Verify mocked data appears
    expect(page.locator('.user-name')).to_have_text("Test User")
```

### 4. Multi-Browser Testing

```python
import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.parametrize("browser_type", ["chromium", "firefox", "webkit"])
def test_cross_browser(browser_type):
    """Test across all browsers."""
    with sync_playwright() as p:
        browser = getattr(p, browser_type).launch()
        page = browser.new_page()
        
        page.goto("https://example.com")
        expect(page).to_have_title("Example Domain")
        
        browser.close()
```

### 5. Screenshots and Videos

```python
def test_with_screenshots(page: Page):
    """Capture screenshots and videos."""
    page.goto("https://example.com")
    
    # Full page screenshot
    page.screenshot(path="full_page.png", full_page=True)
    
    # Element screenshot
    page.locator("#header").screenshot(path="header.png")

# Configure video recording in pytest.ini
# [pytest]
# playwright_video_dir = screenshots/videos/
# playwright_video_retain_on_failure = true
```

### 6. Performance Metrics

```python
def test_performance_metrics(page: Page):
    """Monitor Core Web Vitals."""
    page.goto("https://example.com")
    
    # Get performance metrics
    metrics = page.evaluate('''() => {
        const paint = performance.getEntriesByType('paint');
        const navigation = performance.getEntriesByType('navigation')[0];
        
        return {
            fcp: paint.find(entry => entry.name === 'first-contentful-paint')?.startTime,
            lcp: performance.getEntriesByType('largest-contentful-paint')[0]?.startTime,
            loadTime: navigation?.loadEventEnd - navigation?.fetchStart
        };
    }''')
    
    # Assert performance thresholds
    assert metrics['fcp'] < 1800  # First Contentful Paint < 1.8s
    assert metrics['lcp'] < 2500  # Largest Contentful Paint < 2.5s
    assert metrics['loadTime'] < 3000  # Load time < 3s
```

## 🎯 Real-World Examples

### Example 1: Google Search

```python
# tests/web/test_playwright_search_engine.py
import pytest
from playwright.sync_api import Page, expect

def test_google_search_basic(page: Page):
    """Basic Google search with Playwright."""
    page.goto("https://www.google.com")
    
    # Handle cookie consent if present
    try:
        page.click("button:has-text('Accept all')", timeout=3000)
    except:
        pass
    
    # Search
    page.fill('textarea[name="q"]', "Playwright Python")
    page.press('textarea[name="q"]', "Enter")
    
    # Verify results
    expect(page.locator("#search")).to_be_visible()
    expect(page.locator("h3").first).to_be_visible()
```

### Example 2: Form Testing

```python
def test_form_submission(page: Page):
    """Test form with multiple input types."""
    page.goto("https://example.com/form")
    
    # Text input
    page.fill("#name", "John Doe")
    
    # Dropdown
    page.select_option("#country", "US")
    
    # Checkbox
    page.check("#terms")
    
    # Radio button
    page.click("input[name='gender'][value='male']")
    
    # File upload
    page.set_input_files("#avatar", "test_image.png")
    
    # Submit
    page.click("button[type='submit']")
    
    # Verify success
    expect(page.locator(".success-message")).to_be_visible()
```

### Example 3: SPA Navigation

```python
def test_single_page_app(page: Page):
    """Test Single Page Application routing."""
    page.goto("https://example.com/app")
    
    # Navigate through SPA
    page.click("a[href='/about']")
    expect(page).to_have_url("https://example.com/app/about")
    
    page.click("a[href='/products']")
    expect(page).to_have_url("https://example.com/app/products")
    
    # Verify client-side routing (no full page reload)
    assert page.evaluate("() => window.performance.navigation.type") == 0
```

### Example 4: Authentication Flow

```python
def test_login_flow(page: Page):
    """Test complete login flow."""
    page.goto("https://example.com/login")
    
    # Enter credentials
    page.fill("#username", "testuser")
    page.fill("#password", "password123")
    
    # Click login
    page.click("button:has-text('Login')")
    
    # Wait for navigation
    page.wait_for_url("**/dashboard")
    
    # Verify logged in
    expect(page.locator(".user-profile")).to_contain_text("testuser")
    
    # Logout
    page.click(".logout-button")
    expect(page).to_have_url("**/login")
```

### Example 5: API Mocking

```python
def test_with_mocked_api(page: Page):
    """Test UI with mocked backend."""
    
    # Mock API responses
    page.route("**/api/products", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"id": 1, "name": "Test Product", "price": 99.99}]'
    ))
    
    page.goto("https://example.com/products")
    
    # Verify mocked data renders
    expect(page.locator(".product-name")).to_have_text("Test Product")
    expect(page.locator(".product-price")).to_have_text("$99.99")
```

## 🏃 Running Playwright Tests

```bash
# Run all Playwright tests
pytest tests/web/test_playwright_*.py -v

# Run specific test
pytest tests/web/test_playwright_search_engine.py::test_google_search_basic -v

# Run in headed mode (see browser)
pytest tests/web/test_playwright_search_engine.py --headed

# Run with specific browser
pytest tests/web/test_playwright_search_engine.py --browser firefox
pytest tests/web/test_playwright_search_engine.py --browser webkit

# Run with slow motion (for debugging)
pytest tests/web/test_playwright_search_engine.py --headed --slowmo 1000

# Generate trace for debugging
pytest tests/web/test_playwright_search_engine.py --tracing on
```

## 🔧 Configuration

### pytest.ini

```ini
[pytest]
# Playwright specific settings
playwright_headed = false
playwright_slow_mo = 0
playwright_video_dir = screenshots/videos/
playwright_screenshot_dir = screenshots/
playwright_trace_dir = traces/

# Browser selection
playwright_browsers = chromium,firefox,webkit

# Timeout settings
playwright_timeout = 30000
```

### Fixtures

```python
# conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Customize browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "videos/",
        "record_video_size": {"width": 1920, "height": 1080}
    }

@pytest.fixture
def authenticated_page(page):
    """Fixture for authenticated page."""
    page.goto("https://example.com/login")
    page.fill("#username", "testuser")
    page.fill("#password", "password123")
    page.click("button:has-text('Login')")
    page.wait_for_url("**/dashboard")
    return page
```

## 💡 Best Practices

1. **Use auto-waiting**: Leverage Playwright's built-in waiting
2. **Expect assertions**: Use `expect()` instead of `assert`
3. **Locator strategies**: Prefer user-facing attributes (text, role, label)
4. **Mobile testing**: Test responsive designs with device emulation
5. **Network mocking**: Test edge cases with mocked responses
6. **Parallel execution**: Run tests concurrently for speed
7. **Trace debugging**: Use traces to debug failed tests

## 📊 Comparison: Playwright vs Selenium

| Feature | Playwright | Selenium |
|---------|-----------|----------|
| **Speed** | Faster (async) | Slower |
| **Auto-waiting** | Built-in | Manual waits |
| **Multi-browser** | Chromium, Firefox, WebKit | All major browsers |
| **Mobile emulation** | Excellent | Limited |
| **Network interception** | Native | Requires proxy |
| **Learning curve** | Moderate | Lower |
| **Community** | Growing | Mature |

## 📚 Related Documentation

- [Web UI Testing](WEB_UI_TESTING.md) - Selenium-based tests
- [Performance Monitoring](PERFORMANCE_MONITORING.md) - Performance metrics
- [API Testing](API_TESTING.md) - API automation

## 🔗 File Locations

- **Tests**: `tests/web/test_playwright_*.py`
- **Factory**: `utils/playwright_factory.py`
- **Locators**: `locators/playwright_search_engine_locators.py`
- **Screenshots**: `screenshots/`
- **Videos**: `videos/`

---

**Value Proposition**: Modern, fast browser automation with built-in best practices - test across browsers and devices without complex setup or explicit waits.
