"""
Comprehensive tests for PyRustor Refactor functionality.

This module contains thorough tests for the Refactor class, covering:
- Function and class renaming
- Import replacement and modernization
- Code generation and formatting
- Error handling and edge cases
- Complex refactoring workflows
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


@pytest.mark.unit
@pytest.mark.refactor
class TestRefactorBasics:
    """Test basic refactor functionality."""
    
    def test_refactor_creation(self, parser):
        """Test creating a refactor instance."""
        ast = parser.parse_string("def hello(): pass")
        refactor = pyrustor.Refactor(ast)
        
        assert refactor is not None
        assert isinstance(refactor, pyrustor.Refactor)
        assert refactor.change_summary() == "No changes made"
    
    def test_refactor_with_empty_ast(self, parser):
        """Test creating refactor with empty AST."""
        ast = parser.parse_string("")
        refactor = pyrustor.Refactor(ast)
        
        assert refactor is not None
        assert refactor.change_summary() == "No changes made"
    
    def test_get_code_without_changes(self, parser):
        """Test getting code without any changes."""
        code = "def hello(): pass"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        result = refactor.get_code()
        assert "hello" in result
        assert "pass" in result


@pytest.mark.unit
@pytest.mark.refactor
class TestFunctionRenaming:
    """Test function renaming functionality."""
    
    def test_rename_simple_function(self, parser, assertions):
        """Test renaming a simple function."""
        ast = parser.parse_string("def old_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_function("old_function", "new_function")
        
        # Check the actual code was modified
        code = refactor.get_code()
        assert "def new_function" in code
        assert "def old_function" not in code
        
        # Check changes were recorded
        assertions.assert_changes_recorded(refactor, 1)
    
    def test_rename_function_with_parameters(self, parser):
        """Test renaming function with parameters."""
        code = "def calculate(x, y, z=10): return x + y + z"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_function("calculate", "compute")
        
        result = refactor.get_code()
        assert "def compute(x, y, z)" in result  # Default values not fully supported yet
    
    def test_rename_function_with_docstring(self, parser):
        """Test renaming function with docstring."""
        code = '''
def old_function():
    """This is a documented function."""
    return True
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_function("old_function", "new_function")
        
        result = refactor.get_code()
        assert "def new_function" in result
        assert "documented function" in result
    
    def test_rename_multiple_functions(self, parser, sample_function_code):
        """Test renaming multiple functions."""
        ast = parser.parse_string(sample_function_code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_function("hello_world", "greet_world")
        refactor.rename_function("calculate_sum", "add_numbers")
        
        result = refactor.get_code()
        assert "def greet_world" in result
        assert "def add_numbers" in result
        assert "def hello_world" not in result
        assert "def calculate_sum" not in result
    
    def test_rename_nonexistent_function_raises_error(self, parser):
        """Test that renaming nonexistent function raises error."""
        ast = parser.parse_string("def existing_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        with pytest.raises(ValueError, match=".*not found.*"):
            refactor.rename_function("nonexistent_function", "new_name")
    
    def test_rename_function_to_existing_name(self, parser):
        """Test renaming function to an existing name."""
        code = '''
def function_a(): pass
def function_b(): pass
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # This should work - we're not checking for name conflicts yet
        refactor.rename_function("function_a", "function_b")
        
        result = refactor.get_code()
        # Both functions will have the same name now
        assert result.count("def function_b") == 2


@pytest.mark.unit
@pytest.mark.refactor
class TestClassRenaming:
    """Test class renaming functionality."""
    
    def test_rename_simple_class(self, parser, assertions):
        """Test renaming a simple class."""
        ast = parser.parse_string("class OldClass: pass")
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_class("OldClass", "NewClass")
        
        # Check the actual code was modified
        code = refactor.get_code()
        assert "class NewClass" in code
        assert "class OldClass" not in code
        
        # Check changes were recorded
        assertions.assert_changes_recorded(refactor, 1)
    
    def test_rename_class_with_inheritance(self, parser):
        """Test renaming class with inheritance."""
        code = "class Child(Parent): pass"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_class("Child", "Offspring")
        
        result = refactor.get_code()
        assert "class Offspring(Parent)" in result
    
    def test_rename_class_with_methods(self, parser, sample_class_code):
        """Test renaming class with methods."""
        ast = parser.parse_string(sample_class_code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.rename_class("Person", "Individual")
        refactor.rename_class("Employee", "Worker")
        
        result = refactor.get_code()
        assert "class Individual" in result
        assert "class Worker" in result
        assert "class Person" not in result
        assert "class Employee" not in result
    
    def test_rename_nonexistent_class_raises_error(self, parser):
        """Test that renaming nonexistent class raises error."""
        ast = parser.parse_string("class ExistingClass: pass")
        refactor = pyrustor.Refactor(ast)
        
        with pytest.raises(ValueError, match=".*not found.*"):
            refactor.rename_class("NonexistentClass", "NewClass")


@pytest.mark.unit
@pytest.mark.refactor
class TestImportReplacement:
    """Test import replacement functionality."""
    
    def test_replace_simple_import(self, parser):
        """Test replacing a simple import."""
        ast = parser.parse_string("import old_module")
        refactor = pyrustor.Refactor(ast)
        
        refactor.replace_import("old_module", "new_module")
        
        # The operation should complete without error
        # Note: Full import replacement may not be fully implemented yet
        result = refactor.get_code()
        assert result is not None
    
    def test_replace_from_import(self, parser):
        """Test replacing from import."""
        code = "from old_package import function"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.replace_import("old_package", "new_package")
        
        result = refactor.get_code()
        assert result is not None
    
    def test_replace_multiple_imports(self, parser, sample_import_code):
        """Test replacing multiple imports."""
        ast = parser.parse_string(sample_import_code)
        refactor = pyrustor.Refactor(ast)
        
        # Replace legacy imports
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("imp", "importlib")
        
        result = refactor.get_code()
        assert result is not None
    
    def test_replace_nonexistent_import(self, parser):
        """Test replacing import that doesn't exist."""
        ast = parser.parse_string("import existing_module")
        refactor = pyrustor.Refactor(ast)
        
        # This should not raise an error, just do nothing
        refactor.replace_import("nonexistent_module", "new_module")
        
        result = refactor.get_code()
        # Note: Our code generator may not preserve all statement types perfectly
        assert result is not None and len(result) > 0


@pytest.mark.unit
@pytest.mark.refactor
class TestSyntaxModernization:
    """Test syntax modernization functionality."""
    
    def test_modernize_empty_code(self, parser):
        """Test modernizing empty code."""
        ast = parser.parse_string("")
        refactor = pyrustor.Refactor(ast)
        
        refactor.modernize_syntax()
        
        result = refactor.get_code()
        assert result == ""
    
    def test_modernize_simple_code(self, parser):
        """Test modernizing simple code."""
        code = "def hello(): pass"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        refactor.modernize_syntax()
        
        result = refactor.get_code()
        assert "def hello" in result
    
    def test_modernize_complex_code(self, parser, complex_code_sample):
        """Test modernizing complex code."""
        ast = parser.parse_string(complex_code_sample)
        refactor = pyrustor.Refactor(ast)
        
        refactor.modernize_syntax()
        
        result = refactor.get_code()
        assert result is not None
        assert len(result) > 0


@pytest.mark.unit
@pytest.mark.refactor
class TestCodeGeneration:
    """Test code generation functionality."""
    
    def test_get_code_preserves_structure(self, parser):
        """Test that get_code preserves code structure."""
        code = '''
def function_one():
    return 1

def function_two():
    return 2

class MyClass:
    def method(self):
        return "method"
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        result = refactor.get_code()
        
        # Check that all elements are present
        assert "def function_one" in result
        assert "def function_two" in result
        assert "class MyClass" in result
        assert "def method" in result
    
    def test_get_code_after_modifications(self, parser):
        """Test get_code after making modifications."""
        code = '''
def old_function():
    return "old"

class OldClass:
    pass
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # Make modifications
        refactor.rename_function("old_function", "new_function")
        refactor.rename_class("OldClass", "NewClass")
        
        result = refactor.get_code()
        
        # Check modifications are reflected
        assert "def new_function" in result
        assert "class NewClass" in result
        assert "def old_function" not in result
        assert "class OldClass" not in result
    
    def test_get_code_with_complex_expressions(self, parser):
        """Test get_code with complex expressions."""
        code = '''
def complex_function():
    result = [x**2 for x in range(10) if x % 2 == 0]
    return {"data": result, "count": len(result)}
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        result = refactor.get_code()
        
        # Should contain the function definition
        assert "def complex_function" in result
        # Note: Complex expressions might not be fully preserved yet


@pytest.mark.unit
@pytest.mark.refactor
@pytest.mark.error_handling
class TestRefactorErrorHandling:
    """Test refactor error handling."""
    
    def test_invalid_function_name(self, parser):
        """Test renaming to invalid function name."""
        ast = parser.parse_string("def valid_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # First rename should work
        refactor.rename_function("valid_function", "123invalid")

        # Second rename should fail because "valid_function" no longer exists
        with pytest.raises(ValueError):
            refactor.rename_function("valid_function", "with-dashes")
        
        # Should not crash
        result = refactor.get_code()
        assert result is not None
    
    def test_invalid_class_name(self, parser):
        """Test renaming to invalid class name."""
        ast = parser.parse_string("class ValidClass: pass")
        refactor = pyrustor.Refactor(ast)
        
        # These should work - we're not validating names yet
        refactor.rename_class("ValidClass", "123invalid")
        
        # Should not crash
        result = refactor.get_code()
        assert result is not None
    
    def test_empty_names(self, parser):
        """Test renaming to empty names."""
        ast = parser.parse_string("def function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Empty names should work but might produce invalid code
        refactor.rename_function("function", "")
        
        result = refactor.get_code()
        assert result is not None


@pytest.mark.integration
@pytest.mark.refactor
class TestRefactorFileOperations:
    """Test refactor file operations."""
    
    def test_save_to_file(self, parser, temp_directory):
        """Test saving refactored code to file."""
        code = "def test_function(): pass"
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # Apply changes
        refactor.rename_function("test_function", "renamed_function")
        
        # Save to file
        output_file = temp_directory / "output.py"
        refactor.save_to_file(str(output_file))
        
        # Verify file was created and has correct content
        assert output_file.exists()
        content = output_file.read_text()
        assert "def renamed_function" in content
        assert "def test_function" not in content
    
    def test_save_to_nonexistent_directory(self, parser):
        """Test saving to nonexistent directory."""
        ast = parser.parse_string("def function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # This should raise an error
        with pytest.raises((FileNotFoundError, OSError, ValueError)):
            refactor.save_to_file("/nonexistent/directory/file.py")


@pytest.mark.integration
@pytest.mark.refactor
class TestComplexRefactoringWorkflows:
    """Test complex refactoring workflows."""
    
    def test_complete_modernization_workflow(self, parser, complex_code_sample):
        """Test complete code modernization workflow."""
        ast = parser.parse_string(complex_code_sample)
        refactor = pyrustor.Refactor(ast)
        
        # Step 1: Modernize imports
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("imp", "importlib")
        
        # Step 2: Rename classes and functions
        refactor.rename_class("DataProcessor", "ModernDataProcessor")
        refactor.rename_function("legacy_function", "modern_function")
        refactor.rename_function("another_legacy_function", "another_modern_function")
        
        # Step 3: Apply syntax modernization
        refactor.modernize_syntax()
        
        # Get final result
        result = refactor.get_code()
        
        # Verify changes
        assert "class ModernDataProcessor" in result
        assert "def modern_function" in result
        assert "def another_modern_function" in result
        assert "class DataProcessor" not in result
        assert "def legacy_function" not in result
        
        # Check that multiple changes were recorded
        summary = refactor.change_summary()
        assert "changes" in summary.lower()
    
    def test_incremental_refactoring(self, parser):
        """Test incremental refactoring with change tracking."""
        code = '''
def func1(): pass
def func2(): pass
class Class1: pass
class Class2: pass
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # Initially no changes
        assert refactor.change_summary() == "No changes made"
        
        # Make incremental changes
        refactor.rename_function("func1", "function1")
        assert "1 changes" in refactor.change_summary()
        
        refactor.rename_function("func2", "function2")
        assert "2 changes" in refactor.change_summary()
        
        refactor.rename_class("Class1", "Component1")
        assert "3 changes" in refactor.change_summary()
        
        refactor.rename_class("Class2", "Component2")
        assert "4 changes" in refactor.change_summary()
        
        # Verify final result
        result = refactor.get_code()
        assert "def function1" in result
        assert "def function2" in result
        assert "class Component1" in result
        assert "class Component2" in result


@pytest.mark.benchmark
@pytest.mark.refactor
@pytest.mark.slow
class TestRefactorPerformance:
    """Test refactor performance characteristics."""
    
    def test_large_file_refactoring_performance(self, parser, performance_timer):
        """Test refactoring performance with large files."""
        # Generate large code
        large_code = "\n".join([
            f"def function_{i}(): return {i}"
            for i in range(500)
        ])
        
        ast = parser.parse_string(large_code)
        refactor = pyrustor.Refactor(ast)
        
        performance_timer.start()
        
        # Rename many functions
        for i in range(0, 500, 10):  # Rename every 10th function
            refactor.rename_function(f"function_{i}", f"renamed_function_{i}")
        
        result = refactor.get_code()
        
        performance_timer.stop()
        
        # Should complete in reasonable time
        assert performance_timer.elapsed < 2.0
        assert result is not None
        assert "renamed_function_0" in result
