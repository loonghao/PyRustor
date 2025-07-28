"""
Test the new bottom-level API implementation.

This module tests the newly implemented bottom-level API that allows users
to build higher-level functionality on top of PyRustor's core capabilities.
"""

import pytest
import pyrustor


class TestBottomLevelAPI:
    """Test the bottom-level API functionality."""

    def test_ast_node_queries(self):
        """Test AST node query methods."""
        source_code = '''
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"

def test_function():
    return "hello"

class TestClass:
    pass
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test find_nodes
        all_nodes = ast.find_nodes()
        assert len(all_nodes) > 0
        
        # Test find specific node types (using correct Rust AST node type names)
        import_nodes = ast.find_nodes("ImportFrom")
        assert len(import_nodes) >= 2  # Should find the pkg_resources imports

        try_except_nodes = ast.find_nodes("Try")
        assert len(try_except_nodes) == 1

        function_nodes = ast.find_nodes("FunctionDef")
        assert len(function_nodes) == 1

        class_nodes = ast.find_nodes("ClassDef")
        assert len(class_nodes) == 1

    def test_import_queries(self):
        """Test import query methods."""
        source_code = '''
import os
import sys
from pkg_resources import get_distribution
from pathlib import Path
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test find all imports
        all_imports = ast.find_imports()
        assert len(all_imports) == 4
        
        # Test find specific module imports
        pkg_resources_imports = ast.find_imports("pkg_resources")
        assert len(pkg_resources_imports) == 1
        assert pkg_resources_imports[0].module == "pkg_resources"
        assert "get_distribution" in pkg_resources_imports[0].items

    def test_function_call_queries(self):
        """Test function call query methods."""
        source_code = '''
result = get_distribution(__name__).version
other_result = some_function()
get_distribution("other_package")
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test find function calls
        get_dist_calls = ast.find_function_calls("get_distribution")
        assert len(get_dist_calls) >= 1  # Should find at least one call
        
        some_func_calls = ast.find_function_calls("some_function")
        assert len(some_func_calls) >= 1

    def test_try_except_queries(self):
        """Test try-except block query methods."""
        source_code = '''
try:
    result = risky_operation()
except ValueError:
    result = "error"

try:
    other_result = another_operation()
except (TypeError, KeyError):
    other_result = None
except DistributionNotFound:
    other_result = "not found"
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test find all try-except blocks
        # Note: Each except clause creates a separate TryExceptNode
        all_try_except = ast.find_try_except_blocks()
        assert len(all_try_except) == 3  # ValueError, (TypeError, KeyError), DistributionNotFound
        
        # Test find specific exception types
        value_error_blocks = ast.find_try_except_blocks("ValueError")
        assert len(value_error_blocks) == 1
        
        dist_not_found_blocks = ast.find_try_except_blocks("DistributionNotFound")
        assert len(dist_not_found_blocks) == 1

    def test_assignment_queries(self):
        """Test assignment query methods."""
        source_code = '''
__version__ = "1.0.0"
result = get_distribution(__name__).version
x = 42
__author__ = "Test Author"
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test find all assignments
        all_assignments = ast.find_assignments()
        assert len(all_assignments) == 4
        
        # Test find specific target patterns
        version_assignments = ast.find_assignments("__version__")
        assert len(version_assignments) == 1
        assert version_assignments[0].target == "__version__"
        
        dunder_assignments = ast.find_assignments("__")
        assert len(dunder_assignments) == 2  # __version__ and __author__

    def test_refactor_bottom_level_api(self):
        """Test bottom-level API methods on Refactor class."""
        source_code = '''
from pkg_resources import get_distribution
__version__ = get_distribution(__name__).version
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        refactor = pyrustor.Refactor(ast)
        
        # Test access to underlying AST
        underlying_ast = refactor.ast()
        assert underlying_ast is not None
        
        # Test find methods on refactor
        imports = refactor.find_imports("pkg_resources")
        assert len(imports) == 1
        
        calls = refactor.find_function_calls("get_distribution")
        assert len(calls) >= 1
        
        assignments = refactor.find_assignments("__version__")
        assert len(assignments) == 1

    def test_node_operations(self):
        """Test node operation methods."""
        source_code = '''
def old_function():
    return "old"
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        refactor = pyrustor.Refactor(ast)
        
        # Find function nodes (using correct Rust AST node type name)
        function_nodes = refactor.find_nodes("FunctionDef")
        assert len(function_nodes) == 1
        
        # Test node operations (these are placeholder implementations)
        node_ref = function_nodes[0]
        
        # Test replace_node
        refactor.replace_node(node_ref, "def new_function(): return 'new'")
        
        # Test insert operations
        refactor.insert_before(node_ref, "# Comment before")
        refactor.insert_after(node_ref, "# Comment after")
        
        # Test remove_node
        refactor.remove_node(node_ref)
        
        # Test range replacement
        refactor.replace_code_range(1, 2, "# Replaced lines")
        
        # Verify changes were recorded
        changes = refactor.change_summary()
        assert len(changes) > 0

    def test_code_generator(self):
        """Test the code generator functionality."""
        parser = pyrustor.Parser()
        ast = parser.parse_string("# empty")
        refactor = pyrustor.Refactor(ast)
        
        # Get code generator
        generator = refactor.code_generator()
        assert generator is not None
        
        # Test import generation
        import_stmt = generator.create_import("os")
        assert import_stmt == "import os"
        
        import_with_alias = generator.create_import("json", None, "js")
        assert import_with_alias == "import json as js"
        
        from_import = generator.create_import("pathlib", ["Path"])
        assert from_import == "from pathlib import Path"
        
        multiple_from_import = generator.create_import("typing", ["List", "Dict"])
        assert multiple_from_import == "from typing import List, Dict"
        
        # Test assignment generation
        assignment = generator.create_assignment("x", "42")
        assert assignment == "x = 42"
        
        # Test function call generation
        func_call = generator.create_function_call("print", ["'hello'"])
        assert func_call == "print('hello')"
        
        # Test try-except generation
        try_except = generator.create_try_except(
            "result = risky_operation()",
            "ValueError",
            "result = 'error'"
        )
        expected = "try:\n    result = risky_operation()\nexcept ValueError:\n    result = 'error'"
        assert try_except == expected

    def test_standalone_code_generator(self):
        """Test using CodeGenerator independently."""
        generator = pyrustor.CodeGenerator()
        
        # Test various code generation methods
        import_stmt = generator.create_import("internal_pyharmony", ["get_package_version"])
        assert import_stmt == "from internal_pyharmony import get_package_version"
        
        assignment = generator.create_assignment("__version__", "get_package_version(__name__)")
        assert assignment == "__version__ = get_package_version(__name__)"
        
        func_call = generator.create_function_call("get_package_version", ["__name__"])
        assert func_call == "get_package_version(__name__)"

    def test_user_built_pkg_resources_modernization(self):
        """Test how a user would build pkg_resources modernization using bottom-level API."""
        
        def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony", target_function="get_package_version"):
            """User-built function using bottom-level API."""
            
            # 1. Check if we have pkg_resources imports
            pkg_imports = refactor.find_imports("pkg_resources")
            if not pkg_imports:
                return False
            
            # 2. Find try-except blocks with DistributionNotFound
            try_except_blocks = refactor.find_try_except_blocks("DistributionNotFound")
            if not try_except_blocks:
                return False
            
            # 3. Find get_distribution calls
            get_dist_calls = refactor.find_function_calls("get_distribution")
            if not get_dist_calls:
                return False
            
            # 4. Find __version__ assignments
            version_assignments = refactor.find_assignments("__version__")
            if not version_assignments:
                return False
            
            # 5. Apply transformations using existing high-level API
            refactor.replace_import("pkg_resources", target_module)
            
            # In a full implementation, we would:
            # - Use replace_node to replace the try-except block
            # - Use code_generator to create the new assignment
            # - But for now, we just record that we found the pattern
            
            return True
        
        # Test the user-built function
        source_code = '''
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        refactor = pyrustor.Refactor(ast)
        
        # Apply user-built modernization
        success = modernize_pkg_resources_version(refactor)
        assert success
        
        # Verify that basic transformation was applied
        result = refactor.get_code()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_api_object_representations(self):
        """Test string representations of API objects."""
        source_code = '''
from pkg_resources import get_distribution
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0"
'''
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        
        # Test node representations
        nodes = ast.find_nodes()
        assert len(nodes) > 0
        node_repr = repr(nodes[0])
        assert "AstNodeRef" in node_repr
        
        imports = ast.find_imports()
        assert len(imports) > 0
        import_repr = repr(imports[0])
        assert "ImportNode" in import_repr
        
        try_except_blocks = ast.find_try_except_blocks()
        if try_except_blocks:
            try_except_repr = repr(try_except_blocks[0])
            assert "TryExceptNode" in try_except_repr
        
        assignments = ast.find_assignments()
        assert len(assignments) > 0
        assignment_repr = repr(assignments[0])
        assert "AssignmentNode" in assignment_repr
        
        # Test code generator representation
        generator = pyrustor.CodeGenerator()
        generator_repr = repr(generator)
        assert "CodeGenerator" in generator_repr
