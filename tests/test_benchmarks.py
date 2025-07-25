"""Benchmark tests for PyRustor performance"""

import pytest
import time
import psutil
import os
import pyrustor


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark test cases"""

    def test_parsing_performance(self, benchmark):
        """Benchmark parsing performance"""
        # Generate a moderately complex Python file
        source = """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Union
from pkg_resources import get_distribution, DistributionNotFound

class ComplexClass:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self._cache = {}
    
    def method1(self, data: List[str]) -> Dict[str, int]:
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
        return len(item) * 42

def function1():
    return "test"

def function2(x: int, y: int) -> int:
    return x + y

def function3(data: List[str]) -> None:
    for item in data:
        print(item)
"""
        
        def parse_code():
            parser = pyrustor.Parser()
            return parser.parse_string(source)
        
        result = benchmark(parse_code)
        assert result is not None
        assert not result.is_empty()

    def test_refactoring_performance(self, benchmark):
        """Benchmark refactoring performance"""
        parser = pyrustor.Parser()
        source = """
from pkg_resources import get_distribution, DistributionNotFound
import ConfigParser

class OldClass:
    def old_method1(self):
        config = ConfigParser.ConfigParser()
        return config
    
    def old_method2(self):
        try:
            version = get_distribution(__name__).version
        except DistributionNotFound:
            version = "unknown"
        return version

def old_function1():
    return "test"

def old_function2():
    return OldClass()
"""
        ast = parser.parse_string(source)
        
        def apply_refactoring():
            refactor = pyrustor.Refactor(ast)
            refactor.replace_import("pkg_resources", "xxx_pyharmony")
            refactor.replace_import("ConfigParser", "configparser")
            refactor.rename_class("OldClass", "NewClass")
            # Skip method renaming for now - only rename top-level functions
            refactor.rename_function("old_function1", "new_function1")
            refactor.rename_function("old_function2", "new_function2")
            return refactor
        
        result = benchmark(apply_refactoring)
        assert result is not None
        summary = result.change_summary()
        assert "changes" in summary

    def test_large_file_parsing(self, benchmark):
        """Benchmark parsing of large files"""
        # Generate a large Python file
        large_source = "# Large Python file for benchmarking\n"
        large_source += "import os\nimport sys\n"
        large_source += "from pkg_resources import get_distribution, DistributionNotFound\n\n"
        
        # Add many functions
        for i in range(100):
            large_source += f"""
def function_{i}(param1, param2={i}):
    \"\"\"Function number {i}\"\"\"
    try:
        result = get_distribution("package_{i}").version
    except DistributionNotFound:
        result = "unknown"
    return f"Function {i}: {{result}}"
"""
        
        # Add many classes
        for i in range(50):
            large_source += f"""
class Class_{i}:
    \"\"\"Class number {i}\"\"\"
    
    def __init__(self):
        self.value = {i}
    
    def method_{i}(self):
        return function_{i}("test", {i})
    
    def another_method_{i}(self):
        return self.value * 2
"""
        
        def parse_large_file():
            parser = pyrustor.Parser()
            return parser.parse_string(large_source)
        
        result = benchmark(parse_large_file)
        assert result is not None
        assert not result.is_empty()
        assert result.statement_count() > 100

    def test_memory_usage_parsing(self):
        """Test memory usage during parsing"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate a large source file
        large_source = "import os\nimport sys\n"
        for i in range(1000):
            large_source += f"def func_{i}(): return {i}\n"
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(large_source)
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100 * 1024 * 1024
        assert ast is not None
        assert not ast.is_empty()

    def test_memory_usage_refactoring(self):
        """Test memory usage during refactoring"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create a complex source file
        source = """
from pkg_resources import get_distribution, DistributionNotFound
import ConfigParser
"""
        
        for i in range(200):
            source += f"""
class OldClass_{i}:
    def old_method_{i}(self):
        config = ConfigParser.ConfigParser()
        try:
            version = get_distribution("package_{i}").version
        except DistributionNotFound:
            version = "unknown"
        return version

def old_function_{i}():
    return OldClass_{i}()
"""
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply many refactoring operations
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        refactor.replace_import("ConfigParser", "configparser")
        
        for i in range(50):  # Only refactor first 50 to keep test reasonable
            refactor.rename_class(f"OldClass_{i}", f"NewClass_{i}")
            # Skip method renaming for now - only rename top-level functions
            refactor.rename_function(f"old_function_{i}", f"new_function_{i}")
        
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 200 * 1024 * 1024
        
        summary = refactor.change_summary()
        assert "changes" in summary

    def test_concurrent_parsing(self, benchmark):
        """Test parsing performance with multiple parsers"""
        sources = []
        for i in range(10):
            source = f"""
import module_{i}
from pkg_resources import get_distribution

class TestClass_{i}:
    def method_{i}(self):
        return get_distribution("package_{i}").version

def function_{i}():
    return TestClass_{i}()
"""
            sources.append(source)
        
        def parse_multiple():
            results = []
            for source in sources:
                parser = pyrustor.Parser()
                ast = parser.parse_string(source)
                results.append(ast)
            return results
        
        results = benchmark(parse_multiple)
        assert len(results) == 10
        for ast in results:
            assert ast is not None
            assert not ast.is_empty()

    def test_ast_information_extraction_performance(self, benchmark):
        """Benchmark AST information extraction"""
        # Create a complex AST
        source = """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
"""
        
        for i in range(100):
            source += f"""
class Class_{i}:
    def method_{i}_a(self):
        return {i}
    
    def method_{i}_b(self):
        return {i} * 2

def function_{i}_a():
    return Class_{i}()

def function_{i}_b():
    return "test_{i}"
"""
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source)
        
        def extract_info():
            functions = ast.function_names()
            classes = ast.class_names()
            imports = ast.imports()
            count = ast.statement_count()
            return len(functions), len(classes), len(imports), count
        
        result = benchmark(extract_info)
        func_count, class_count, import_count, stmt_count = result
        
        assert func_count >= 200  # Should have many functions
        assert class_count >= 100  # Should have many classes
        assert import_count >= 4   # Should have imports
        assert stmt_count > 300    # Should have many statements

    @pytest.mark.skip(reason="Code generation for try/except statements not yet implemented")
    def test_string_conversion_performance(self, benchmark):
        """Benchmark AST to string conversion"""
        # Create a moderately complex AST
        source = """
from pkg_resources import get_distribution, DistributionNotFound
import ConfigParser
import os
import sys

class ComplexClass:
    def __init__(self, config):
        self.config = config
    
    def process_data(self, data):
        results = []
        for item in data:
            processed = self._process_item(item)
            results.append(processed)
        return results
    
    def _process_item(self, item):
        try:
            version = get_distribution(item).version
        except DistributionNotFound:
            version = "unknown"
        return f"{item}: {version}"

def main():
    config = ConfigParser.ConfigParser()
    processor = ComplexClass(config)
    data = ["package1", "package2", "package3"]
    results = processor.process_data(data)
    return results

if __name__ == "__main__":
    main()
"""
        
        parser = pyrustor.Parser()
        ast = parser.parse_string(source)
        
        def convert_to_string():
            return ast.to_string()
        
        result = benchmark(convert_to_string)
        assert result is not None
        assert len(result) > 0
        assert "ComplexClass" in result
        assert "main" in result
