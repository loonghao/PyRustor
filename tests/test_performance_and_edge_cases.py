"""
Performance and edge cases testing for PyRustor.

This module tests PyRustor's performance characteristics and edge case handling
to ensure robustness in real-world scenarios.
"""

import pytest
import time
import tempfile
from pathlib import Path
import pyrustor


class TestPerformanceAndEdgeCases:
    """Test PyRustor performance and edge case handling."""

    def test_empty_file_handling(self, temp_directory):
        """Test handling of empty Python files."""
        # Create empty file
        empty_file = temp_directory / "empty.py"
        empty_file.write_text("")
        
        # Test parsing
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(empty_file))
        
        assert ast.is_empty()
        assert ast.statement_count() == 0
        
        # Test refactoring empty file
        refactor = pyrustor.Refactor(ast)
        result = refactor.get_code()
        assert result == "" or result.strip() == ""

    def test_whitespace_only_file(self, temp_directory):
        """Test handling of files with only whitespace."""
        whitespace_content = "   \n\n  \t  \n   "
        
        whitespace_file = temp_directory / "whitespace.py"
        whitespace_file.write_text(whitespace_content)
        
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(whitespace_file))
        
        assert ast.is_empty()

    def test_comments_only_file(self, temp_directory):
        """Test handling of files with only comments."""
        comments_content = '''
# This is a comment
# Another comment
"""
This is a docstring
but no actual code
"""
# More comments
'''
        
        comments_file = temp_directory / "comments.py"
        comments_file.write_text(comments_content)
        
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(comments_file))
        
        # Should be considered comments-only since no executable statements
        assert ast.is_comments_only()

    def test_very_long_lines(self, temp_directory):
        """Test handling of files with very long lines."""
        # Create a file with very long lines
        long_line_content = f'''
def function_with_very_long_line():
    """Function with a very long line."""
    very_long_string = "{'x' * 1000}"
    another_long_line = "{'y' * 2000}"
    return very_long_string + another_long_line

class ClassWithLongLine:
    """Class with long line."""

    def method_with_long_parameters(self, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10):
        return "Long parameter list"
'''
        
        long_lines_file = temp_directory / "long_lines.py"
        long_lines_file.write_text(long_line_content)
        
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(long_lines_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("function_with_very_long_line", "renamed_function")
        
        result = refactor.get_code()
        assert "renamed_function" in result

    def test_deeply_nested_structures(self, temp_directory):
        """Test handling of deeply nested code structures."""
        nested_content = '''
def level_1():
    def level_2():
        def level_3():
            def level_4():
                def level_5():
                    class NestedClass:
                        def nested_method(self):
                            if True:
                                if True:
                                    if True:
                                        if True:
                                            return "deeply nested"
                    return NestedClass()
                return level_5()
            return level_4()
        return level_3()
    return level_2()

class OuterClass:
    class MiddleClass:
        class InnerClass:
            def inner_method(self):
                return "inner"
'''
        
        nested_file = temp_directory / "nested.py"
        nested_file.write_text(nested_content)
        
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(nested_file))
        
        assert not ast.is_empty()
        
        # Test refactoring nested structures
        refactor = pyrustor.Refactor(ast)
        refactor.rename_class("NestedClass", "RenamedNestedClass")
        refactor.rename_function("level_1", "renamed_level_1")
        
        result = refactor.get_code()
        assert "RenamedNestedClass" in result
        assert "renamed_level_1" in result

    def test_many_small_functions(self, temp_directory):
        """Test performance with many small functions."""
        # Generate file with many small functions
        many_functions_content = "# File with many small functions\n\n"
        
        for i in range(200):
            many_functions_content += f'''
def function_{i}():
    """Function number {i}."""
    return {i}

'''
        
        many_functions_file = temp_directory / "many_functions.py"
        many_functions_file.write_text(many_functions_content)
        
        # Measure parsing time
        parser = pyrustor.Parser()
        start_time = time.time()
        ast = parser.parse_file(str(many_functions_file))
        parse_time = time.time() - start_time
        
        assert not ast.is_empty()
        assert ast.statement_count() == 200
        
        # Parsing should be reasonably fast (less than 1 second for 200 functions)
        assert parse_time < 1.0
        
        # Test refactoring performance
        refactor = pyrustor.Refactor(ast)
        start_time = time.time()
        
        # Rename a few functions
        for i in range(0, 10):
            refactor.rename_function(f"function_{i}", f"renamed_function_{i}")
        
        refactor_time = time.time() - start_time
        
        # Refactoring should also be reasonably fast
        assert refactor_time < 2.0
        
        result = refactor.get_code()
        assert "renamed_function_0" in result

    def test_complex_string_literals(self, temp_directory):
        """Test handling of complex string literals."""
        complex_strings_content = '''
def string_examples():
    """Function with various string types."""

    # Raw strings
    raw_string = r"Raw string with backslashes"

    # F-strings with complex expressions
    name = "PyRustor"
    f_string = f"Hello {name.upper()}, today is {2024}"

    # Strings with escape sequences
    escaped = "Line 1\\nLine 2\\tTabbed"

    # Unicode strings
    unicode_str = "Unicode: ABC"

    return raw_string, f_string, escaped, unicode_str

class StringProcessor:
    """Class for processing strings."""

    def process_multiline(self):
        return "multiline string"
'''
        
        complex_strings_file = temp_directory / "complex_strings.py"
        complex_strings_file.write_text(complex_strings_content)
        
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(complex_strings_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("string_examples", "renamed_string_examples")
        refactor.rename_class("StringProcessor", "RenamedStringProcessor")
        
        result = refactor.get_code()
        assert "renamed_string_examples" in result
        assert "RenamedStringProcessor" in result

    def test_unusual_identifier_names(self, temp_directory):
        """Test handling of unusual but valid Python identifier names."""
        unusual_names_content = '''
# Unusual but valid Python identifiers
def _private_function():
    return "private"

def __dunder_function__():
    return "dunder"

def function_with_numbers123():
    return "numbers"

def 中文函数名():  # Unicode identifiers (valid in Python 3)
    return "unicode"

class _PrivateClass:
    def __init__(self):
        self._private_attr = "private"
        self.__very_private = "very private"

class CamelCaseClass:
    def camelCaseMethod(self):
        return "camelCase"

# Variables with unusual names
_global_var = "global"
__module_private__ = "module private"
CONSTANT_VALUE = 42
'''
        
        unusual_names_file = temp_directory / "unusual_names.py"
        unusual_names_file.write_text(unusual_names_content, encoding='utf-8')

        parser = pyrustor.Parser()
        ast = parser.parse_file(str(unusual_names_file))
        
        assert not ast.is_empty()
        
        # Test refactoring with unusual names
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("_private_function", "_renamed_private_function")
        refactor.rename_class("_PrivateClass", "_RenamedPrivateClass")
        
        result = refactor.get_code()
        assert "_renamed_private_function" in result
        assert "_RenamedPrivateClass" in result

    def test_memory_usage_with_large_ast(self, temp_directory):
        """Test memory usage with large AST structures."""
        # Generate a file that creates a large AST
        large_ast_content = '''
"""Module that generates a large AST."""

# Large data structure
large_dict = {
'''
        
        # Add many dictionary entries
        for i in range(500):
            large_ast_content += f'    "key_{i}": "value_{i}",\n'
        
        large_ast_content += '''
}

# Large list
large_list = [
'''
        
        # Add many list items
        for i in range(500):
            large_ast_content += f'    {i},\n'
        
        large_ast_content += '''
]

def process_large_data():
    """Process the large data structures."""
    result = {}
    for key, value in large_dict.items():
        result[key] = value.upper()
    return result

class LargeDataProcessor:
    """Process large amounts of data."""
    
    def __init__(self):
        self.data = large_dict.copy()
        self.numbers = large_list.copy()
    
    def process_all(self):
        """Process all data."""
        return [str(x) for x in self.numbers]
'''
        
        large_ast_file = temp_directory / "large_ast.py"
        large_ast_file.write_text(large_ast_content)
        
        # Test parsing and refactoring
        parser = pyrustor.Parser()
        ast = parser.parse_file(str(large_ast_file))
        
        assert not ast.is_empty()
        
        # Test refactoring
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("process_large_data", "renamed_process_large_data")
        refactor.rename_class("LargeDataProcessor", "RenamedLargeDataProcessor")
        
        result = refactor.get_code()
        assert "renamed_process_large_data" in result
        assert "RenamedLargeDataProcessor" in result

    def test_concurrent_parsing_simulation(self, temp_directory):
        """Test behavior that simulates concurrent parsing scenarios."""
        # Create multiple files for concurrent-like testing
        files_content = {}
        
        for i in range(10):
            files_content[f"module_{i}.py"] = f'''
import ConfigParser
import urllib2

def function_{i}():
    """Function {i}."""
    return "Result {i}"

class Class_{i}:
    """Class {i}."""
    
    def method_{i}(self):
        return "Method {i}"
'''
        
        # Write all files
        for filename, content in files_content.items():
            file_path = temp_directory / filename
            file_path.write_text(content)
        
        # Parse all files sequentially (simulating concurrent access patterns)
        parser = pyrustor.Parser()
        results = []
        
        start_time = time.time()
        
        for filename in files_content.keys():
            file_path = temp_directory / filename
            ast = parser.parse_file(str(file_path))
            
            # Apply refactoring
            refactor = pyrustor.Refactor(ast)
            refactor.replace_import("ConfigParser", "configparser")
            refactor.replace_import("urllib2", "urllib.request")
            
            results.append((filename, refactor.get_code()))
        
        total_time = time.time() - start_time
        
        # Should complete in reasonable time
        assert total_time < 5.0
        assert len(results) == 10
        
        # Verify all refactoring was applied
        for filename, code in results:
            assert "configparser" in code or "ConfigParser" not in code
