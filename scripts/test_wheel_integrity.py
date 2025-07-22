#!/usr/bin/env python3
"""
Test script to verify wheel integrity and functionality.
This script should be run after installing from a wheel to ensure
all components are properly included and functional.
"""

import sys
import traceback
from typing import List, Tuple


def test_basic_import() -> Tuple[bool, str]:
    """Test basic module import."""
    try:
        import pyrustor
        return True, f"✅ Basic import successful"
    except Exception as e:
        return False, f"❌ Basic import failed: {e}"


def test_parser_availability() -> Tuple[bool, str]:
    """Test that Parser class is available."""
    try:
        import pyrustor
        if not hasattr(pyrustor, 'Parser'):
            return False, f"❌ Parser class not found in pyrustor module"
        return True, f"✅ Parser class is available"
    except Exception as e:
        return False, f"❌ Parser availability check failed: {e}"


def test_parser_creation() -> Tuple[bool, str]:
    """Test Parser instantiation."""
    try:
        import pyrustor
        parser = pyrustor.Parser()
        return True, f"✅ Parser created successfully"
    except Exception as e:
        return False, f"❌ Parser creation failed: {e}"


def test_basic_parsing() -> Tuple[bool, str]:
    """Test basic parsing functionality."""
    try:
        import pyrustor
        parser = pyrustor.Parser()
        ast = parser.parse_string("def hello(): pass")
        
        if ast is None:
            return False, f"❌ Parsing returned None"
        
        if ast.is_empty():
            return False, f"❌ AST is empty for valid code"
        
        functions = ast.function_names()
        if len(functions) != 1 or functions[0] != "hello":
            return False, f"❌ Expected function 'hello', got: {functions}"
        
        return True, f"✅ Basic parsing works correctly"
    except Exception as e:
        return False, f"❌ Basic parsing failed: {e}"


def test_refactor_availability() -> Tuple[bool, str]:
    """Test that Refactor class is available."""
    try:
        import pyrustor
        if not hasattr(pyrustor, 'Refactor'):
            return False, f"❌ Refactor class not found in pyrustor module"
        return True, f"✅ Refactor class is available"
    except Exception as e:
        return False, f"❌ Refactor availability check failed: {e}"


def test_refactor_creation() -> Tuple[bool, str]:
    """Test Refactor instantiation."""
    try:
        import pyrustor
        parser = pyrustor.Parser()
        ast = parser.parse_string("def hello(): pass")
        refactor = pyrustor.Refactor(ast)
        return True, f"✅ Refactor created successfully"
    except Exception as e:
        return False, f"❌ Refactor creation failed: {e}"


def test_version_info() -> Tuple[bool, str]:
    """Test version information availability."""
    try:
        import pyrustor
        if not hasattr(pyrustor, '__version__'):
            return False, f"❌ __version__ attribute not found"
        
        version = pyrustor.__version__
        if not version:
            return False, f"❌ Version is empty or None"
        
        return True, f"✅ Version info available: {version}"
    except Exception as e:
        return False, f"❌ Version info check failed: {e}"


def test_module_attributes() -> Tuple[bool, str]:
    """Test that all expected module attributes are present."""
    try:
        import pyrustor
        
        expected_attrs = ['Parser', 'Refactor', '__version__']
        available_attrs = [attr for attr in dir(pyrustor) if not attr.startswith('_')]
        
        missing_attrs = [attr for attr in expected_attrs if not hasattr(pyrustor, attr)]
        
        if missing_attrs:
            return False, f"❌ Missing attributes: {missing_attrs}. Available: {available_attrs}"
        
        return True, f"✅ All expected attributes present: {available_attrs}"
    except Exception as e:
        return False, f"❌ Module attributes check failed: {e}"


def run_all_tests() -> None:
    """Run all tests and report results."""
    tests = [
        ("Basic Import", test_basic_import),
        ("Module Attributes", test_module_attributes),
        ("Parser Availability", test_parser_availability),
        ("Parser Creation", test_parser_creation),
        ("Basic Parsing", test_basic_parsing),
        ("Refactor Availability", test_refactor_availability),
        ("Refactor Creation", test_refactor_creation),
        ("Version Info", test_version_info),
    ]
    
    print("🧪 Running PyRustor wheel integrity tests...\n")
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            print(f"{test_name:20} | {message}")
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"{test_name:20} | ❌ Test execution failed: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("\n❌ Some tests failed! The wheel may be incomplete or corrupted.")
        sys.exit(1)
    else:
        print("\n✅ All tests passed! The wheel appears to be complete and functional.")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
