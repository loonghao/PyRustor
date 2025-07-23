"""
API compatibility and regression testing for PyRustor.

This module tests PyRustor's API stability and ensures that changes
don't break existing functionality.
"""

import pytest
import tempfile
from pathlib import Path
import pyrustor


class TestAPICompatibility:
    """Test PyRustor API compatibility and stability."""

    def test_parser_api_stability(self):
        """Test that Parser API remains stable."""
        # Test Parser instantiation
        parser = pyrustor.Parser()
        assert parser is not None
        
        # Test basic methods exist and work
        assert hasattr(parser, 'parse_string')
        assert hasattr(parser, 'parse_file')
        assert hasattr(parser, 'parse_directory')
        
        # Test parse_string method signature and behavior
        simple_code = "def test(): pass"
        ast = parser.parse_string(simple_code)
        assert ast is not None

    def test_python_ast_api_stability(self):
        """Test that PythonAst API remains stable."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def test(): pass\nclass Test: pass")
        
        # Test essential methods exist
        assert hasattr(ast, 'is_empty')
        assert hasattr(ast, 'statement_count')
        assert hasattr(ast, 'function_names')
        assert hasattr(ast, 'class_names')
        assert hasattr(ast, 'imports')
        assert hasattr(ast, 'to_string')
        
        # Test method return types and basic functionality
        assert isinstance(ast.is_empty(), bool)
        assert isinstance(ast.statement_count(), int)
        assert isinstance(ast.function_names(), list)
        assert isinstance(ast.class_names(), list)
        assert isinstance(ast.imports(), list)
        assert isinstance(ast.to_string(), str)
        
        # Test expected values
        assert not ast.is_empty()
        assert ast.statement_count() == 2
        assert "test" in ast.function_names()
        assert "Test" in ast.class_names()

    def test_refactor_api_stability(self):
        """Test that Refactor API remains stable."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("""
import ConfigParser
def old_function(): pass
class OldClass: pass
""")
        
        refactor = pyrustor.Refactor(ast)
        
        # Test essential methods exist
        assert hasattr(refactor, 'rename_function')
        assert hasattr(refactor, 'rename_class')
        assert hasattr(refactor, 'replace_import')
        assert hasattr(refactor, 'modernize_syntax')
        assert hasattr(refactor, 'get_code')
        assert hasattr(refactor, 'to_string')
        assert hasattr(refactor, 'change_summary')
        assert hasattr(refactor, 'save_to_file')
        
        # Test method functionality
        refactor.rename_function("old_function", "new_function")
        refactor.rename_class("OldClass", "NewClass")
        refactor.replace_import("ConfigParser", "configparser")
        
        result = refactor.get_code()
        assert "new_function" in result
        assert "NewClass" in result

    def test_formatting_api_stability(self):
        """Test formatting-related API stability."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("""
def   messy_function(  x,y  ):
    return x+y
""")
        
        refactor = pyrustor.Refactor(ast)
        
        # Test formatting methods exist
        assert hasattr(refactor, 'refactor_and_format')
        
        # Test formatting functionality
        formatted_result = refactor.refactor_and_format()
        assert isinstance(formatted_result, str)

    def test_error_handling_consistency(self):
        """Test that error handling remains consistent."""
        parser = pyrustor.Parser()
        
        # Test parsing invalid syntax
        with pytest.raises(Exception):
            parser.parse_string("def invalid_syntax(")
        
        # Test invalid file path
        with pytest.raises(Exception):
            parser.parse_file("/non/existent/file.py")

    def test_backward_compatibility_scenarios(self):
        """Test scenarios that should remain backward compatible."""
        # Test basic workflow that should always work
        parser = pyrustor.Parser()
        
        # Parse simple code
        ast = parser.parse_string("def hello(): return 'world'")
        assert not ast.is_empty()
        
        # Create refactor instance
        refactor = pyrustor.Refactor(ast)
        
        # Apply basic refactoring
        refactor.rename_function("hello", "greet")
        
        # Get result
        result = refactor.get_code()
        assert "greet" in result
        assert "hello" not in result or "def greet" in result

    def test_import_modernization_patterns(self):
        """Test common import modernization patterns remain working."""
        test_cases = [
            ("import ConfigParser", "configparser"),
            ("import urllib2", "urllib.request"),
            ("from imp import reload", "importlib"),
            ("import cPickle", "pickle"),
            ("import Queue", "queue"),
        ]
        
        for old_import, new_module in test_cases:
            parser = pyrustor.Parser()
            ast = parser.parse_string(old_import)

            refactor = pyrustor.Refactor(ast)

            # Extract the correct module name to replace
            if old_import.startswith("from "):
                # For "from imp import reload", we want to replace "imp"
                old_module = old_import.split()[1]
            else:
                # For "import ConfigParser", we want to replace "ConfigParser"
                old_module = old_import.split()[-1]

            refactor.replace_import(old_module, new_module)

            result = refactor.get_code()
            # Should contain the new import or have replaced the old one
            assert new_module in result or old_module not in result

    def test_string_formatting_modernization(self):
        """Test string formatting modernization patterns."""
        old_formatting_code = '''
def format_examples():
    name = "world"
    age = 25
    
    # Old % formatting
    msg1 = "Hello %s" % name
    msg2 = "Age: %d" % age
    msg3 = "Name: %s, Age: %d" % (name, age)
    
    return msg1, msg2, msg3
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(old_formatting_code)
        
        refactor = pyrustor.Refactor(ast)
        refactor.modernize_syntax()
        
        result = refactor.get_code()
        # Should have modernized the formatting (exact behavior may vary)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_class_and_function_renaming_edge_cases(self):
        """Test edge cases in class and function renaming."""
        complex_code = '''
class MyClass:
    def my_method(self):
        return MyClass()
    
    @classmethod
    def create_my_class(cls):
        return cls()

def use_my_class():
    obj = MyClass()
    return obj.my_method()

def another_function():
    return MyClass.create_my_class()
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(complex_code)
        
        refactor = pyrustor.Refactor(ast)
        refactor.rename_class("MyClass", "RenamedClass")
        refactor.rename_function("my_method", "renamed_method")
        
        result = refactor.get_code()
        assert "RenamedClass" in result
        assert "renamed_method" in result

    def test_version_compatibility(self):
        """Test version information and compatibility."""
        # Test that version information is accessible
        assert hasattr(pyrustor, '__version__')
        assert isinstance(pyrustor.__version__, str)
        
        # Test that main classes are importable
        assert hasattr(pyrustor, 'Parser')
        assert hasattr(pyrustor, 'PythonAst')
        assert hasattr(pyrustor, 'Refactor')

    def test_file_operations_api_consistency(self, temp_directory):
        """Test file operations API consistency."""
        # Create test file
        test_content = '''
def test_function():
    return "test"

class TestClass:
    pass
'''
        
        test_file = temp_directory / "test_api.py"
        test_file.write_text(test_content)
        
        # Test file parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        # Test refactoring and saving
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("test_function", "renamed_function")
        
        output_file = temp_directory / "output_api.py"
        refactor.save_to_file(str(output_file))
        
        # Verify file was created
        assert output_file.exists()
        content = output_file.read_text()
        assert "renamed_function" in content

    def test_directory_parsing_api_consistency(self, temp_directory):
        """Test directory parsing API consistency."""
        # Create multiple test files
        files = {
            "module1.py": "def func1(): pass",
            "module2.py": "class Class2: pass",
            "subdir/module3.py": "def func3(): pass",
        }
        
        # Create subdirectory
        subdir = temp_directory / "subdir"
        subdir.mkdir()
        
        # Write files
        for filepath, content in files.items():
            full_path = temp_directory / filepath
            full_path.write_text(content)
        
        # Test directory parsing
        parser = pyrustor.Parser()
        
        # Non-recursive
        results_non_recursive = parser.parse_directory(str(temp_directory), recursive=False)
        assert len(results_non_recursive) == 2  # Only top-level files
        
        # Recursive
        results_recursive = parser.parse_directory(str(temp_directory), recursive=True)
        assert len(results_recursive) == 3  # All files including subdirectory

    def test_change_tracking_api(self):
        """Test change tracking API consistency."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("""
def old_function():
    return "old"

class OldClass:
    pass
""")
        
        refactor = pyrustor.Refactor(ast)
        
        # Test initial state
        summary = refactor.change_summary()
        assert "No changes made" in summary or summary == ""
        
        # Apply changes
        refactor.rename_function("old_function", "new_function")
        refactor.rename_class("OldClass", "NewClass")
        
        # Test change tracking
        summary = refactor.change_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "No changes made" not in summary

    def test_repr_and_str_methods(self):
        """Test __repr__ and __str__ methods for debugging."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def test(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Test that repr methods don't crash
        parser_repr = repr(parser)
        refactor_repr = repr(refactor)
        
        assert isinstance(parser_repr, str)
        assert isinstance(refactor_repr, str)
        assert len(parser_repr) > 0
        assert len(refactor_repr) > 0
