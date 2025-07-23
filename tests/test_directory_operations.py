"""
Directory operations testing for PyRustor.

This module tests PyRustor's ability to parse and refactor entire directories
of Python files, which is crucial for real-world usage.
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


class TestDirectoryOperations:
    """Test PyRustor with directory-level operations."""

    def test_parse_simple_directory(self, temp_directory):
        """Test parsing a directory with multiple Python files."""
        # Create multiple Python files
        files = {
            "module1.py": '''
def function_one():
    """First function."""
    return "Hello from module 1"

class ClassOne:
    """First class."""
    pass
''',
            "module2.py": '''
import ConfigParser
from imp import reload

def function_two():
    """Second function."""
    return "Hello from module 2"

class ClassTwo:
    """Second class."""
    
    def method_two(self):
        return "Method from class two"
''',
            "utils.py": '''
import urllib2

def utility_function():
    """Utility function."""
    return "Utility"

def old_helper():
    """Old helper function."""
    return "Old helper"
''',
        }
        
        # Write files to directory
        for filename, content in files.items():
            file_path = temp_directory / filename
            file_path.write_text(content)
        
        # Test directory parsing
        parser = pyrustor.Parser()
        results = parser.parse_directory(str(temp_directory), recursive=False)
        
        # Verify results
        assert len(results) == 3
        
        # Check that all files were parsed
        filenames = [os.path.basename(path) for path, _ in results]
        assert "module1.py" in filenames
        assert "module2.py" in filenames
        assert "utils.py" in filenames
        
        # Check AST content
        for path, ast in results:
            assert not ast.is_empty()
            assert ast.statement_count() > 0

    def test_parse_nested_directory(self, temp_directory):
        """Test parsing a nested directory structure."""
        # Create nested directory structure
        subdir1 = temp_directory / "package1"
        subdir2 = temp_directory / "package2"
        nested_dir = subdir1 / "nested"
        
        subdir1.mkdir()
        subdir2.mkdir()
        nested_dir.mkdir()
        
        files = {
            "main.py": '''
from package1 import module1
from package2.module2 import ClassTwo

def main():
    """Main function."""
    return "Main application"
''',
            "package1/__init__.py": '''
"""Package 1 initialization."""
from .module1 import function_one
''',
            "package1/module1.py": '''
import ConfigParser

def function_one():
    """Function in package 1."""
    return "Package 1 function"

class OldClass:
    """Old class in package 1."""
    pass
''',
            "package1/nested/__init__.py": '''
"""Nested package initialization."""
''',
            "package1/nested/deep_module.py": '''
import urllib2
from imp import reload

def deep_function():
    """Deep nested function."""
    return "Deep function"
''',
            "package2/__init__.py": '''
"""Package 2 initialization."""
''',
            "package2/module2.py": '''
import ConfigParser

class ClassTwo:
    """Class in package 2."""
    
    def method_two(self):
        return "Method two"

def helper_function():
    """Helper function."""
    return "Helper"
''',
        }
        
        # Write files
        for filepath, content in files.items():
            full_path = temp_directory / filepath
            full_path.write_text(content)
        
        # Test recursive directory parsing
        parser = pyrustor.Parser()
        results = parser.parse_directory(str(temp_directory), recursive=True)
        
        # Verify results
        assert len(results) >= 6  # Should find all Python files
        
        # Check that nested files were found
        paths = [path for path, _ in results]
        assert any("nested" in path for path in paths)
        assert any("deep_module.py" in path for path in paths)

    def test_directory_refactoring_workflow(self, temp_directory):
        """Test a complete directory refactoring workflow."""
        # Create a project structure with legacy code
        files = {
            "models.py": '''
import ConfigParser
from imp import reload

class UserModel:
    """User model with legacy patterns."""
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
    
    def get_user_info(self, user_id):
        """Get user info using old formatting."""
        return "User ID: %d" % user_id

class OldDataModel:
    """Old data model."""
    pass
''',
            "views.py": '''
import urllib2
from models import UserModel, OldDataModel

def user_view(request):
    """User view with legacy patterns."""
    model = UserModel("config.ini")
    data_model = OldDataModel()
    
    user_info = model.get_user_info(123)
    return "Response: %s" % user_info

def old_api_view(request):
    """Old API view."""
    return "Old API response"
''',
            "utils.py": '''
import ConfigParser
import urllib2

def fetch_external_data(url):
    """Fetch data using urllib2."""
    response = urllib2.urlopen(url)
    return response.read()

def old_utility_function():
    """Old utility function."""
    return "Old utility"

def format_message(msg, status):
    """Format message using old formatting."""
    return "Message: %s, Status: %d" % (msg, status)
''',
        }
        
        # Write files
        for filename, content in files.items():
            file_path = temp_directory / filename
            file_path.write_text(content)
        
        # Parse all files
        parser = pyrustor.Parser()
        results = parser.parse_directory(str(temp_directory), recursive=False)
        
        # Apply refactoring to each file
        refactored_results = []
        
        for file_path, ast in results:
            refactor = pyrustor.Refactor(ast)
            
            # Apply common modernizations
            refactor.replace_import("ConfigParser", "configparser")
            refactor.replace_import("urllib2", "urllib.request")
            refactor.replace_import("imp", "importlib")
            
            # Rename old classes and functions (don't error if not found)
            refactor.rename_class_optional("OldDataModel", "ModernDataModel", False)
            refactor.rename_function_optional("old_api_view", "modern_api_view", False)
            refactor.rename_function_optional("old_utility_function", "modern_utility_function", False)
            
            # Modernize syntax
            refactor.modernize_syntax()
            
            # Get refactored code
            refactored_code = refactor.get_code()
            refactored_results.append((file_path, refactored_code, refactor.change_summary()))
        
        # Verify refactoring results
        assert len(refactored_results) == 3
        
        for file_path, code, summary in refactored_results:
            # Check that modernizations were applied
            if "models.py" in file_path:
                assert "configparser" in code or "ConfigParser" not in code
                assert "ModernDataModel" in code
            elif "views.py" in file_path:
                assert "modern_api_view" in code
                # Note: ModernDataModel is in models.py, not views.py
            elif "utils.py" in file_path:
                assert "urllib.request" in code or "urllib2" not in code
                assert "modern_utility_function" in code
            
            # Check that changes were recorded
            assert "No changes made" not in summary

    def test_directory_with_syntax_errors(self, temp_directory):
        """Test directory parsing with files containing syntax errors."""
        files = {
            "valid_file.py": '''
def valid_function():
    """This is a valid function."""
    return "Valid"
''',
            "invalid_file.py": '''
def invalid_function(
    """This file has syntax errors."""
    return "Invalid"
''',  # Missing closing parenthesis
            "another_valid.py": '''
class ValidClass:
    """This is a valid class."""
    pass
''',
        }
        
        # Write files
        for filename, content in files.items():
            file_path = temp_directory / filename
            file_path.write_text(content)
        
        # Test directory parsing - should handle errors gracefully
        parser = pyrustor.Parser()
        
        # This should not raise an exception, but may return fewer results
        try:
            results = parser.parse_directory(str(temp_directory), recursive=False)
            # Should parse at least the valid files
            assert len(results) >= 2
            
            # Check that valid files were parsed correctly
            for path, ast in results:
                if "valid_file.py" in path or "another_valid.py" in path:
                    assert not ast.is_empty()
                    
        except Exception as e:
            # If parsing fails, it should provide meaningful error information
            assert "Parse error" in str(e) or "syntax" in str(e).lower()

    def test_empty_directory(self, temp_directory):
        """Test parsing an empty directory."""
        parser = pyrustor.Parser()
        results = parser.parse_directory(str(temp_directory), recursive=False)
        
        # Should return empty results, not raise an error
        assert len(results) == 0

    def test_directory_with_non_python_files(self, temp_directory):
        """Test directory parsing with mixed file types."""
        files = {
            "script.py": '''
def python_function():
    """Python function."""
    return "Python"
''',
            "data.txt": "This is a text file",
            "config.json": '{"key": "value"}',
            "readme.md": "# README",
            "another_script.py": '''
class PythonClass:
    """Python class."""
    pass
''',
        }
        
        # Write files
        for filename, content in files.items():
            file_path = temp_directory / filename
            file_path.write_text(content)
        
        # Test directory parsing
        parser = pyrustor.Parser()
        results = parser.parse_directory(str(temp_directory), recursive=False)
        
        # Should only parse Python files
        assert len(results) == 2
        
        # Check that only .py files were parsed
        for path, ast in results:
            assert path.endswith(".py")
            assert not ast.is_empty()
