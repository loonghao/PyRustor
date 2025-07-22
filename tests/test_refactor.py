"""Tests for PyRustor Refactor functionality"""

import pytest
import tempfile
import os
import pyrustor


@pytest.mark.refactor
class TestRefactor:
    """Test cases for the Refactor class"""

    def test_refactor_creation(self):
        """Test creating a refactor instance"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def hello(): pass")
        refactor = pyrustor.Refactor(ast)
        
        assert refactor is not None
        assert refactor.change_summary() == "No changes made"

    def test_rename_function_basic(self):
        """Test basic function renaming"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def old_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Rename the function
        refactor.rename_function("old_function", "new_function")
        
        # Check that change was recorded
        summary = refactor.change_summary()
        assert "1 changes" in summary or "Renamed function" in summary

    def test_rename_multiple_functions(self):
        """Test renaming multiple functions"""
        parser = pyrustor.Parser()
        source = """
def func_a():
    pass

def func_b():
    return 42

def func_c():
    print("hello")
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Rename multiple functions
        refactor.rename_function("func_a", "function_alpha")
        refactor.rename_function("func_b", "function_beta")
        refactor.rename_function("func_c", "function_gamma")
        
        # Check that all changes were recorded
        summary = refactor.change_summary()
        assert "3 changes" in summary

    def test_rename_nonexistent_function(self):
        """Test renaming a function that doesn't exist"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def existing_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        with pytest.raises(ValueError):
            refactor.rename_function("nonexistent_function", "new_name")

    def test_rename_class_basic(self):
        """Test basic class renaming"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("class OldClass: pass")
        refactor = pyrustor.Refactor(ast)
        
        # Rename the class
        refactor.rename_class("OldClass", "NewClass")
        
        # Check that change was recorded
        summary = refactor.change_summary()
        assert "1 changes" in summary or "Renamed class" in summary

    def test_rename_multiple_classes(self):
        """Test renaming multiple classes"""
        parser = pyrustor.Parser()
        source = """
class ClassA:
    pass

class ClassB:
    def method(self):
        pass

class ClassC(ClassA):
    def __init__(self):
        super().__init__()
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Rename multiple classes
        refactor.rename_class("ClassA", "ComponentA")
        refactor.rename_class("ClassB", "ComponentB")
        refactor.rename_class("ClassC", "ComponentC")
        
        # Check that all changes were recorded
        summary = refactor.change_summary()
        assert "3 changes" in summary

    def test_rename_nonexistent_class(self):
        """Test renaming a class that doesn't exist"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("class ExistingClass: pass")
        refactor = pyrustor.Refactor(ast)
        
        with pytest.raises(ValueError):
            refactor.rename_class("NonexistentClass", "NewClass")

    def test_replace_import_basic(self):
        """Test basic import replacement"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("import old_module")
        refactor = pyrustor.Refactor(ast)
        
        # Replace the import
        refactor.replace_import("old_module", "new_module")
        
        # The operation should complete without error
        assert True  # Just test that the operation doesn't crash

    def test_replace_import_from_statement(self):
        """Test replacing from import statements"""
        parser = pyrustor.Parser()
        source = """
from old_package import function1, function2
from another_old import Class1
import yet_another_old
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Replace various imports
        refactor.replace_import("old_package", "new_package")
        refactor.replace_import("another_old", "another_new")
        refactor.replace_import("yet_another_old", "yet_another_new")
        
        # Should complete without error
        assert True

    def test_modernize_syntax(self):
        """Test syntax modernization"""
        parser = pyrustor.Parser()
        source = """
def old_style_function():
    name = "John"
    age = 30
    message = "Hello, %s! You are %d years old." % (name, age)
    return message
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply syntax modernization
        refactor.modernize_syntax()
        
        # Should complete without error
        result = refactor.get_code()
        assert result is not None

    def test_save_to_file(self):
        """Test saving refactored code to file"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def test_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Apply some changes
        refactor.rename_function("test_function", "renamed_function")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            temp_file = f.name
        
        try:
            refactor.save_to_file(temp_file)
            
            # Verify file was created and has content
            assert os.path.exists(temp_file)
            with open(temp_file, 'r') as f:
                content = f.read()
                assert len(content) > 0
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_change_tracking(self):
        """Test that changes are properly tracked"""
        parser = pyrustor.Parser()
        source = """
def func1(): pass
def func2(): pass
class Class1: pass
class Class2: pass
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Initially no changes
        assert refactor.change_summary() == "No changes made"
        
        # Make some changes
        refactor.rename_function("func1", "function1")
        assert "1 changes" in refactor.change_summary()
        
        refactor.rename_function("func2", "function2")
        assert "2 changes" in refactor.change_summary()
        
        refactor.rename_class("Class1", "Component1")
        assert "3 changes" in refactor.change_summary()
        
        refactor.rename_class("Class2", "Component2")
        assert "4 changes" in refactor.change_summary()

    def test_complex_refactoring_workflow(self):
        """Test a complex refactoring workflow"""
        parser = pyrustor.Parser()
        source = """
import ConfigParser
from imp import reload

class OldStyleClass:
    def old_method(self):
        config = ConfigParser.ConfigParser()
        return config

def old_function():
    return "old implementation"

def another_old_function():
    reload(some_module)
    return True
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply multiple refactoring operations
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("imp", "importlib")
        refactor.rename_class("OldStyleClass", "ModernClass")
        # Skip method renaming for now - only rename top-level functions
        refactor.rename_function("old_function", "new_function")
        refactor.rename_function("another_old_function", "another_new_function")
        refactor.modernize_syntax()
        
        # Check that multiple changes were recorded
        summary = refactor.change_summary()
        changes_count = summary.count("changes")
        assert changes_count > 0

    def test_edge_cases(self):
        """Test edge cases and error conditions"""
        parser = pyrustor.Parser()
        
        # Test with empty AST
        empty_ast = parser.parse_string("")
        refactor = pyrustor.Refactor(empty_ast)
        
        # These should not crash even with empty AST
        refactor.modernize_syntax()
        assert refactor.change_summary() == "No changes made"
        
        # Test with minimal code
        minimal_ast = parser.parse_string("pass")
        minimal_refactor = pyrustor.Refactor(minimal_ast)
        minimal_refactor.modernize_syntax()
        result = minimal_refactor.get_code()
        assert result is not None
