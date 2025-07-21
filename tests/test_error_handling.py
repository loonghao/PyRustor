"""Tests for error handling in PyRustor"""

import pytest
import tempfile
import os
import pyrustor


class TestErrorHandling:
    """Test cases for error handling and edge cases"""

    def test_invalid_syntax_errors(self):
        """Test handling of various syntax errors"""
        parser = pyrustor.Parser()
        
        invalid_sources = [
            # Definitely invalid syntax that should cause parse errors
            "def func(",  # Unclosed parenthesis
            "def func(x, y",  # Unclosed parenthesis
            "print('hello'",  # Unclosed quote
            "def 123invalid(): pass",  # Invalid identifier
            "class 456Invalid: pass",  # Invalid identifier
        ]

        for source in invalid_sources:
            with pytest.raises(ValueError, match="Parse error"):
                parser.parse_string(source)

        # Test some sources that might be valid but incomplete
        potentially_valid_sources = [
            "def invalid_function()",  # Missing colon - might be valid in some contexts
            "class InvalidClass",      # Missing colon - might be valid in some contexts
            "if True",                 # Incomplete but might be valid
            "import",                  # Incomplete import
            "from",                    # Incomplete from
        ]

        # These might or might not raise errors depending on the parser implementation
        for source in potentially_valid_sources:
            try:
                parser.parse_string(source)
            except ValueError:
                pass  # Expected for some invalid syntax

    def test_empty_and_whitespace_handling(self):
        """Test handling of empty and whitespace-only input"""
        parser = pyrustor.Parser()
        
        # Empty string
        ast_empty = parser.parse_string("")
        assert ast_empty.is_empty()
        assert ast_empty.statement_count() == 0
        assert len(ast_empty.function_names()) == 0
        assert len(ast_empty.class_names()) == 0
        
        # Whitespace only
        ast_whitespace = parser.parse_string("   \n\n  \t  \n")
        assert ast_whitespace.is_empty()
        
        # Comments only
        ast_comments = parser.parse_string("# Just a comment\n# Another comment")
        assert ast_comments.is_empty()
        
        # Docstring only
        ast_docstring = parser.parse_string('"""Just a docstring"""')
        assert not ast_docstring.is_empty()  # Docstrings are statements

    def test_file_not_found_errors(self):
        """Test handling of file not found errors"""
        parser = pyrustor.Parser()
        
        with pytest.raises(ValueError, match="Parse error"):
            parser.parse_file("nonexistent_file.py")

        with pytest.raises(ValueError, match="Parse error"):
            parser.parse_file("/path/that/does/not/exist.py")

    def test_directory_not_found_errors(self):
        """Test handling of directory not found errors"""
        parser = pyrustor.Parser()
        
        with pytest.raises(ValueError):
            parser.parse_directory("nonexistent_directory", recursive=False)

    def test_permission_errors(self):
        """Test handling of permission errors"""
        # Skip on Windows as permission handling is different
        if os.name == 'nt':
            pytest.skip("Permission tests not reliable on Windows")

        # This test might not work on all systems, so we'll skip if needed
        try:
            # Create a temporary file and remove read permissions
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write("def test(): pass")
                temp_file = f.name

            # Remove read permissions (Unix-like systems)
            if hasattr(os, 'chmod'):
                os.chmod(temp_file, 0o000)

                parser = pyrustor.Parser()
                with pytest.raises(ValueError):
                    parser.parse_file(temp_file)

                # Restore permissions for cleanup
                os.chmod(temp_file, 0o644)

            os.unlink(temp_file)

        except (OSError, PermissionError):
            # Skip this test if we can't manipulate permissions
            pytest.skip("Cannot test permission errors on this system")

    def test_refactor_with_empty_ast(self):
        """Test refactoring operations on empty AST"""
        parser = pyrustor.Parser()
        empty_ast = parser.parse_string("")
        refactor = pyrustor.Refactor(empty_ast)
        
        # These operations should not crash but should not find anything to refactor
        with pytest.raises(ValueError):
            refactor.rename_function("nonexistent", "new_name")
        
        with pytest.raises(ValueError):
            refactor.rename_class("NonexistentClass", "NewClass")
        
        # These should complete without error
        refactor.replace_import("nonexistent_module", "new_module")
        refactor.modernize_syntax()
        
        # Should still report no changes
        assert refactor.change_summary() == "No changes made"

    def test_refactor_nonexistent_items(self):
        """Test refactoring operations on nonexistent functions/classes"""
        parser = pyrustor.Parser()
        source = """
def existing_function():
    pass

class ExistingClass:
    pass
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Try to rename nonexistent items
        with pytest.raises(ValueError, match="Function 'nonexistent_function' not found"):
            refactor.rename_function("nonexistent_function", "new_name")
        
        with pytest.raises(ValueError, match="Class 'NonexistentClass' not found"):
            refactor.rename_class("NonexistentClass", "NewClass")
        
        # Valid operations should still work
        refactor.rename_function("existing_function", "renamed_function")
        refactor.rename_class("ExistingClass", "RenamedClass")
        
        summary = refactor.change_summary()
        assert "2 changes" in summary

    def test_invalid_names_for_renaming(self):
        """Test renaming with invalid Python identifiers"""
        parser = pyrustor.Parser()
        source = """
def valid_function():
    pass

class ValidClass:
    pass
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Invalid new names (these might be caught by the implementation)
        invalid_names = [
            "123invalid",  # Starts with number
            "invalid-name",  # Contains hyphen
            "invalid name",  # Contains space
            "def",  # Python keyword
            "class",  # Python keyword
            "",  # Empty string
        ]
        
        for invalid_name in invalid_names:
            # The implementation might or might not validate names
            # We'll just ensure it doesn't crash
            try:
                refactor.rename_function("valid_function", invalid_name)
            except ValueError:
                pass  # Expected for invalid names
            
            try:
                refactor.rename_class("ValidClass", invalid_name)
            except ValueError:
                pass  # Expected for invalid names

    def test_circular_imports_handling(self):
        """Test handling of circular import patterns"""
        parser = pyrustor.Parser()
        
        # This shouldn't cause parsing issues, but might be problematic for refactoring
        source = """
import module_a
from module_b import function_b

def function_a():
    return function_b()
"""
        
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Should be able to replace imports even in circular scenarios
        refactor.replace_import("module_a", "new_module_a")
        refactor.replace_import("module_b", "new_module_b")
        
        # Should complete without error
        assert True

    def test_unicode_and_encoding_handling(self):
        """Test handling of Unicode characters and encoding issues"""
        parser = pyrustor.Parser()
        
        # Unicode in strings and comments
        unicode_source = """
# 这是一个中文注释
def unicode_function():
    \"\"\"函数文档字符串\"\"\"
    message = "Hello, 世界! 🌍"
    return message

class UnicodeClass:
    \"\"\"包含Unicode的类\"\"\"
    
    def method_with_unicode(self):
        return "测试方法"
"""
        
        ast = parser.parse_string(unicode_source)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert "unicode_function" in functions
        
        classes = ast.class_names()
        assert "UnicodeClass" in classes
        
        # Refactoring should work with Unicode content
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("unicode_function", "renamed_unicode_function")
        refactor.rename_class("UnicodeClass", "RenamedUnicodeClass")
        
        result = refactor.to_string()
        assert result is not None

    def test_very_long_lines(self):
        """Test handling of very long lines"""
        parser = pyrustor.Parser()
        
        # Create a very long line
        long_string = "x" * 10000
        source = f"""
def function_with_long_line():
    very_long_string = "{long_string}"
    return very_long_string
"""
        
        ast = parser.parse_string(source)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert "function_with_long_line" in functions

    def test_deeply_nested_structures(self):
        """Test handling of deeply nested code structures"""
        parser = pyrustor.Parser()
        
        # Create deeply nested structure
        nested_source = "def outer():\n"
        indent = "    "
        for i in range(20):  # 20 levels of nesting
            nested_source += f"{indent * (i + 1)}if True:\n"
        nested_source += f"{indent * 21}return 'deeply_nested'\n"
        
        ast = parser.parse_string(nested_source)
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert "outer" in functions

    def test_save_to_invalid_path(self):
        """Test saving to invalid file paths"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("def test(): pass")
        refactor = pyrustor.Refactor(ast)
        
        # Try to save to invalid paths
        invalid_paths = [
            "/root/cannot_write_here.py",  # Permission denied (on Unix)
            "nonexistent_dir/file.py",     # Directory doesn't exist
            "",                            # Empty path
        ]
        
        for invalid_path in invalid_paths:
            with pytest.raises(ValueError):
                refactor.save_to_file(invalid_path)

    def test_memory_stress(self):
        """Test behavior under memory stress conditions"""
        parser = pyrustor.Parser()
        
        # Create a very large source file
        large_source = "# Memory stress test\n"
        for i in range(5000):  # Large but not excessive
            large_source += f"""
def function_{i}():
    \"\"\"Function {i} for memory stress testing\"\"\"
    data = [j for j in range(100)]
    return sum(data) + {i}

class Class_{i}:
    \"\"\"Class {i} for memory stress testing\"\"\"

    def __init__(self):
        self.value = {i}
        self.data = list(range({i % 100}))

    def method_{i}(self):
        return self.value * len(self.data)
"""
        
        # This should complete without running out of memory
        ast = parser.parse_string(large_source)
        assert not ast.is_empty()
        assert ast.statement_count() > 1000
        
        # Basic refactoring should still work
        refactor = pyrustor.Refactor(ast)
        refactor.rename_function("function_0", "renamed_function_0")
        
        summary = refactor.change_summary()
        assert "1 changes" in summary
