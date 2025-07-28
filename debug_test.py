import pyrustor

# Test the large file content that's causing issues
large_content = '''
"""Large Python module for testing performance."""

import os
import sys
import json
import datetime
from typing import List, Dict, Optional
import ConfigParser
import urllib2

class TestClass0:
    """Test class number 0."""

    def __init__(self, value):
        self.value = value
        self.id = 0

    def method_0(self):
        """Method 0."""
        return "Result from method 0: %s" % self.value

def function_0():
    """Function number 0."""
    return "Function 0 result"

# Main execution
if __name__ == "__main__":
    for i in range(10):
        obj = TestClass0(f"value_{i}")
        print(obj.method_0())
'''

try:
    parser = pyrustor.Parser()
    ast = parser.parse_string(large_content)
    refactor = pyrustor.Refactor(ast)

    print("Parsing successful!")
    print(f"Statement count: {ast.statement_count()}")

    # Try to get the code back
    result = refactor.get_code()
    print("Code generation successful!")
    print(f"Generated code length: {len(result)}")

except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}")
