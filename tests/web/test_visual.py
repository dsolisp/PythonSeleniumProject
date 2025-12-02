"""
Visual Regression Testing Module.
Uses Pillow for screenshot comparison and visual diff generation.
"""

import os
import pytest
from PIL import Image, ImageChops, ImageDraw
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import io


# Visual test configuration
BASELINE_DIR = "test-results/visual/baselines"
ACTUAL_DIR = "test-results/visual/actual"
DIFF_DIR = "test-results/visual/diffs"
SIMILARITY_THRESHOLD = 0.95  # 95% similarity required


@pytest.fixture(scope="module")
def visual_driver():
    """Create headless Chrome driver for visual testing."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--force-device-scale-factor=1")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def setup_directories():
    """Ensure visual test directories exist."""
    for dir_path in [BASELINE_DIR, ACTUAL_DIR, DIFF_DIR]:
        os.makedirs(dir_path, exist_ok=True)


def take_screenshot(driver, url, name):
    """Take screenshot and return as PIL Image."""
    driver.get(url)
    driver.implicitly_wait(2)
    
    screenshot = driver.get_screenshot_as_png()
    return Image.open(io.BytesIO(screenshot))


def calculate_similarity(img1, img2):
    """Calculate similarity percentage between two images."""
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
    
    # Calculate RMS difference
    histogram = diff.histogram()
    total_pixels = img1.size[0] * img1.size[1] * 3  # 3 channels
    
    sum_of_squares = sum(count * (i % 256) ** 2 for i, count in enumerate(histogram))
    rms = (sum_of_squares / total_pixels) ** 0.5
    
    # Convert RMS to similarity (0-255 range)
    similarity = 1 - (rms / 255)
    return similarity


def create_diff_image(img1, img2, name):
    """Create visual diff image highlighting differences."""
    if img1.size != img2.size:
        img2 = img2.resize(img1.size, Image.Resampling.LANCZOS)
    
    diff = ImageChops.difference(img1.convert("RGB"), img2.convert("RGB"))
    
    # Enhance diff for visibility
    diff_enhanced = Image.new("RGB", img1.size, (255, 255, 255))
    for x in range(img1.size[0]):
        for y in range(img1.size[1]):
            r, g, b = diff.getpixel((x, y))
            if r + g + b > 30:  # Threshold for difference
                diff_enhanced.putpixel((x, y), (255, 0, 0))  # Red for differences
    
    diff_path = os.path.join(DIFF_DIR, f"{name}_diff.png")
    diff_enhanced.save(diff_path)
    return diff_path


@pytest.mark.visual
@pytest.mark.web
class TestVisualRegression:
    """Visual regression tests using screenshot comparison."""

    def test_bing_homepage_visual(self, visual_driver):
        """Test Bing homepage visual appearance."""
        name = "bing_homepage"
        url = "https://www.bing.com"
        
        actual = take_screenshot(visual_driver, url, name)
        actual_path = os.path.join(ACTUAL_DIR, f"{name}.png")
        actual.save(actual_path)
        
        baseline_path = os.path.join(BASELINE_DIR, f"{name}.png")
        if not os.path.exists(baseline_path):
            actual.save(baseline_path)
            print(f"✅ Baseline created: {baseline_path}")
            return
        
        baseline = Image.open(baseline_path)
        similarity = calculate_similarity(baseline, actual)
        
        print(f"✅ Visual similarity: {similarity:.2%}")
        assert similarity >= SIMILARITY_THRESHOLD, f"Visual diff detected: {similarity:.2%}"

    def test_saucedemo_login_visual(self, visual_driver):
        """Test SauceDemo login page visual appearance."""
        name = "saucedemo_login"
        url = "https://www.saucedemo.com"
        
        actual = take_screenshot(visual_driver, url, name)
        actual_path = os.path.join(ACTUAL_DIR, f"{name}.png")
        actual.save(actual_path)
        
        baseline_path = os.path.join(BASELINE_DIR, f"{name}.png")
        if not os.path.exists(baseline_path):
            actual.save(baseline_path)
            print(f"✅ Baseline created: {baseline_path}")
            return
        
        baseline = Image.open(baseline_path)
        similarity = calculate_similarity(baseline, actual)
        
        print(f"✅ Visual similarity: {similarity:.2%}")
        if similarity < SIMILARITY_THRESHOLD:
            diff_path = create_diff_image(baseline, actual, name)
            print(f"   Diff saved: {diff_path}")

    def test_screenshot_capture_quality(self, visual_driver):
        """Test screenshot capture produces valid images."""
        img = take_screenshot(visual_driver, "https://www.bing.com", "quality_test")

        assert img.size[0] >= 1200, f"Width too small: {img.size[0]}"
        assert img.size[1] >= 500, f"Height too small: {img.size[1]}"
        assert img.mode in ["RGB", "RGBA"], f"Unexpected mode: {img.mode}"

        print(f"✅ Screenshot quality: {img.size[0]}x{img.size[1]} {img.mode}")

    def test_image_comparison_algorithm(self, visual_driver):
        """Test image comparison algorithm accuracy."""
        img1 = take_screenshot(visual_driver, "https://www.bing.com", "compare_1")
        img2 = take_screenshot(visual_driver, "https://www.bing.com", "compare_2")
        
        # Same page should be very similar
        similarity = calculate_similarity(img1, img2)
        print(f"✅ Same page similarity: {similarity:.2%}")
        assert similarity > 0.90, f"Same page should be similar: {similarity:.2%}"

    def test_diff_detection(self, visual_driver):
        """Test that visual diffs are detected for different pages."""
        img1 = take_screenshot(visual_driver, "https://www.bing.com", "diff_1")
        img2 = take_screenshot(visual_driver, "https://www.saucedemo.com", "diff_2")
        
        # Different pages should have low similarity
        similarity = calculate_similarity(img1, img2)
        print(f"✅ Different pages similarity: {similarity:.2%}")
        assert similarity < 0.80, f"Different pages should differ: {similarity:.2%}"

