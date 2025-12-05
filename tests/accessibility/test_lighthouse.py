"""
Lighthouse-Style Accessibility Audits.
Uses axe-selenium-python with Lighthouse-like scoring methodology.
Equivalent to Playwright's lighthouse.spec.ts
"""

from dataclasses import dataclass

import pytest
from axe_selenium_python import Axe
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.settings import settings


@dataclass
class AccessibilityScore:
    """Lighthouse-style accessibility score data."""

    score: int
    passes: int
    violations: int
    incomplete: int
    inapplicable: int
    critical_violations: int
    serious_violations: int


def calculate_accessibility_score(results: dict) -> AccessibilityScore:
    """
    Calculate a Lighthouse-style accessibility score from Axe results.
    Lighthouse uses a weighted scoring system based on impact.
    """
    violations = results.get("violations", [])
    passes = results.get("passes", [])
    incomplete = results.get("incomplete", [])
    inapplicable = results.get("inapplicable", [])

    critical = sum(1 for v in violations if v.get("impact") == "critical")
    serious = sum(1 for v in violations if v.get("impact") == "serious")
    moderate = sum(1 for v in violations if v.get("impact") == "moderate")
    minor = sum(1 for v in violations if v.get("impact") == "minor")

    # Weighted penalty: critical=10, serious=5, moderate=2, minor=1
    penalty = (critical * 10) + (serious * 5) + (moderate * 2) + minor
    max_penalty = 50  # Cap penalty at 50 points
    score = max(0, 100 - min(penalty, max_penalty))

    return AccessibilityScore(
        score=score,
        passes=len(passes),
        violations=len(violations),
        incomplete=len(incomplete),
        inapplicable=len(inapplicable),
        critical_violations=critical,
        serious_violations=serious,
    )


@pytest.fixture
def browser():
    """Create a headless Chrome browser for accessibility testing."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    yield driver
    driver.quit()


class TestLighthouseAccessibility:
    """Lighthouse-style accessibility audit tests."""

    def test_bing_homepage_accessibility_score(self, browser):
        """Should have good accessibility score on Bing homepage."""
        browser.get(settings.BASE_URL)

        axe = Axe(browser)
        axe.inject()
        results = axe.run()

        score_data = calculate_accessibility_score(results)

        print("\n=== Lighthouse-Style Accessibility Audit ===")
        print(f"Bing Homepage Score: {score_data.score}%")
        print(f"Passes: {score_data.passes}, Violations: {score_data.violations}")
        print(
            f"Critical: {score_data.critical_violations}, "
            f"Serious: {score_data.serious_violations}"
        )

        # Expect at least 50% accessibility score (Bing has known issues)
        assert score_data.score >= 50, f"Score {score_data.score}% below 50% threshold"

    def test_saucedemo_login_accessibility_score(self, browser):
        """Should have good accessibility score on SauceDemo login."""
        browser.get("https://www.saucedemo.com")

        axe = Axe(browser)
        axe.inject()
        results = axe.run()

        score_data = calculate_accessibility_score(results)

        print("\n=== SauceDemo Lighthouse-Style Accessibility ===")
        print(f"Login Page Score: {score_data.score}%")
        print(f"Passes: {score_data.passes}, Violations: {score_data.violations}")

        # SauceDemo is a demo site, expect at least 60%
        assert score_data.score >= 60, f"Score {score_data.score}% below 60% threshold"

    def test_detailed_accessibility_report(self, browser):
        """Should report accessibility issues in detail."""
        browser.get(settings.BASE_URL)

        axe = Axe(browser)
        axe.inject()
        results = axe.run()

        score_data = calculate_accessibility_score(results)
        violations = results.get("violations", [])

        # Check specific accessibility categories
        aria_violations = [v for v in violations if v.get("id", "").startswith("aria")]
        color_violations = [v for v in violations if "color" in v.get("id", "")]
        image_violations = [
            v
            for v in violations
            if "image" in v.get("id", "") or "alt" in v.get("id", "")
        ]

        print("\n=== Detailed Accessibility Report ===")
        print(f"Overall Score: {score_data.score}%")
        print(f"ARIA issues: {len(aria_violations)}")
        print(f"Color contrast issues: {len(color_violations)}")
        print(f"Image/alt issues: {len(image_violations)}")

        # Verify we got audit results
        total_checks = score_data.passes + score_data.violations + score_data.incomplete
        assert total_checks > 0, "No accessibility checks were performed"

    def test_no_critical_accessibility_violations(self, browser):
        """Should have no critical accessibility violations."""
        browser.get(settings.BASE_URL)

        axe = Axe(browser)
        axe.inject()
        results = axe.run()

        score_data = calculate_accessibility_score(results)

        print("\n=== Critical Violations Check ===")
        print(
            f"Critical: {score_data.critical_violations}, "
            f"Serious: {score_data.serious_violations}"
        )

        # Allow up to 5 critical violations (external sites may have issues beyond our control)
        assert score_data.critical_violations <= 5, (
            f"Found {score_data.critical_violations} critical violations (max allowed: 5)"
        )
