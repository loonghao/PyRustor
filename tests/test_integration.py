"""Integration tests for PyRustor"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


@pytest.mark.integration
class TestIntegration:
    """Integration test cases"""

    def test_end_to_end_refactoring_workflow(self):
        """Test complete end-to-end refactoring workflow"""
        parser = pyrustor.Parser()
        
        # Complex source code with multiple refactoring opportunities
        source = """
#!/usr/bin/env python3
\"\"\"
Legacy Python module that needs modernization
\"\"\"

import ConfigParser
import optparse
from pkg_resources import get_distribution, DistributionNotFound
from imp import reload
import StringIO
import urllib2

# Version detection using old pkg_resources pattern
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"

class OldConfigManager:
    \"\"\"Old-style configuration manager\"\"\"
    
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.parser = optparse.OptionParser()
    
    def old_load_config(self, filename):
        \"\"\"Load configuration from file\"\"\"
        self.config.read(filename)
        return self.config
    
    def old_parse_args(self, args):
        \"\"\"Parse command line arguments\"\"\"
        return self.parser.parse_args(args)

def old_network_function():
    \"\"\"Old network function using urllib2\"\"\"
    try:
        response = urllib2.urlopen("http://example.com")
        return response.read()
    except urllib2.URLError:
        return None

def old_string_function():
    \"\"\"Old string handling function\"\"\"
    buffer = StringIO.StringIO()
    buffer.write("Hello, World!")
    return buffer.getvalue()

def old_reload_function(module):
    \"\"\"Old module reloading function\"\"\"
    reload(module)
    return True

def main():
    \"\"\"Main function\"\"\"
    manager = OldConfigManager()
    config = manager.old_load_config("config.ini")
    
    data = old_network_function()
    text = old_string_function()
    
    print(f"Version: {__version__}")
    print(f"Data length: {len(data) if data else 0}")
    print(f"Text: {text}")

if __name__ == "__main__":
    main()
"""
        
        # Parse the source
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply comprehensive refactoring
        # 1. Modernize imports
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("optparse", "argparse")
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        refactor.replace_import("imp", "importlib")
        refactor.replace_import("StringIO", "io")
        refactor.replace_import("urllib2", "urllib.request")
        
        # 2. Rename classes and functions (only top-level functions for now)
        refactor.rename_class("OldConfigManager", "ModernConfigManager")
        refactor.rename_function("old_network_function", "fetch_data")
        refactor.rename_function("old_string_function", "create_string")
        refactor.rename_function("old_reload_function", "reload_module")
        refactor.rename_function("main", "main_function")
        
        # 3. Apply syntax modernization
        refactor.modernize_syntax()
        
        # Verify the refactoring was applied
        summary = refactor.change_summary()
        assert "changes" in summary
        
        # Get the refactored code
        result = refactor.get_code()
        assert result is not None
        assert len(result) > 0

    def test_file_based_refactoring(self):
        """Test refactoring operations on actual files"""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
from pkg_resources import get_distribution, DistributionNotFound
import ConfigParser

class OldProcessor:
    def old_method(self):
        config = ConfigParser.ConfigParser()
        try:
            version = get_distribution(__name__).version
        except DistributionNotFound:
            version = "unknown"
        return version

def old_function():
    processor = OldProcessor()
    return processor.old_method()
""")
            temp_file = f.name
        
        try:
            # Parse the file
            parser = pyrustor.Parser()
            ast = parser.parse_file(temp_file)
            
            # Apply refactoring
            refactor = pyrustor.Refactor(ast)
            refactor.replace_import("pkg_resources", "xxx_pyharmony")
            refactor.replace_import("ConfigParser", "configparser")
            refactor.rename_class("OldProcessor", "NewProcessor")
            refactor.rename_function("old_function", "new_function")
            
            # Save the refactored code to a new file
            output_file = temp_file.replace('.py', '_refactored.py')
            refactor.save_to_file(output_file)
            
            # Verify the output file exists and has content
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                content = f.read()
                assert len(content) > 0
            
            # Clean up
            os.unlink(output_file)
            
        finally:
            os.unlink(temp_file)

    def test_directory_refactoring(self):
        """Test refactoring multiple files in a directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple Python files
            files_content = {
                "module1.py": """
from pkg_resources import get_distribution
class OldClass1:
    def old_method1(self):
        return get_distribution(__name__).version
""",
                "module2.py": """
import ConfigParser
def old_function2():
    config = ConfigParser.ConfigParser()
    return config
""",
                "module3.py": """
from imp import reload
class OldClass3:
    def old_method3(self, module):
        reload(module)
        return True
"""
            }
            
            # Write files
            for filename, content in files_content.items():
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write(content)
            
            # Parse all files
            parser = pyrustor.Parser()
            results = parser.parse_directory(temp_dir, recursive=False)
            
            assert len(results) == 3
            
            # Apply refactoring to each file
            for filepath, ast in results:
                refactor = pyrustor.Refactor(ast)
                
                # Apply common refactoring patterns
                refactor.replace_import("pkg_resources", "xxx_pyharmony")
                refactor.replace_import("ConfigParser", "configparser")
                refactor.replace_import("imp", "importlib")
                
                # Apply renaming based on file
                if "module1" in filepath:
                    refactor.rename_class("OldClass1", "NewClass1")
                    # Skip method renaming for now
                elif "module2" in filepath:
                    refactor.rename_function("old_function2", "new_function2")
                elif "module3" in filepath:
                    refactor.rename_class("OldClass3", "NewClass3")
                    # Skip method renaming for now
                
                # Verify changes were applied
                summary = refactor.change_summary()
                assert len(summary) > 0

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery in refactoring operations"""
        parser = pyrustor.Parser()
        
        # Test with valid code
        valid_source = """
def valid_function():
    return "valid"

class ValidClass:
    pass
"""
        ast = parser.parse_string(valid_source)
        refactor = pyrustor.Refactor(ast)
        
        # Valid operations should succeed
        refactor.rename_function("valid_function", "renamed_function")
        refactor.rename_class("ValidClass", "RenamedClass")
        
        # Invalid operations should raise errors
        with pytest.raises(ValueError):
            refactor.rename_function("nonexistent_function", "new_name")
        
        with pytest.raises(ValueError):
            refactor.rename_class("NonexistentClass", "NewClass")
        
        # Previous valid changes should still be recorded
        summary = refactor.change_summary()
        assert "2 changes" in summary

    def test_performance_with_large_code(self):
        """Test performance with larger code files"""
        # Generate a larger Python file
        large_source = """
# Large Python module for performance testing
import os
import sys
from pkg_resources import get_distribution, DistributionNotFound

"""
        
        # Add many functions and classes
        for i in range(50):
            large_source += f"""
def old_function_{i}():
    \"\"\"Function number {i}\"\"\"
    try:
        version = get_distribution("package_{i}").version
    except DistributionNotFound:
        version = "unknown"
    return f"Function {i}: {{version}}"

class OldClass_{i}:
    \"\"\"Class number {i}\"\"\"
    
    def old_method_{i}(self):
        return old_function_{i}()
    
    def another_method_{i}(self):
        return f"Method {i}"
"""
        
        # Parse and refactor
        parser = pyrustor.Parser()
        ast = parser.parse_string(large_source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply refactoring operations
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Rename some functions and classes
        for i in range(0, 10):  # Only rename first 10 to keep test reasonable
            refactor.rename_function(f"old_function_{i}", f"new_function_{i}")
            refactor.rename_class(f"OldClass_{i}", f"NewClass_{i}")
        
        # Verify operations completed
        summary = refactor.change_summary()
        assert "changes" in summary
        
        result = refactor.get_code()
        assert result is not None
        assert len(result) > len(large_source) * 0.8  # Should be roughly same size

    def test_ast_information_extraction(self):
        """Test extracting comprehensive information from AST"""
        parser = pyrustor.Parser()
        source = """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

class DataProcessor:
    def __init__(self):
        pass
    
    def process_data(self, data: List[str]) -> Dict[str, int]:
        return {}
    
    def save_results(self, results: Dict[str, int]) -> None:
        pass

class FileManager:
    def read_file(self, path: Path) -> str:
        return ""
    
    def write_file(self, path: Path, content: str) -> None:
        pass

def main_function():
    processor = DataProcessor()
    manager = FileManager()
    return True

def helper_function(x: int, y: int) -> int:
    return x + y

def another_helper() -> None:
    pass
"""
        
        ast = parser.parse_string(source)
        
        # Test AST information extraction
        assert not ast.is_empty()
        assert ast.statement_count() > 5
        
        # Test function extraction
        functions = ast.function_names()
        expected_functions = ["main_function", "helper_function", "another_helper"]
        for func in expected_functions:
            assert func in functions
        
        # Test class extraction
        classes = ast.class_names()
        expected_classes = ["DataProcessor", "FileManager"]
        for cls in expected_classes:
            assert cls in classes
        
        # Test import extraction
        imports = ast.imports()
        assert len(imports) >= 4  # Should have multiple imports
        
        # Test round-trip conversion
        result = ast.to_string()
        assert result is not None
        assert "DataProcessor" in result
        assert "FileManager" in result
        assert "main_function" in result
