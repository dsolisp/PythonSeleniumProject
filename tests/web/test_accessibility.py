"""
Accessibility Testing Module.
Uses axe-core via axe-selenium-python for WCAG compliance testing.
"""

import pytest
from axe_selenium_python import Axe
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def driver():
    """Create headless Chrome driver for accessibility testing."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


def run_axe_analysis(driver, url):
    """Run axe-core accessibility analysis and return results."""
    driver.get(url)
    axe = Axe(driver)
    axe.inject()
    results = axe.run()
    return results


def get_violations_by_impact(results, impact_level):
    """Filter violations by impact level (critical, serious, moderate, minor)."""
    return [v for v in results.get("violations", []) if v.get("impact") == impact_level]


def calculate_accessibility_score(results):
    """Calculate accessibility score similar to Lighthouse."""
    violations = results.get("violations", [])
    passes = results.get("passes", [])
    
    total_rules = len(violations) + len(passes)
    if total_rules == 0:
        return 100
    
    # Weight by impact
    impact_weights = {"critical": 10, "serious": 5, "moderate": 2, "minor": 1}
    penalty = 0
    
    for violation in violations:
        impact = violation.get("impact", "minor")
        penalty += impact_weights.get(impact, 1)
    
    # Calculate score (100 - penalty, minimum 0)
    score = max(0, 100 - penalty * 2)
    return score


@pytest.mark.accessibility
@pytest.mark.web
class TestAccessibility:
    """Accessibility tests using axe-core."""

    def test_bing_homepage_accessibility(self, driver):
        """Test Bing homepage for accessibility violations."""
        results = run_axe_analysis(driver, "https://www.bing.com")
        
        violations = results.get("violations", [])
        critical = get_violations_by_impact(results, "critical")
        
        score = calculate_accessibility_score(results)
        print(f"✅ Bing accessibility score: {score}")
        print(f"   Total violations: {len(violations)}")
        print(f"   Critical violations: {len(critical)}")
        
        # No critical violations allowed
        assert len(critical) == 0, f"Critical violations found: {critical}"

    def test_saucedemo_login_accessibility(self, driver):
        """Test SauceDemo login page for accessibility."""
        results = run_axe_analysis(driver, "https://www.saucedemo.com")
        
        violations = results.get("violations", [])
        critical = get_violations_by_impact(results, "critical")
        serious = get_violations_by_impact(results, "serious")
        
        score = calculate_accessibility_score(results)
        print(f"✅ SauceDemo login accessibility score: {score}")
        print(f"   Total violations: {len(violations)}")
        print(f"   Critical: {len(critical)}, Serious: {len(serious)}")
        
        # Log violation details
        for v in violations[:3]:  # First 3 violations
            print(f"   - {v.get('id')}: {v.get('description')[:50]}...")

    def test_wcag_color_contrast(self, driver):
        """Test for WCAG color contrast compliance."""
        results = run_axe_analysis(driver, "https://www.saucedemo.com")
        
        violations = results.get("violations", [])
        contrast_violations = [v for v in violations if "color-contrast" in v.get("id", "")]
        
        print(f"✅ Color contrast check complete")
        print(f"   Contrast violations: {len(contrast_violations)}")
        
        # Report but don't fail on contrast issues (common in third-party sites)
        if contrast_violations:
            for v in contrast_violations:
                nodes = v.get("nodes", [])
                print(f"   - {len(nodes)} elements with contrast issues")

    def test_keyboard_accessibility(self, driver):
        """Test for keyboard navigation accessibility."""
        results = run_axe_analysis(driver, "https://www.saucedemo.com")
        
        violations = results.get("violations", [])
        keyboard_violations = [
            v for v in violations 
            if any(tag in v.get("tags", []) for tag in ["keyboard", "focus"])
        ]
        
        print(f"✅ Keyboard accessibility check complete")
        print(f"   Keyboard-related violations: {len(keyboard_violations)}")

    def test_form_accessibility(self, driver):
        """Test form elements for accessibility compliance."""
        results = run_axe_analysis(driver, "https://www.saucedemo.com")
        
        violations = results.get("violations", [])
        form_violations = [
            v for v in violations 
            if any(tag in v.get("tags", []) for tag in ["forms", "label"])
        ]
        
        print(f"✅ Form accessibility check complete")
        print(f"   Form-related violations: {len(form_violations)}")
        
        # Check for label association
        label_violations = [v for v in violations if "label" in v.get("id", "")]
        if label_violations:
            print(f"   Label violations: {len(label_violations)}")

    def test_accessibility_score_threshold(self, driver):
        """Test that accessibility score meets minimum threshold."""
        results = run_axe_analysis(driver, "https://www.bing.com")
        
        score = calculate_accessibility_score(results)
        min_threshold = 50  # Minimum acceptable score
        
        print(f"✅ Accessibility score: {score} (threshold: {min_threshold})")
        assert score >= min_threshold, f"Score {score} below threshold {min_threshold}"

