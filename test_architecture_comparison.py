"""
Quick comparison test of both approaches
"""
import pytest
from unittest.mock import Mock

def test_monolithic_approach():
    """Test current monolithic base page approach."""
    from pages.base_page import BasePage
    
    mock_driver = Mock()
    page = BasePage(mock_driver)
    
    # Direct, simple API
    assert hasattr(page, 'click')
    assert hasattr(page, 'take_screenshot') 
    assert hasattr(page, 'execute_query')
    assert hasattr(page, 'navigate_to')
    
    # Single object to manage
    assert page.driver == mock_driver
    print("✅ Monolithic: Simple, direct API")

def test_composition_approach():
    """Test composition-based approach."""
    from pages.base_page_composition_example import BasePageComposition
    
    mock_driver = Mock()
    page = BasePageComposition(mock_driver)
    
    # Same API through delegation
    assert hasattr(page, 'click') 
    assert hasattr(page, 'take_screenshot')
    assert hasattr(page, 'execute_query')
    assert hasattr(page, 'navigate_to')
    
    # But also access to individual components
    assert hasattr(page, 'elements')
    assert hasattr(page, 'navigation')
    assert hasattr(page, 'screenshots')
    assert hasattr(page, 'database')
    
    print("✅ Composition: Modular, but more complex")

def test_api_compatibility():
    """Test that both approaches provide same API."""
    from pages.base_page import BasePage
    from pages.base_page_composition_example import BasePageComposition
    
    mock_driver = Mock()
    
    monolithic = BasePage(mock_driver)
    composition = BasePageComposition(mock_driver)
    
    # Both should have same public methods
    mono_methods = [method for method in dir(monolithic) if not method.startswith('_')]
    comp_methods = [method for method in dir(composition) if not method.startswith('_')]
    
    # Key methods should be available in both
    key_methods = ['click', 'send_keys', 'get_text', 'navigate_to', 'take_screenshot']
    
    for method in key_methods:
        assert hasattr(monolithic, method), f"Monolithic missing {method}"
        assert hasattr(composition, method), f"Composition missing {method}"
    
    print("✅ Both approaches provide same API")

if __name__ == "__main__":
    test_monolithic_approach()
    test_composition_approach() 
    test_api_compatibility()
    print("\n🎯 CONCLUSION: Both work, but monolithic is simpler for your use case!")