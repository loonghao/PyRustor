"""
File operations testing for PyRustor.

This module tests PyRustor's file I/O operations including reading from files,
saving refactored code to files, and handling various file scenarios.
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


class TestFileOperations:
    """Test PyRustor file I/O operations."""

    def test_parse_file_basic(self, temp_directory):
        """Test basic file parsing functionality."""
        # Create a test Python file
        test_content = '''
"""Test module for file parsing."""

import os
import sys
from pathlib import Path

def test_function():
    """Test function."""
    return "Hello, World!"

class TestClass:
    """Test class."""
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    test = TestClass("PyRustor")
    print(test.greet())
'''
        
        test_file = temp_directory / "test_module.py"
        test_file.write_text(test_content)
        
        # Test file parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        # Verify parsing results
        assert not ast.is_empty()
        assert ast.statement_count() > 0
        
        # Check detected elements
        functions = ast.function_names()
        classes = ast.class_names()
        imports = ast.imports()
        
        assert "test_function" in functions
        assert "TestClass" in classes
        assert len(imports) > 0

    def test_save_to_file(self, temp_directory):
        """Test saving refactored code to a file."""
        # Original code with legacy patterns
        original_code = '''
import ConfigParser
import urllib2
from imp import reload

class OldStyleClass:
    """Old style class with legacy patterns."""
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
    
    def fetch_data(self, url):
        """Fetch data using urllib2."""
        response = urllib2.urlopen(url)
        return response.read()
    
    def format_message(self, msg, code):
        """Format message using old string formatting."""
        return "Message: %s (Code: %d)" % (msg, code)

def old_function():
    """Old function to be renamed."""
    return "Old function result"
'''
        
        # Parse the code
        parser = pyrustor.Parser()
        ast = parser.parse_string(original_code)
        
        # Apply refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        refactor.replace_import("imp", "importlib")
        refactor.rename_class("OldStyleClass", "ModernClass")
        refactor.rename_function("old_function", "modern_function")
        refactor.modernize_syntax()
        
        # Save to file
        output_file = temp_directory / "refactored_output.py"
        refactor.save_to_file(str(output_file))
        
        # Verify file was created and contains expected content
        assert output_file.exists()
        
        saved_content = output_file.read_text()
        assert "ModernClass" in saved_content
        assert "modern_function" in saved_content
        assert "configparser" in saved_content or "ConfigParser" not in saved_content

    def test_file_with_encoding_issues(self, temp_directory):
        """Test handling files with different encodings."""
        # Create file with UTF-8 content including special characters
        utf8_content = '''
# -*- coding: utf-8 -*-
"""
Module with UTF-8 characters: 中文, émojis 🚀, and special symbols ∑∆.
"""

def process_unicode_text():
    """Process text with unicode characters."""
    text = "Hello 世界! 🌍"
    return f"Processed: {text}"

class UnicodeHandler:
    """Handle unicode text processing."""
    
    def __init__(self):
        self.greeting = "你好"
    
    def say_hello(self, name):
        return f"{self.greeting}, {name}! 😊"
'''
        
        test_file = temp_directory / "unicode_test.py"
        test_file.write_text(utf8_content, encoding='utf-8')
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("process_unicode_text", "handle_unicode_text")
        
        # Save and verify
        output_file = temp_directory / "unicode_output.py"
        refactor.save_to_file(str(output_file))
        
        saved_content = output_file.read_text(encoding='utf-8')
        assert "handle_unicode_text" in saved_content
        assert "你好" in saved_content
        assert "🌍" in saved_content

    def test_large_file_handling(self, temp_directory):
        """Test handling of larger Python files."""
        # Generate a larger Python file
        large_content = '''
"""Large Python module for testing performance."""

import os
import sys
import json
import datetime
from typing import List, Dict, Optional
import ConfigParser
import urllib2

'''
        
        # Add many classes and functions
        for i in range(50):
            large_content += f'''
class TestClass{i}:
    """Test class number {i}."""
    
    def __init__(self, value):
        self.value = value
        self.id = {i}
    
    def method_{i}(self):
        """Method {i}."""
        return "Result from method {i}: %s" % self.value
    
    def process_data_{i}(self, data):
        """Process data in method {i}."""
        return "Processed %d items in class {i}" % len(data)

def function_{i}():
    """Function number {i}."""
    return "Function {i} result"

def old_function_{i}():
    """Old function {i} to be renamed."""
    return "Old function {i}"

'''
        
        large_content += '''
# Main execution
if __name__ == "__main__":
    for i in range(10):
        obj = TestClass0(f"value_{i}")
        print(obj.method_0())
'''
        
        # Write large file
        large_file = temp_directory / "large_module.py"
        large_file.write_text(large_content)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(large_file))
        
        assert not ast.is_empty()
        assert ast.statement_count() > 100  # Should have many statements
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        
        # Apply some refactoring operations
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        
        # Rename some functions (just a few to avoid too much processing)
        for i in range(5):
            refactor.rename_function(f"old_function_{i}", f"modern_function_{i}")
        
        # Get result
        result = refactor.get_code()
        assert "modern_function_0" in result
        assert len(result) > 1000  # Should be a substantial amount of code

    def test_file_with_syntax_variations(self, temp_directory):
        """Test files with various Python syntax patterns."""
        syntax_variations = '''
"""Module with various Python syntax patterns."""

# Different import styles
import os, sys
from pathlib import (
    Path,
    PurePath
)
from typing import *
import ConfigParser as config_parser

# Different function definitions
def simple_function():
    pass

def function_with_args(a, b, c=None):
    return a + b

def function_with_kwargs(*args, **kwargs):
    return args, kwargs

async def async_function():
    return "async result"

# Different class definitions
class SimpleClass:
    pass

class ClassWithInheritance(object):
    def __init__(self):
        super(ClassWithInheritance, self).__init__()

class ClassWithMethods:
    @property
    def prop(self):
        return self._prop
    
    @staticmethod
    def static_method():
        return "static"
    
    @classmethod
    def class_method(cls):
        return cls

# Different string formatting styles
def string_formatting_examples():
    old_style = "Hello %s" % "world"
    format_style = "Hello {}".format("world")
    f_string = f"Hello {'world'}"
    return old_style, format_style, f_string

# Decorators
@property
def decorated_function():
    return "decorated"

# Context managers
def context_manager_example():
    with open("file.txt") as f:
        content = f.read()
    return content

# List comprehensions and generators
def comprehension_examples():
    list_comp = [x for x in range(10)]
    dict_comp = {x: x**2 for x in range(5)}
    gen_exp = (x for x in range(10))
    return list_comp, dict_comp, gen_exp
'''
        
        test_file = temp_directory / "syntax_variations.py"
        test_file.write_text(syntax_variations)
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(test_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.replace_import("ConfigParser", "configparser")
        refactor.rename_function("simple_function", "renamed_simple_function")
        refactor.modernize_syntax()
        
        result = refactor.get_code()
        assert "renamed_simple_function" in result

    def test_file_permissions_and_errors(self, temp_directory):
        """Test handling of file permission errors and other I/O issues."""
        # Test non-existent file
        parser = pyrustor.Parser()
        
        with pytest.raises(Exception):  # Should raise some kind of error
            parser.parse_file(str(temp_directory / "non_existent.py"))
        
        # Test directory instead of file
        with pytest.raises(Exception):  # Should raise some kind of error
            parser.parse_file(str(temp_directory))

    def test_backup_and_restore_workflow(self, temp_directory):
        """Test a complete backup and restore workflow."""
        original_content = '''
import ConfigParser
import urllib2

class OriginalClass:
    """Original class."""
    
    def original_method(self):
        return "Original method"

def original_function():
    """Original function."""
    return "Original result"
'''
        
        # Create original file
        original_file = temp_directory / "original.py"
        original_file.write_text(original_content)
        
        # Create backup
        backup_file = temp_directory / "original.py.backup"
        backup_file.write_text(original_content)
        
        # Parse and refactor
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(original_file))
        
        refactor = pyrustor.Refactor(ast)
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("urllib2", "urllib.request")
        refactor.rename_class("OriginalClass", "RefactoredClass")
        refactor.rename_function("original_function", "refactored_function")
        
        # Save refactored version
        refactor.save_to_file(str(original_file))
        
        # Verify refactoring
        refactored_content = original_file.read_text()
        assert "RefactoredClass" in refactored_content
        assert "refactored_function" in refactored_content
        
        # Verify backup still contains original
        backup_content = backup_file.read_text()
        assert "OriginalClass" in backup_content
        assert "original_function" in backup_content
