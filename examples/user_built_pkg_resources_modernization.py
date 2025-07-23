#!/usr/bin/env python3
"""
Example: User-built pkg_resources modernization using PyRustor's bottom-level API.

This example demonstrates how users can build their own high-level functionality
on top of PyRustor's bottom-level API, specifically showing how to modernize
pkg_resources version detection patterns.
"""

import pyrustor


def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony", target_function="get_package_version"):
    """
    User-built function to modernize pkg_resources version detection.
    
    Transforms:
        from pkg_resources import DistributionNotFound
        from pkg_resources import get_distribution
        
        try:
            __version__ = get_distribution(__name__).version
        except DistributionNotFound:
            __version__ = "0.0.0-dev.1"
    
    Into:
        from internal_pyharmony import get_package_version
        
        __version__ = get_package_version(__name__)
    
    Args:
        refactor: PyRustor Refactor instance
        target_module: Module to import the new function from
        target_function: Function name to use for version detection
    
    Returns:
        bool: True if modernization was applied, False if pattern not found
    """
    
    print("🔍 Analyzing code for pkg_resources version detection pattern...")
    
    # Step 1: Check if we have pkg_resources imports
    pkg_imports = refactor.find_imports("pkg_resources")
    if not pkg_imports:
        print("❌ No pkg_resources imports found")
        return False
    
    print(f"✅ Found {len(pkg_imports)} pkg_resources imports")
    for imp in pkg_imports:
        print(f"   - {imp.module}: {imp.items}")
    
    # Step 2: Find try-except blocks with DistributionNotFound
    try_except_blocks = refactor.find_try_except_blocks("DistributionNotFound")
    if not try_except_blocks:
        print("❌ No try-except blocks with DistributionNotFound found")
        return False
    
    print(f"✅ Found {len(try_except_blocks)} DistributionNotFound try-except blocks")
    
    # Step 3: Find get_distribution calls
    get_dist_calls = refactor.find_function_calls("get_distribution")
    if not get_dist_calls:
        print("❌ No get_distribution calls found")
        return False
    
    print(f"✅ Found {len(get_dist_calls)} get_distribution calls")
    
    # Step 4: Find __version__ assignments
    version_assignments = refactor.find_assignments("__version__")
    if not version_assignments:
        print("❌ No __version__ assignments found")
        return False
    
    print(f"✅ Found {len(version_assignments)} __version__ assignments")
    
    # Step 5: Apply transformations
    print(f"🔧 Applying modernization...")
    
    # Replace pkg_resources imports with target module
    print(f"   - Replacing pkg_resources imports with {target_module}")
    refactor.replace_import("pkg_resources", target_module)
    
    # In a full implementation, we would:
    # 1. Use replace_node to replace the try-except block with simple assignment
    # 2. Use code_generator to create the new assignment
    # 3. Remove unused imports
    
    # For demonstration, we'll show how the code generator would be used:
    generator = refactor.code_generator()
    
    # Generate the new import statement
    new_import = generator.create_import(target_module, [target_function])
    print(f"   - Generated new import: {new_import}")
    
    # Generate the new assignment
    new_assignment = generator.create_assignment("__version__", f"{target_function}(__name__)")
    print(f"   - Generated new assignment: {new_assignment}")
    
    print("✅ Modernization completed!")
    return True


def demonstrate_bottom_level_api():
    """Demonstrate the bottom-level API capabilities."""
    
    print("=" * 60)
    print("PyRustor Bottom-Level API Demonstration")
    print("=" * 60)
    
    # Example code with pkg_resources pattern
    source_code = '''
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = "0.0.0-dev.1"

def some_function():
    """Example function."""
    return "hello"
'''
    
    print("\n📝 Original Code:")
    print(source_code)
    
    # Parse the code
    parser = pyrustor.Parser()
    ast = parser.parse_string(source_code)
    refactor = pyrustor.Refactor(ast)
    
    print("\n🔍 AST Analysis:")
    print(f"   - Total statements: {ast.statement_count()}")
    print(f"   - Function names: {ast.function_names()}")
    print(f"   - Class names: {ast.class_names()}")
    imports = ast.find_imports()
    print(f"   - Imports: {[f'{imp.module}: {imp.items}' for imp in imports]}")
    
    print("\n🔧 Bottom-Level API Queries:")
    
    # Demonstrate node queries
    all_nodes = ast.find_nodes()
    print(f"   - Total nodes found: {len(all_nodes)}")
    
    import_nodes = ast.find_imports("pkg_resources")
    print(f"   - pkg_resources imports: {len(import_nodes)}")
    
    function_calls = ast.find_function_calls("get_distribution")
    print(f"   - get_distribution calls: {len(function_calls)}")
    
    try_except_blocks = ast.find_try_except_blocks("DistributionNotFound")
    print(f"   - DistributionNotFound blocks: {len(try_except_blocks)}")
    
    version_assignments = ast.find_assignments("__version__")
    print(f"   - __version__ assignments: {len(version_assignments)}")
    
    print("\n🚀 Applying User-Built Modernization:")
    
    # Apply user-built modernization
    success = modernize_pkg_resources_version(refactor)
    
    if success:
        print("\n📄 Refactored Code:")
        result = refactor.get_code()
        print(result)
        
        print("\n📊 Change Summary:")
        summary = refactor.change_summary()
        print(summary)
    else:
        print("\n❌ Modernization could not be applied")


def demonstrate_code_generator():
    """Demonstrate the code generator capabilities."""
    
    print("\n" + "=" * 60)
    print("Code Generator Demonstration")
    print("=" * 60)
    
    # Create a standalone code generator
    generator = pyrustor.CodeGenerator()
    
    print("\n🏗️  Code Generation Examples:")
    
    # Import statements
    print("\n📦 Import Statements:")
    print(f"   - Simple import: {generator.create_import('os')}")
    print(f"   - Import with alias: {generator.create_import('json', None, 'js')}")
    print(f"   - From import: {generator.create_import('pathlib', ['Path'])}")
    print(f"   - Multiple from import: {generator.create_import('typing', ['List', 'Dict'])}")
    
    # Assignments
    print("\n📝 Assignment Statements:")
    print(f"   - Simple assignment: {generator.create_assignment('x', '42')}")
    print(f"   - Function call assignment: {generator.create_assignment('result', 'func(arg1, arg2)')}")
    
    # Function calls
    print("\n📞 Function Calls:")
    print(f"   - No args: {generator.create_function_call('func', [])}")
    hello_arg = "'hello'"
    print(f"   - With args: {generator.create_function_call('print', [hello_arg])}")
    print(f"   - Multiple args: {generator.create_function_call('max', ['a', 'b'])}")
    
    # Try-except blocks
    print("\n🛡️  Try-Except Blocks:")
    try_except = generator.create_try_except(
        "result = risky_operation()",
        "ValueError",
        "result = 'error'"
    )
    print(f"   - Try-except:\n{try_except}")
    
    print("\n✨ Complete pkg_resources Modernization Example:")
    
    # Show how to generate the complete modernized code
    new_import = generator.create_import("internal_pyharmony", ["get_package_version"])
    new_assignment = generator.create_assignment("__version__", "get_package_version(__name__)")
    
    modernized_code = f"{new_import}\n\n{new_assignment}"
    print(modernized_code)


def demonstrate_pattern_matching():
    """Demonstrate pattern matching capabilities."""
    
    print("\n" + "=" * 60)
    print("Pattern Matching Demonstration")
    print("=" * 60)
    
    # Complex code with multiple patterns
    complex_code = '''
import os
import sys
from pkg_resources import get_distribution, DistributionNotFound
import ConfigParser
import urllib2

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "unknown"

def old_function():
    config = ConfigParser.ConfigParser()
    response = urllib2.urlopen("http://example.com")
    return "Hello %s" % "world"

class OldClass:
    def method(self):
        return "old method"
'''
    
    print("\n📝 Complex Code Example:")
    print(complex_code)
    
    parser = pyrustor.Parser()
    ast = parser.parse_string(complex_code)
    
    print("\n🔍 Pattern Analysis:")
    
    # Find different patterns
    patterns = {
        "Legacy imports": ast.find_imports("ConfigParser") + ast.find_imports("urllib2"),
        "pkg_resources usage": ast.find_imports("pkg_resources"),
        "Version detection": ast.find_try_except_blocks("DistributionNotFound"),
        "Old-style functions": [f for f in ast.function_names() if f.startswith("old_")],
        "Old-style classes": [c for c in ast.class_names() if c.startswith("Old")],
    }
    
    for pattern_name, matches in patterns.items():
        if isinstance(matches, list) and matches and isinstance(matches[0], str):
            print(f"   - {pattern_name}: {len(matches)} found - {matches}")
        else:
            print(f"   - {pattern_name}: {len(matches)} found")
    
    print("\n🔧 Potential Modernizations:")
    print("   - Replace ConfigParser with configparser")
    print("   - Replace urllib2 with urllib.request")
    print("   - Modernize pkg_resources version detection")
    print("   - Rename old_function to modern_function")
    print("   - Rename OldClass to ModernClass")
    print("   - Modernize string formatting")


if __name__ == "__main__":
    demonstrate_bottom_level_api()
    demonstrate_code_generator()
    demonstrate_pattern_matching()
    
    print("\n" + "=" * 60)
    print("🎉 Bottom-Level API Demonstration Complete!")
    print("=" * 60)
    print("\n💡 Key Takeaways:")
    print("   - PyRustor provides powerful bottom-level APIs")
    print("   - Users can build custom modernization functions")
    print("   - Code generation makes creating new code easy")
    print("   - Pattern matching enables complex transformations")
    print("   - The API is composable and extensible")
    print("\n🚀 Ready to build your own code transformations!")
