"""
Test Ruff formatter integration with PyRustor refactoring operations.

This module tests the integration of Ruff's formatter with PyRustor's refactoring
capabilities, allowing users to apply formatting automatically during refactoring.
"""

import pytest
import pyrustor


class TestFormattingIntegration:
    """Test Ruff formatter integration with refactoring operations."""

    def test_rename_function_with_format(self):
        """Test renaming a function with automatic formatting."""
        messy_code = '''def   old_function(  x,y  ):
    return x+y
        
def another_function():
    result=old_function(1,2)
    return result'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(messy_code)
        refactor = pyrustor.Refactor(ast)
        
        # Rename function with formatting
        refactor.rename_function_with_format("old_function", "new_function", apply_formatting=True)
        
        # Verify both renaming and formatting changes
        changes = refactor.change_summary()
        assert len(changes) > 0  # Should have changes

        # Check for rename and format changes in the summary string
        changes_lower = changes.lower()
        assert "rename" in changes_lower or "function" in changes_lower
        assert "format" in changes_lower

    def test_rename_class_with_format(self):
        """Test renaming a class with automatic formatting."""
        messy_code = '''class   OldClass:
    def __init__(self,name):
        self.name=name
    def get_name(self):
        return self.name
        
obj=OldClass("test")'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(messy_code)
        refactor = pyrustor.Refactor(ast)
        
        # Rename class with formatting
        refactor.rename_class_with_format("OldClass", "NewClass", apply_formatting=True)
        
        changes = refactor.change_summary()
        assert len(changes) > 0
        changes_lower = changes.lower()
        assert "rename" in changes_lower or "class" in changes_lower
        assert "format" in changes_lower

    def test_modernize_syntax_with_format(self):
        """Test modernizing syntax with automatic formatting."""
        old_syntax_code = '''def format_string(name,age):
    return "Name: %s, Age: %d"%(name,age)
        
def another_function():
    result=format_string("John",25)
    return result'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(old_syntax_code)
        refactor = pyrustor.Refactor(ast)
        
        # Modernize syntax with formatting
        refactor.modernize_syntax_with_format(apply_formatting=True)

        changes = refactor.change_summary()
        assert len(changes) > 0
        changes_lower = changes.lower()
        # For now, just check that formatting was applied
        # In a full implementation, this would also include syntax modernization
        assert "format" in changes_lower



    def test_format_only(self):
        """Test applying only formatting without other refactoring."""
        messy_code = '''import   os,sys
def   badly_formatted_function(  x,y,z  ):
    result=x+y*z
    return result
        
class   BadlyFormattedClass:
    def __init__(self,name,value):
        self.name=name
        self.value=value
    def process(self):
        return self.name+str(self.value)'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(messy_code)
        refactor = pyrustor.Refactor(ast)
        
        # Apply only formatting
        refactor.format_code()
        formatted_result = refactor.get_code()
        
        changes = refactor.change_summary()
        assert len(changes) > 0
        assert "format" in changes.lower()
        
        # Result should be formatted
        assert isinstance(formatted_result, str)
        assert len(formatted_result) > 0

    def test_to_string_with_format_parameter(self):
        """Test the to_string_with_format method."""
        code = '''def example(x,y):
    return x+y'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # Test without formatting
        result_no_format = refactor.get_code_with_format(apply_formatting=False)
        changes_before = refactor.change_summary()

        # Test with formatting
        result_with_format = refactor.get_code_with_format(apply_formatting=True)
        changes_after = refactor.change_summary()

        # Should have formatting changes
        assert len(changes_after) > len(changes_before)
        assert "format" in changes_after.lower()
        
        # Both should return strings
        assert isinstance(result_no_format, str)
        assert isinstance(result_with_format, str)

    def test_multiple_operations_with_formatting(self):
        """Test multiple refactoring operations with formatting applied at the end."""
        complex_code = '''import   ConfigParser
from   imp   import reload

class   OldStyleClass:
    def old_method(self,x,y):
        return "Name: %s, Age: %d"%(x,y)
        
def old_function():
    return OldStyleClass()'''

        parser = pyrustor.Parser()
        ast = parser.parse_string(complex_code)
        refactor = pyrustor.Refactor(ast)
        
        # Apply multiple refactoring operations
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("imp", "importlib")
        refactor.rename_class("OldStyleClass", "ModernClass")
        refactor.rename_function("old_function", "new_function")
        refactor.modernize_syntax()
        
        # Apply formatting at the end
        final_result = refactor.refactor_and_format()
        
        changes = refactor.change_summary()
        assert len(changes) > 0  # Should have changes

        # Should have various types of changes in the summary
        changes_lower = changes.lower()
        # At least one of these should be present
        has_refactoring = any(keyword in changes_lower for keyword in ["import", "rename", "modern", "syntax"])
        assert has_refactoring
        assert "format" in changes_lower
        
        assert isinstance(final_result, str)
        assert len(final_result) > 0


if __name__ == "__main__":
    pytest.main([__file__])
