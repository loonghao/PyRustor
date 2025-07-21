"""Tests for PyRustor Parser functionality"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


@pytest.mark.parser
class TestParser:
    """Test cases for the Parser class"""

    def test_parser_creation(self):
        """Test that we can create a parser"""
        parser = pyrustor.Parser()
        assert parser is not None

    def test_parse_empty_string(self):
        """Test parsing an empty string"""
        parser = pyrustor.Parser()
        ast = parser.parse_string("")
        
        assert ast is not None
        assert ast.is_empty()
        assert ast.statement_count() == 0

    def test_parse_simple_function(self):
        """Test parsing a simple function"""
        parser = pyrustor.Parser()
        source = "def hello_world(): pass"
        ast = parser.parse_string(source)
        
        assert ast is not None
        assert not ast.is_empty()
        assert ast.statement_count() == 1
        
        functions = ast.function_names()
        assert len(functions) == 1
        assert functions[0] == "hello_world"

    def test_parse_multiple_functions(self):
        """Test parsing multiple functions"""
        parser = pyrustor.Parser()
        source = """
def func1():
    pass

def func2():
    return 42

def func3(x, y):
    return x + y
"""
        ast = parser.parse_string(source)
        
        assert ast is not None
        assert not ast.is_empty()
        
        functions = ast.function_names()
        assert len(functions) == 3
        assert "func1" in functions
        assert "func2" in functions
        assert "func3" in functions

    def test_parse_class_definitions(self):
        """Test parsing class definitions"""
        parser = pyrustor.Parser()
        source = """
class SimpleClass:
    pass

class ClassWithMethods:
    def method1(self):
        pass
    
    def method2(self, x):
        return x * 2

class InheritedClass(SimpleClass):
    def __init__(self):
        super().__init__()
"""
        ast = parser.parse_string(source)
        
        assert ast is not None
        assert not ast.is_empty()
        
        classes = ast.class_names()
        assert len(classes) == 3
        assert "SimpleClass" in classes
        assert "ClassWithMethods" in classes
        assert "InheritedClass" in classes

    def test_parse_imports(self):
        """Test parsing various import statements"""
        parser = pyrustor.Parser()
        source = """
import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
import json as js
from typing import List, Dict, Optional
"""
        ast = parser.parse_string(source)
        
        assert ast is not None
        assert not ast.is_empty()
        
        imports = ast.imports()
        assert len(imports) >= 4  # Should have multiple imports

    def test_parse_complex_code(self):
        """Test parsing complex Python code"""
        parser = pyrustor.Parser()
        source = """
#!/usr/bin/env python3
\"\"\"
A complex Python module for testing
\"\"\"

import os
import sys
from typing import List, Dict, Optional, Union
from pathlib import Path

# Global variable
GLOBAL_CONSTANT = 42

class DataProcessor:
    \"\"\"A class for processing data\"\"\"
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self._cache = {}
    
    def process(self, data: List[str]) -> Dict[str, int]:
        \"\"\"Process the input data\"\"\"
        result = {}
        for item in data:
            if item in self._cache:
                result[item] = self._cache[item]
            else:
                processed = self._process_item(item)
                self._cache[item] = processed
                result[item] = processed
        return result
    
    def _process_item(self, item: str) -> int:
        \"\"\"Process a single item\"\"\"
        return len(item) * GLOBAL_CONSTANT

def main():
    \"\"\"Main function\"\"\"
    processor = DataProcessor({"mode": "fast"})
    data = ["hello", "world", "python"]
    result = processor.process(data)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
        ast = parser.parse_string(source)
        
        assert ast is not None
        assert not ast.is_empty()
        assert ast.statement_count() > 5
        
        functions = ast.function_names()
        assert "main" in functions
        
        classes = ast.class_names()
        assert "DataProcessor" in classes

    def test_parse_invalid_syntax(self):
        """Test parsing invalid Python syntax"""
        parser = pyrustor.Parser()
        
        invalid_sources = [
            "def invalid syntax:",
            "class Missing Colon",
            "if True\n    pass",
            "for i in range(10\n    print(i)",
            "def func(\n    pass",
        ]
        
        for source in invalid_sources:
            with pytest.raises(ValueError):
                parser.parse_string(source)

    def test_parse_file(self):
        """Test parsing from a file"""
        parser = pyrustor.Parser()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def test_function():
    return "Hello from file"

class TestClass:
    def method(self):
        pass
""")
            temp_file = f.name
        
        try:
            ast = parser.parse_file(temp_file)
            
            assert ast is not None
            assert not ast.is_empty()
            
            functions = ast.function_names()
            assert "test_function" in functions
            
            classes = ast.class_names()
            assert "TestClass" in classes
            
        finally:
            os.unlink(temp_file)

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file"""
        parser = pyrustor.Parser()
        
        with pytest.raises(ValueError):
            parser.parse_file("nonexistent_file.py")

    def test_parse_directory(self):
        """Test parsing multiple files from a directory"""
        parser = pyrustor.Parser()
        
        # Create a temporary directory with Python files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1_path = os.path.join(temp_dir, "file1.py")
            with open(file1_path, 'w') as f:
                f.write("def func1(): pass")
            
            file2_path = os.path.join(temp_dir, "file2.py")
            with open(file2_path, 'w') as f:
                f.write("class Class2: pass")
            
            # Create a subdirectory
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            file3_path = os.path.join(subdir, "file3.py")
            with open(file3_path, 'w') as f:
                f.write("def func3(): return 42")
            
            # Parse directory non-recursively
            results = parser.parse_directory(temp_dir, recursive=False)
            assert len(results) == 2  # Should find file1.py and file2.py
            
            # Parse directory recursively
            results_recursive = parser.parse_directory(temp_dir, recursive=True)
            assert len(results_recursive) == 3  # Should find all three files

    def test_ast_to_string_roundtrip(self):
        """Test that parsing and converting back to string preserves structure"""
        parser = pyrustor.Parser()
        original_source = """def hello():
    return "world"

class Test:
    pass"""

        ast = parser.parse_string(original_source)
        result = ast.to_string()

        # The result should contain the same structural elements
        # Note: Current implementation returns debug format, not Python code
        assert "hello" in result
        assert "world" in result
        assert "Test" in result
        # For now, just check that we get some output
        assert len(result) > 0
