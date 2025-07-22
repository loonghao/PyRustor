"""
Comprehensive tests for PyRustor Parser functionality.

This module contains thorough tests for the Parser class, covering:
- Basic parsing operations
- Edge cases and error conditions
- Performance characteristics
- Various Python syntax constructs
"""

import pytest
import pyrustor
from pathlib import Path


@pytest.mark.unit
@pytest.mark.parser
class TestParserBasics:
    """Test basic parser functionality."""
    
    def test_parser_creation(self, parser):
        """Test that parser can be created successfully."""
        assert parser is not None
        assert isinstance(parser, pyrustor.Parser)
    
    def test_parse_empty_string(self, parser):
        """Test parsing an empty string."""
        ast = parser.parse_string("")
        assert ast is not None
        assert ast.is_empty()
        assert ast.statement_count() == 0
    
    def test_parse_whitespace_only(self, parser):
        """Test parsing whitespace-only string."""
        ast = parser.parse_string("   \n\t  \n  ")
        assert ast is not None
        assert ast.is_empty()
    
    def test_parse_comments_only(self, parser):
        """Test parsing comments-only code."""
        code = """
        # This is a comment
        # Another comment
        """
        ast = parser.parse_string(code)
        assert ast is not None
        # Comments don't create statements in the AST
        assert ast.is_empty()


@pytest.mark.unit
@pytest.mark.parser
class TestParserFunctions:
    """Test parsing function definitions."""
    
    def test_parse_simple_function(self, parser):
        """Test parsing a simple function."""
        ast = parser.parse_string("def hello(): pass")
        
        assert not ast.is_empty()
        assert ast.statement_count() == 1
        
        functions = ast.function_names()
        assert len(functions) == 1
        assert functions[0] == "hello"
    
    def test_parse_function_with_parameters(self, parser):
        """Test parsing function with parameters."""
        code = "def greet(name, age=25): return f'Hello {name}, age {age}'"
        ast = parser.parse_string(code)
        
        assert not ast.is_empty()
        functions = ast.function_names()
        assert "greet" in functions
    
    def test_parse_function_with_docstring(self, parser):
        """Test parsing function with docstring."""
        code = '''
def documented_function():
    """This function has documentation."""
    return True
'''
        ast = parser.parse_string(code)
        
        assert not ast.is_empty()
        functions = ast.function_names()
        assert "documented_function" in functions
    
    def test_parse_multiple_functions(self, parser, sample_function_code):
        """Test parsing multiple functions."""
        ast = parser.parse_string(sample_function_code)
        
        functions = ast.function_names()
        assert len(functions) == 2
        assert "hello_world" in functions
        assert "calculate_sum" in functions
    
    def test_parse_nested_functions(self, parser):
        """Test parsing nested functions."""
        code = '''
def outer_function():
    def inner_function():
        return "inner"
    return inner_function()
'''
        ast = parser.parse_string(code)
        
        # Only top-level functions should be counted
        functions = ast.function_names()
        assert len(functions) == 1
        assert "outer_function" in functions
    
    def test_parse_async_function(self, parser):
        """Test parsing async function."""
        code = '''
async def async_function():
    await some_operation()
    return "done"
'''
        ast = parser.parse_string(code)
        
        functions = ast.function_names()
        assert "async_function" in functions


@pytest.mark.unit
@pytest.mark.parser
class TestParserClasses:
    """Test parsing class definitions."""
    
    def test_parse_simple_class(self, parser):
        """Test parsing a simple class."""
        ast = parser.parse_string("class TestClass: pass")
        
        assert not ast.is_empty()
        classes = ast.class_names()
        assert len(classes) == 1
        assert classes[0] == "TestClass"
    
    def test_parse_class_with_inheritance(self, parser):
        """Test parsing class with inheritance."""
        code = "class Child(Parent): pass"
        ast = parser.parse_string(code)
        
        classes = ast.class_names()
        assert "Child" in classes
    
    def test_parse_class_with_multiple_inheritance(self, parser):
        """Test parsing class with multiple inheritance."""
        code = "class MultiChild(Parent1, Parent2, Parent3): pass"
        ast = parser.parse_string(code)
        
        classes = ast.class_names()
        assert "MultiChild" in classes
    
    def test_parse_class_with_methods(self, parser, sample_class_code):
        """Test parsing class with methods."""
        ast = parser.parse_string(sample_class_code)
        
        classes = ast.class_names()
        assert len(classes) == 2
        assert "Person" in classes
        assert "Employee" in classes
    
    def test_parse_nested_classes(self, parser):
        """Test parsing nested classes."""
        code = '''
class OuterClass:
    class InnerClass:
        pass
    
    def method(self):
        pass
'''
        ast = parser.parse_string(code)
        
        # Only top-level classes should be counted
        classes = ast.class_names()
        assert len(classes) == 1
        assert "OuterClass" in classes


@pytest.mark.unit
@pytest.mark.parser
class TestParserImports:
    """Test parsing import statements."""
    
    def test_parse_simple_import(self, parser):
        """Test parsing simple import."""
        ast = parser.parse_string("import os")
        
        imports = ast.imports()
        assert len(imports) >= 1
        assert any("os" in imp for imp in imports)
    
    def test_parse_from_import(self, parser):
        """Test parsing from import."""
        ast = parser.parse_string("from sys import path")
        
        imports = ast.imports()
        assert len(imports) >= 1
    
    def test_parse_multiple_imports(self, parser, sample_import_code):
        """Test parsing multiple import statements."""
        ast = parser.parse_string(sample_import_code)
        
        imports = ast.imports()
        assert len(imports) >= 5  # Should have multiple imports
    
    def test_parse_aliased_import(self, parser):
        """Test parsing aliased imports."""
        code = '''
import numpy as np
from pandas import DataFrame as df
'''
        ast = parser.parse_string(code)
        
        imports = ast.imports()
        assert len(imports) >= 2


@pytest.mark.unit
@pytest.mark.parser
@pytest.mark.error_handling
class TestParserErrorHandling:
    """Test parser error handling."""
    
    def test_invalid_syntax_raises_error(self, parser):
        """Test that invalid syntax raises appropriate error."""
        with pytest.raises(ValueError, match=".*[Pp]arse.*"):
            parser.parse_string("def invalid syntax:")
    
    def test_incomplete_function_raises_error(self, parser):
        """Test that incomplete function raises error."""
        with pytest.raises(ValueError):
            parser.parse_string("def incomplete_function(")
    
    def test_invalid_indentation_raises_error(self, parser):
        """Test that invalid indentation raises error."""
        code = '''
def function():
pass  # Invalid indentation
'''
        with pytest.raises(ValueError):
            parser.parse_string(code)
    
    def test_unclosed_string_raises_error(self, parser):
        """Test that unclosed string raises error."""
        with pytest.raises(ValueError):
            parser.parse_string('message = "unclosed string')
    
    def test_invalid_character_raises_error(self, parser):
        """Test that invalid characters raise error."""
        with pytest.raises(ValueError):
            parser.parse_string("def function(): return @invalid")


@pytest.mark.unit
@pytest.mark.parser
@pytest.mark.edge_case
class TestParserEdgeCases:
    """Test parser edge cases."""
    
    def test_very_long_function_name(self, parser):
        """Test parsing function with very long name."""
        long_name = "very_" * 100 + "long_function_name"
        code = f"def {long_name}(): pass"
        
        ast = parser.parse_string(code)
        functions = ast.function_names()
        assert long_name in functions
    
    def test_unicode_in_code(self, parser):
        """Test parsing code with unicode characters."""
        code = '''
def greet_unicode():
    return "Hello 世界! 🌍"

class UnicodeClass:
    """A class with unicode: café, naïve, résumé"""
    pass
'''
        ast = parser.parse_string(code)
        
        assert not ast.is_empty()
        functions = ast.function_names()
        classes = ast.class_names()
        assert "greet_unicode" in functions
        assert "UnicodeClass" in classes
    
    def test_deeply_nested_structures(self, parser):
        """Test parsing deeply nested structures."""
        code = '''
def level1():
    def level2():
        def level3():
            def level4():
                return "deep"
            return level4()
        return level3()
    return level2()
'''
        ast = parser.parse_string(code)
        
        # Should still parse successfully
        functions = ast.function_names()
        assert "level1" in functions
    
    def test_complex_expressions(self, parser):
        """Test parsing complex expressions."""
        code = '''
def complex_function():
    result = (lambda x: x**2 if x > 0 else -x**2)(
        sum([i for i in range(10) if i % 2 == 0])
    )
    return {
        'result': result,
        'data': [x for x in range(result) if x % 3 == 0],
        'nested': {'inner': {'deep': True}}
    }
'''
        ast = parser.parse_string(code)
        
        functions = ast.function_names()
        assert "complex_function" in functions


@pytest.mark.integration
@pytest.mark.parser
class TestParserFileOperations:
    """Test parser file operations."""
    
    def test_parse_from_file(self, parser, temp_python_file):
        """Test parsing from a file."""
        ast = parser.parse_file(temp_python_file)
        
        assert not ast.is_empty()
        functions = ast.function_names()
        classes = ast.class_names()
        
        assert "temp_function" in functions
        assert "TempClass" in classes
    
    def test_parse_nonexistent_file_raises_error(self, parser):
        """Test that parsing nonexistent file raises error."""
        with pytest.raises((FileNotFoundError, ValueError)):
            parser.parse_file("nonexistent_file.py")
    
    def test_parse_empty_file(self, parser, temp_directory):
        """Test parsing an empty file."""
        empty_file = temp_directory / "empty.py"
        empty_file.write_text("")
        
        ast = parser.parse_file(str(empty_file))
        assert ast.is_empty()


@pytest.mark.benchmark
@pytest.mark.parser
@pytest.mark.slow
class TestParserPerformance:
    """Test parser performance characteristics."""
    
    def test_parse_large_file_performance(self, parser, performance_timer):
        """Test parsing performance with large file."""
        # Generate a large Python file
        large_code = "\n".join([
            f"def function_{i}():\n    return {i}"
            for i in range(1000)
        ])
        
        performance_timer.start()
        ast = parser.parse_string(large_code)
        performance_timer.stop()
        
        # Should parse successfully
        assert not ast.is_empty()
        assert ast.statement_count() == 1000
        
        # Performance should be reasonable (less than 1 second for 1000 functions)
        assert performance_timer.elapsed < 1.0
    
    def test_parse_deeply_nested_performance(self, parser, performance_timer):
        """Test parsing performance with deeply nested code."""
        # Generate deeply nested code
        nested_code = "def outer():\n"
        indent = "    "
        for i in range(50):
            nested_code += f"{indent * (i + 1)}def level_{i}():\n"
            nested_code += f"{indent * (i + 2)}pass\n"
        
        performance_timer.start()
        ast = parser.parse_string(nested_code)
        performance_timer.stop()
        
        # Should parse successfully
        assert not ast.is_empty()
        
        # Performance should be reasonable
        assert performance_timer.elapsed < 0.5
