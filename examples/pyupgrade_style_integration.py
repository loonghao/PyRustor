#!/usr/bin/env python3
"""
Example demonstrating how PyRustor can be used to build pyupgrade-style tools.

This example shows how PyRustor's clean API design makes it easy to build
tools similar to pyupgrade that modernize Python code automatically.
"""

import pyrustor


def modernize_python_code(source_code: str, target_version: str = "3.8") -> str:
    """
    Modernize Python code similar to pyupgrade.
    
    This function demonstrates how PyRustor can be used as a foundation
    for building tools like pyupgrade.
    """
    parser = pyrustor.Parser()
    ast = parser.parse_string(source_code)
    refactor = pyrustor.Refactor(ast)
    
    # Apply modernization transformations
    modernize_imports(refactor)
    modernize_syntax_patterns(refactor)
    
    # Return formatted result
    return refactor.refactor_and_format()


def modernize_imports(refactor: pyrustor.Refactor) -> None:
    """Apply import modernizations."""
    # Common import modernizations
    import_mappings = {
        "ConfigParser": "configparser",
        "imp": "importlib", 
        "urllib2": "urllib.request",
        "urlparse": "urllib.parse",
        "BaseHTTPServer": "http.server",
        "SimpleHTTPServer": "http.server",
        "CGIHTTPServer": "http.server",
        "cookielib": "http.cookiejar",
        "Queue": "queue",
        "SocketServer": "socketserver",
        "repr": "reprlib",
        "FileDialog": "tkinter.filedialog",
        "tkSimpleDialog": "tkinter.simpledialog",
        "tkColorChooser": "tkinter.colorchooser",
        "tkCommonDialog": "tkinter.commondialog",
        "tkMessageBox": "tkinter.messagebox",
        "Tkinter": "tkinter",
    }
    
    for old_import, new_import in import_mappings.items():
        refactor.replace_import(old_import, new_import)


def modernize_syntax_patterns(refactor: pyrustor.Refactor) -> None:
    """Apply syntax modernizations."""
    # This would use PyRustor's modernize_syntax method
    # which handles things like:
    # - % formatting -> .format() -> f-strings
    # - old-style classes -> new-style classes
    # - deprecated syntax patterns
    refactor.modernize_syntax()


def main():
    """Demonstrate pyupgrade-style modernization."""
    
    print("=== PyRustor: Building pyupgrade-style Tools ===\n")
    
    # Example 1: Legacy Python 2/3 compatibility code
    print("1. Modernizing Legacy Python 2/3 Code")
    print("-" * 45)
    
    legacy_code = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ConfigParser
import urllib2
from Queue import Queue

class OldStyleClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def get_info(self):
        return "Name: %s, Age: %d" % (self.name, self.age)

def fetch_data(url):
    response = urllib2.urlopen(url)
    return response.read()

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    queue = Queue()
    obj = OldStyleClass("John", 25)
    print(obj.get_info())'''

    print("Original legacy code:")
    print(legacy_code)
    
    modernized = modernize_python_code(legacy_code, target_version="3.8")
    
    print("\nModernized code:")
    print(modernized)
    
    # Example 2: Building a custom modernization tool
    print("\n\n2. Custom Modernization Tool")
    print("-" * 35)
    
    def custom_modernizer(source_code: str) -> str:
        """Custom modernization with specific rules."""
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        refactor = pyrustor.Refactor(ast)
        
        # Apply specific modernizations with formatting
        refactor.replace_import("requests", "httpx")  # Example: migrate to httpx
        refactor.rename_function_with_format("old_api_call", "new_api_call", apply_formatting=True)
        refactor.modernize_syntax_with_format(apply_formatting=True)
        
        return refactor.to_string()
    
    custom_code = '''import requests

def old_api_call(url, data):
    response = requests.post(url, json=data)
    return response.json()

def process_data():
    result = old_api_call("https://api.example.com", {"key": "value"})
    return "Result: %s" % result'''

    print("Code to modernize:")
    print(custom_code)
    
    custom_result = custom_modernizer(custom_code)
    
    print("\nCustom modernized result:")
    print(custom_result)
    
    # Example 3: Incremental modernization
    print("\n\n3. Incremental Modernization")
    print("-" * 35)
    
    def incremental_modernize(source_code: str, steps: list) -> str:
        """Apply modernization steps incrementally."""
        parser = pyrustor.Parser()
        ast = parser.parse_string(source_code)
        refactor = pyrustor.Refactor(ast)
        
        for step in steps:
            if step == "imports":
                modernize_imports(refactor)
            elif step == "syntax":
                refactor.modernize_syntax()
            elif step == "format":
                refactor.format_code()
        
        return refactor.to_string()
    
    incremental_code = '''import ConfigParser
def format_string(name, age):
    return "Name: %s, Age: %d" % (name, age)'''

    print("Original code:")
    print(incremental_code)
    
    # Apply steps incrementally
    steps = ["imports", "syntax", "format"]
    incremental_result = incremental_modernize(incremental_code, steps)
    
    print(f"\nAfter applying steps {steps}:")
    print(incremental_result)
    
    # Example 4: Integration with existing tools
    print("\n\n4. Integration Pattern for Tool Builders")
    print("-" * 45)
    
    class PyUpgradeStyleTool:
        """Example tool class showing integration pattern."""
        
        def __init__(self, target_version: str = "3.8"):
            self.target_version = target_version
            self.parser = pyrustor.Parser()
        
        def process_file(self, file_path: str) -> str:
            """Process a single file."""
            ast = self.parser.parse_file(file_path)
            refactor = pyrustor.Refactor(ast)
            
            # Apply transformations based on target version
            if self.target_version >= "3.6":
                refactor.modernize_syntax()  # Includes f-string conversion
            
            modernize_imports(refactor)
            
            return refactor.refactor_and_format()
        
        def process_string(self, source_code: str) -> tuple[str, list[str]]:
            """Process source code string and return result + changes."""
            ast = self.parser.parse_string(source_code)
            refactor = pyrustor.Refactor(ast)
            
            modernize_imports(refactor)
            refactor.modernize_syntax()
            
            result = refactor.refactor_and_format()
            changes = refactor.change_summary()
            
            return result, changes
    
    # Demonstrate the tool
    tool = PyUpgradeStyleTool(target_version="3.8")
    
    sample_code = '''import urllib2
def greet(name):
    return "Hello, %s!" % name'''

    print("Sample code:")
    print(sample_code)
    
    result, changes = tool.process_string(sample_code)
    
    print("\nProcessed result:")
    print(result)
    
    print("\nChanges applied:")
    for i, change in enumerate(changes, 1):
        print(f"  {i}. {change}")
    
    print("\n" + "="*60)
    print("PyRustor provides a clean, extensible foundation for building")
    print("Python modernization tools like pyupgrade, with built-in")
    print("Ruff formatter integration for high-quality output!")


if __name__ == "__main__":
    main()
