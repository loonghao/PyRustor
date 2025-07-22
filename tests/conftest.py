"""
Pytest configuration and fixtures for PyRustor tests.

This module provides common fixtures and configuration for all test modules.
"""

import pytest
import tempfile
import os
from pathlib import Path
import pyrustor


@pytest.fixture
def parser():
    """Provide a fresh Parser instance for each test."""
    return pyrustor.Parser()


@pytest.fixture
def sample_function_code():
    """Sample Python code with a function for testing."""
    return """
def hello_world(name="World"):
    '''Say hello to someone.'''
    message = f"Hello, {name}!"
    return message

def calculate_sum(a, b):
    '''Calculate the sum of two numbers.'''
    return a + b
"""


@pytest.fixture
def sample_class_code():
    """Sample Python code with classes for testing."""
    return """
class Person:
    '''A simple person class.'''
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name} and I'm {self.age} years old."
    
    def have_birthday(self):
        self.age += 1

class Employee(Person):
    '''An employee class that inherits from Person.'''
    
    def __init__(self, name, age, job_title):
        super().__init__(name, age)
        self.job_title = job_title
    
    def work(self):
        return f"{self.name} is working as a {self.job_title}."
"""


@pytest.fixture
def sample_import_code():
    """Sample Python code with various import statements."""
    return """
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import ConfigParser
from imp import reload
import urllib2
from collections import OrderedDict
"""


@pytest.fixture
def complex_code_sample():
    """Complex Python code sample for comprehensive testing."""
    return """
import ConfigParser
import urllib2
from imp import reload

class DataProcessor:
    '''Process data using legacy methods.'''
    
    def __init__(self, config_file):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        self.data = []
    
    def fetch_data(self, url):
        '''Fetch data from a URL using urllib2.'''
        response = urllib2.urlopen(url)
        return response.read()
    
    def process_data(self, raw_data):
        '''Process raw data.'''
        # Old-style string formatting
        message = "Processing %d bytes of data" % len(raw_data)
        print(message)
        return raw_data.decode('utf-8')
    
    def reload_config(self):
        '''Reload configuration.'''
        reload(ConfigParser)

def legacy_function(items):
    '''Legacy function using old patterns.'''
    result = []
    for item in items:
        if item is not None:
            result.append(str(item))
    return result

def another_legacy_function():
    '''Another legacy function.'''
    data = legacy_function([1, 2, 3, None, 4])
    return "Items: %s" % ", ".join(data)
"""


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing file operations."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def temp_function():
    '''A temporary function for testing.'''
    return "Hello from temp file"

class TempClass:
    '''A temporary class for testing.'''
    pass
""")
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "data"


# Pytest markers for organizing tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "parser: mark test as parser-related"
    )
    config.addinivalue_line(
        "markers", "refactor: mark test as refactor-related"
    )
    config.addinivalue_line(
        "markers", "error_handling: mark test as error handling test"
    )
    config.addinivalue_line(
        "markers", "edge_case: mark test as edge case test"
    )


# Custom assertions for better test readability
class PyRustorAssertions:
    """Custom assertions for PyRustor testing."""
    
    @staticmethod
    def assert_function_renamed(refactor, old_name, new_name):
        """Assert that a function was successfully renamed."""
        code = refactor.get_code()
        assert old_name not in code or f"def {old_name}" not in code
        assert f"def {new_name}" in code
    
    @staticmethod
    def assert_class_renamed(refactor, old_name, new_name):
        """Assert that a class was successfully renamed."""
        code = refactor.get_code()
        assert old_name not in code or f"class {old_name}" not in code
        assert f"class {new_name}" in code
    
    @staticmethod
    def assert_import_replaced(refactor, old_import, new_import):
        """Assert that an import was successfully replaced."""
        code = refactor.get_code()
        # Note: This is a simplified check - full implementation would be more sophisticated
        assert old_import not in code or new_import in code
    
    @staticmethod
    def assert_changes_recorded(refactor, expected_count=None):
        """Assert that changes were properly recorded."""
        summary = refactor.change_summary()
        if expected_count is not None:
            assert f"{expected_count} changes" in summary
        else:
            assert "No changes made" not in summary


@pytest.fixture
def assertions():
    """Provide custom assertions for tests."""
    return PyRustorAssertions()


# Performance testing helpers
@pytest.fixture
def performance_timer():
    """Simple performance timer for benchmarking."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self):
            if self.start_time is None or self.end_time is None:
                return None
            return self.end_time - self.start_time
    
    return Timer()
