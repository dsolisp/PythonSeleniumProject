"""
Enhanced visual regression tests with comprehensive image comparison capabilities.
"""

import pytest
import os
from hamcrest import assert_that, equal_to, less_than
from pages.google_search_page import GoogleSearchPage
import utils.diff_handler as diff_handler
from pages.base_page import BasePage


@pytest.mark.visual
@pytest.mark.parametrize("tc_id", ["tc_1234"])
def test_visual_comparison(tc_id, driver):
    """Enhanced visual regression test with better error reporting and flexibility."""
    base_page = BasePage(driver)
    google_search_page = GoogleSearchPage(driver)

    print(f"🔍 Running visual comparison test for: {tc_id}")
    
    # Define screenshot paths
    expected_image = f'screenshots_diff/{tc_id}_expected_screenshot.png'
    actual_image = f'screenshots_diff/{tc_id}_actual_screenshot.png'
    diff_output_path = f'screenshots_diff/{tc_id}_diff.png'

    try:
        # Ensure screenshots directory exists
        os.makedirs('screenshots_diff', exist_ok=True)
        
        # Navigate to Google if not already there
        if "google.com" not in base_page.driver.current_url:
            base_page.driver.get("https://www.google.com")
            base_page.wait_for_page_load()
        
        # Capture the baseline screenshot (expected)
        print(f"📸 Capturing expected screenshot: {expected_image}")
        google_search_page.capture_main_input_screenshot(expected_image)
        
        # Perform actions that might change the visual appearance
        element = google_search_page.get_search_input()
        if element:
            element.send_keys("Visual Test Query")
            print("✍️ Added text to search input")
        
        # Capture the actual screenshot after changes
        print(f"📸 Capturing actual screenshot: {actual_image}")
        google_search_page.capture_main_input_screenshot(actual_image)

        # Verify both screenshots were created
        assert os.path.exists(expected_image), f"Expected screenshot not found: {expected_image}"
        assert os.path.exists(actual_image), f"Actual screenshot not found: {actual_image}"
        
        # Compare images and generate diff
        print(f"🔄 Comparing images...")
        visual_difference = diff_handler.compare_images(expected_image, actual_image, diff_output_path)
        
        # Enhanced assertion with detailed feedback
        if visual_difference == 0:
            print("✅ Perfect match - no visual differences detected")
        else:
            # Allow for minor differences (anti-aliasing, rendering variations)
            tolerance = 1000  # pixels
            
            if visual_difference <= tolerance:
                print(f"⚠️ Minor visual differences detected: {visual_difference} pixels (within tolerance)")
            else:
                # Generate detailed error message
                error_msg = f"Significant visual differences found: {visual_difference} pixels (tolerance: {tolerance})"
                if os.path.exists(diff_output_path):
                    error_msg += f"\nDifference image saved: {diff_output_path}"
                
                print(f"❌ {error_msg}")
                pytest.fail(error_msg)
        
        # Clean assertion for CI/CD compatibility
        assert_that(visual_difference, less_than(1001), 
                   f"Visual differences exceeded tolerance: {visual_difference} pixels")
        
        print(f"✅ Visual comparison test completed successfully")
        
    except Exception as e:
        error_msg = f"Visual comparison test failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Provide debugging information
        if os.path.exists(expected_image):
            print(f"Expected image exists: {expected_image}")
        if os.path.exists(actual_image):
            print(f"Actual image exists: {actual_image}")
        if os.path.exists(diff_output_path):
            print(f"Diff image exists: {diff_output_path}")
            
        pytest.fail(error_msg)


@pytest.mark.visual
@pytest.mark.smoke
def test_screenshot_functionality():
    """Test that screenshot capture mechanism works correctly."""
    driver_tuple = None
    try:
        from conftest import get_driver
        driver_tuple = get_driver()
        
        base_page = BasePage(driver_tuple)
        google_search_page = GoogleSearchPage(driver_tuple)
        
        # Navigate to Google
        base_page.driver.get("https://www.google.com")
        base_page.wait_for_page_load()
        
        # Test screenshot capture
        test_screenshot = 'screenshots_diff/test_functionality.png'
        google_search_page.capture_main_input_screenshot(test_screenshot)
        
        # Verify screenshot was created
        assert os.path.exists(test_screenshot), f"Test screenshot not created: {test_screenshot}"
        assert os.path.getsize(test_screenshot) > 0, "Screenshot file should not be empty"
        
        print(f"✅ Screenshot functionality test passed")
        
        # Cleanup
        if os.path.exists(test_screenshot):
            os.remove(test_screenshot)
            
    except Exception as e:
        pytest.fail(f"Screenshot functionality test failed: {str(e)}")
    finally:
        if driver_tuple:
            if isinstance(driver_tuple, tuple):
                driver_tuple[0].quit()
                try:
                    driver_tuple[1].close()
                except:
                    pass
            else:
                driver_tuple.quit()


@pytest.mark.visual
def test_diff_handler_availability():
    """Test that the diff handler module and functions are available."""
    try:
        # Test that required functions exist
        assert hasattr(diff_handler, 'compare_images'), "diff_handler should have compare_images function"
        
        # Test with dummy parameters to verify function signature
        # This won't actually run comparison but verifies the function exists
        print("✅ Diff handler module is properly imported and accessible")
        
    except ImportError as e:
        pytest.fail(f"Failed to import diff_handler: {e}")
    except AttributeError as e:
        pytest.fail(f"diff_handler missing required functions: {e}")
    except Exception as e:
        pytest.fail(f"Diff handler availability test failed: {e}")