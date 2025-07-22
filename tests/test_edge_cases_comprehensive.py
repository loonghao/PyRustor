"""
Comprehensive edge case and error handling tests for PyRustor.

This module tests various edge cases, boundary conditions, and error scenarios
to ensure robust behavior under adverse conditions.
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


@pytest.mark.unit
@pytest.mark.edge_case
class TestParserEdgeCases:
    """Test parser edge cases and boundary conditions."""
    
    def test_extremely_long_names(self, parser):
        """Test handling of extremely long identifiers."""
        # Very long but valid function name
        long_func_name = "function_" + "a" * 10000
        code = f"def {long_func_name}(): pass"
        
        ast = parser.parse_string(code)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert long_func_name in functions
        
        # Very long class name
        long_class_name = "Class" + "B" * 10000
        code = f"class {long_class_name}: pass"
        
        ast = parser.parse_string(code)
        classes = ast.class_names()
        assert long_class_name in classes
    
    def test_unicode_identifiers_and_strings(self, parser):
        """Test unicode in identifiers and string literals."""
        code = '''
def greet_世界():
    """Function with unicode name."""
    return "Hello 世界! 🌍 café naïve résumé"

class UnicodeClass_测试:
    """Class with unicode: café, naïve, résumé"""
    
    def method_测试(self):
        return "测试方法"
    
    def emoji_method_rocket(self):
        return "🚀 Rocket method!"

# Unicode variables
变量 = "Unicode variable"
café = "French café"
'''
        
        ast = parser.parse_string(code)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        classes = ast.class_names()
        
        assert "greet_世界" in functions
        assert "UnicodeClass_测试" in classes
    
    def test_deeply_nested_structures(self, parser):
        """Test deeply nested function and class structures."""
        # Generate deeply nested functions
        code = "def level0():\n"
        indent = "    "
        
        for i in range(1, 50):
            code += f"{indent * i}def level{i}():\n"
            code += f"{indent * (i + 1)}return 'level{i}'\n"
        
        ast = parser.parse_string(code)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert "level0" in functions
    
    def test_complex_expressions(self, parser):
        """Test parsing complex Python expressions."""
        code = '''
def complex_expressions():
    # Complex list comprehension
    result = [
        x**2 + y**2 
        for x in range(10) 
        for y in range(10) 
        if (x + y) % 2 == 0 and x != y
    ]
    
    # Complex dictionary comprehension
    mapping = {
        f"key_{i}_{j}": [k for k in range(i*j) if k % 2 == 0]
        for i in range(5)
        for j in range(5)
        if i != j and (i + j) % 3 == 0
    }
    
    # Complex lambda expressions
    processor = lambda data: (
        lambda x: x**2 if x > 0 else -x**2
    )(sum(filter(lambda y: y % 2 == 0, data)))
    
    # Complex generator expression
    gen = (
        x * y * z
        for x in range(3)
        for y in range(3)
        for z in range(3)
        if x + y + z > 5
    )
    
    return result, mapping, processor, list(gen)

class ComplexClass:
    """Class with complex features."""
    
    @property
    @staticmethod
    def complex_property():
        return {
            'nested': {
                'deep': {
                    'very_deep': {
                        'extremely_deep': True
                    }
                }
            }
        }
    
    @classmethod
    def complex_classmethod(cls, *args, **kwargs):
        return cls(*args, **kwargs)

# Complex inheritance
class MultipleInheritance(dict, list):
    """Class with multiple inheritance."""
    pass

# Complex decorator usage
def complex_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@complex_decorator
def decorated_function():
    pass
'''
        
        ast = parser.parse_string(code)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        classes = ast.class_names()
        
        assert "complex_expressions" in functions
        assert "ComplexClass" in classes
        assert "MultipleInheritance" in classes
        assert "complex_decorator" in functions
        assert "decorated_function" in functions
    
    def test_special_string_literals(self, parser):
        """Test various string literal formats."""
        code = r'''
def string_literals():
    # Regular strings
    regular = "Hello world"
    single_quotes = 'Hello world'
    
    # Escape sequences
    escaped = "Line 1\nLine 2\tTabbed\r\nWindows line ending"
    quotes = "He said \"Hello\" and she said 'Hi'"
    backslashes = "Path: C:\\Users\\Name\\file.txt"
    
    # Unicode escapes
    unicode_escapes = "\u0048\u0065\u006c\u006c\u006f"  # "Hello"
    unicode_name = "\N{GREEK CAPITAL LETTER DELTA}"
    
    # Raw strings
    regex = r"^\d{3}-\d{2}-\d{4}$"
    raw_backslashes = r"C:\Users\Name\file.txt"
    
    # Triple quoted strings
    multiline = """
    This is a multiline string
    with "quotes" and 'apostrophes'
    and even \n escape sequences
    """
    
    raw_multiline = r"""
    Raw multiline string
    with \n literal backslashes
    """
    
    # f-strings (format strings)
    name = "World"
    f_string = f"Hello {name}!"
    f_complex = f"Result: {2 + 2} = {2 * 2}"
    
    # Bytes
    byte_string = b"Hello bytes"
    
    return (regular, single_quotes, escaped, quotes, backslashes,
            unicode_escapes, unicode_name, regex, raw_backslashes,
            multiline, raw_multiline, f_string, f_complex, byte_string)
'''
        
        ast = parser.parse_string(code)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert "string_literals" in functions
    
    def test_empty_and_minimal_constructs(self, parser):
        """Test empty and minimal Python constructs."""
        test_cases = [
            ("", True),  # Empty string -> empty AST
            ("pass", False),  # Just pass -> not empty
            ("# Just a comment", True),  # Just comment -> empty
            ("'''Just a docstring'''", False),  # Just docstring -> not empty
            ("def f(): pass", False),  # Minimal function -> not empty
            ("class C: pass", False),  # Minimal class -> not empty
            ("x = 1", False),  # Simple assignment -> not empty
            ("import os", False),  # Simple import -> not empty
            ("   \n\t  \n  ", True),  # Whitespace only -> empty
        ]
        
        for code, should_be_empty in test_cases:
            ast = parser.parse_string(code)
            assert ast is not None
            if should_be_empty:
                assert ast.is_empty()
            else:
                assert not ast.is_empty()


@pytest.mark.unit
@pytest.mark.edge_case
class TestRefactorEdgeCases:
    """Test refactor edge cases and boundary conditions."""
    
    def test_rename_to_same_name(self, parser):
        """Test renaming to the same name."""
        ast = parser.parse_string("def function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Rename to same name should work
        refactor.rename_function("function", "function")
        
        result = refactor.get_code()
        assert "def function" in result
        
        # Should record the change even if it's the same name
        summary = refactor.change_summary()
        assert "1 changes" in summary
    
    def test_multiple_renames_same_target(self, parser):
        """Test multiple renames of the same function."""
        ast = parser.parse_string("def original_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Chain of renames
        refactor.rename_function("original_function", "intermediate_function")
        refactor.rename_function("intermediate_function", "final_function")
        
        result = refactor.get_code()
        assert "def final_function" in result
        assert "def original_function" not in result
        assert "def intermediate_function" not in result
        
        # Should record multiple changes
        summary = refactor.change_summary()
        assert "2 changes" in summary
    
    def test_rename_with_special_characters(self, parser):
        """Test renaming with special characters (may produce invalid code)."""
        ast = parser.parse_string("def valid_function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # These might produce invalid Python code but shouldn't crash
        special_names = [
            "function-with-dashes",
            "function.with.dots",
            "function with spaces",
            "function@with@symbols",
            "123numeric_start",
            "",  # Empty name
        ]
        
        for special_name in special_names:
            try:
                refactor.rename_function("valid_function", special_name)
                result = refactor.get_code()
                assert result is not None
                # Reset for next test
                refactor.rename_function(special_name, "valid_function")
            except ValueError:
                # Some special names might be rejected
                pass
    
    def test_refactor_empty_ast(self, parser):
        """Test refactoring operations on empty AST."""
        ast = parser.parse_string("")
        refactor = pyrustor.Refactor(ast)
        
        # These operations should not crash on empty AST
        refactor.modernize_syntax()
        refactor.replace_import("nonexistent", "also_nonexistent")
        
        result = refactor.get_code()
        assert result == ""
        
        summary = refactor.change_summary()
        assert "No changes made" in summary
    
    def test_refactor_with_unicode_names(self, parser):
        """Test refactoring with unicode names."""
        code = '''
def hello_世界(): pass
class Test_测试: pass
'''
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        # Rename with unicode
        refactor.rename_function("hello_世界", "greet_世界")
        refactor.rename_class("Test_测试", "Class_测试")
        
        result = refactor.get_code()
        assert "def greet_世界" in result
        assert "class Class_测试" in result


@pytest.mark.unit
@pytest.mark.error_handling
class TestErrorConditions:
    """Test various error conditions and exception handling."""
    
    def test_invalid_syntax_errors(self, parser):
        """Test that invalid syntax raises appropriate errors."""
        invalid_codes = [
            "def func(",  # Unclosed parenthesis
            "def func(x, y",  # Unclosed parenthesis
            "print('hello'",  # Unclosed quote
            "def 123invalid(): pass",  # Invalid identifier
            "class 456Invalid: pass",  # Invalid identifier
            "def func(): return @invalid",  # Invalid token
            "if True\n    pass",  # Missing colon
            "def func():\npass",  # Invalid indentation
        ]
        
        for code in invalid_codes:
            with pytest.raises(ValueError):
                parser.parse_string(code)
    
    def test_refactor_nonexistent_targets(self, parser):
        """Test refactoring nonexistent functions/classes."""
        ast = parser.parse_string("def existing(): pass\nclass Existing: pass")
        refactor = pyrustor.Refactor(ast)
        
        # These should raise errors
        with pytest.raises(ValueError, match=".*not found.*"):
            refactor.rename_function("nonexistent", "new_name")
        
        with pytest.raises(ValueError, match=".*not found.*"):
            refactor.rename_class("NonexistentClass", "NewClass")
    
    def test_file_operation_errors(self, parser, temp_directory):
        """Test file operation error conditions."""
        ast = parser.parse_string("def function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Test saving to invalid paths
        invalid_paths = [
            "/invalid/path/that/does/not/exist.py",
            str(temp_directory / "nonexistent_dir" / "file.py"),
        ]
        
        for path in invalid_paths:
            with pytest.raises((FileNotFoundError, OSError, ValueError)):
                refactor.save_to_file(path)
        
        # Test parsing nonexistent files
        with pytest.raises((FileNotFoundError, ValueError)):
            parser.parse_file("nonexistent_file.py")
    
    def test_permission_errors(self, parser, temp_directory):
        """Test permission-related errors."""
        if os.name == 'nt':  # Windows
            pytest.skip("Permission tests not reliable on Windows")
        
        ast = parser.parse_string("def function(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Create a read-only file
        readonly_file = temp_directory / "readonly.py"
        readonly_file.write_text("# readonly")
        readonly_file.chmod(0o444)  # Read-only
        
        try:
            with pytest.raises(PermissionError):
                refactor.save_to_file(str(readonly_file))
        finally:
            # Cleanup - restore write permissions
            readonly_file.chmod(0o644)


@pytest.mark.benchmark
@pytest.mark.slow
class TestPerformanceEdgeCases:
    """Test performance characteristics under extreme conditions."""
    
    def test_large_file_parsing(self, parser, performance_timer):
        """Test parsing very large files."""
        # Generate a large Python file
        large_code = "\n".join([
            f"def function_{i}():\n    return {i}"
            for i in range(2000)
        ])
        
        performance_timer.start()
        ast = parser.parse_string(large_code)
        performance_timer.stop()
        
        assert not ast.is_empty()
        assert ast.statement_count() == 2000
        
        functions = ast.function_names()
        assert len(functions) == 2000
        
        # Should complete in reasonable time
        assert performance_timer.elapsed < 2.0
    
    def test_large_refactoring_operations(self, parser, performance_timer):
        """Test refactoring operations on large codebases."""
        # Generate code with many functions
        functions = [f"def func_{i}(): return {i}" for i in range(1000)]
        code = "\n".join(functions)
        
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)
        
        performance_timer.start()
        
        # Rename every 10th function
        for i in range(0, 1000, 10):
            refactor.rename_function(f"func_{i}", f"renamed_func_{i}")
        
        result = refactor.get_code()
        
        performance_timer.stop()
        
        assert "renamed_func_0" in result
        assert "renamed_func_990" in result
        
        # Should complete in reasonable time
        assert performance_timer.elapsed < 3.0
    
    def test_memory_intensive_operations(self, parser):
        """Test memory-intensive parsing and refactoring."""
        # Generate code with many classes and functions
        code_parts = []
        
        # Add many functions
        for i in range(500):
            code_parts.append(f"def function_{i}(): return {i}")
        
        # Add many classes
        for i in range(500):
            code_parts.append(f"class Class_{i}: pass")
        
        large_code = "\n".join(code_parts)
        
        # Parse the large code
        ast = parser.parse_string(large_code)
        assert not ast.is_empty()
        assert ast.statement_count() == 1000
        
        # Refactor some elements
        refactor = pyrustor.Refactor(ast)
        
        # Rename some functions and classes
        for i in range(0, 500, 50):
            refactor.rename_function(f"function_{i}", f"renamed_function_{i}")
        
        for i in range(0, 500, 50):
            refactor.rename_class(f"Class_{i}", f"RenamedClass_{i}")
        
        result = refactor.get_code()
        assert "renamed_function_0" in result
        assert "RenamedClass_0" in result
