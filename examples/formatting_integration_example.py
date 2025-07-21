#!/usr/bin/env python3
"""
Example demonstrating PyRustor's Ruff formatter integration.

This example shows how to use PyRustor's enhanced API that integrates
Ruff's formatter for high-quality code formatting during refactoring.
"""

import pyrustor


def main():
    """Demonstrate formatting integration features."""
    
    print("=== PyRustor + Ruff Formatter Integration Demo ===\n")
    
    # Example 1: Rename function with automatic formatting
    print("1. Rename Function with Formatting")
    print("-" * 40)
    
    messy_code = '''def   old_function(  x,y,z  ):
    result=x+y*z
    return result
        
def another_function():
    value=old_function(1,2,3)
    return value'''

    parser = pyrustor.Parser()
    ast = parser.parse_string(messy_code)
    refactor = pyrustor.Refactor(ast)
    
    print("Original messy code:")
    print(messy_code)
    
    # Rename with automatic formatting
    refactor.rename_function_with_format("old_function", "calculate_result", apply_formatting=True)
    formatted_result = refactor.to_string()
    
    print("\nAfter rename + formatting:")
    print(formatted_result)
    
    print("\nChanges applied:")
    for change in refactor.change_summary():
        print(f"  - {change}")
    
    # Example 2: Class renaming with formatting
    print("\n\n2. Class Renaming with Formatting")
    print("-" * 40)
    
    class_code = '''class   OldStyleClass:
    def __init__(self,name,age):
        self.name=name
        self.age=age
    def get_info(self):
        return f"{self.name} is {self.age} years old"
        
obj=OldStyleClass("John",25)
print(obj.get_info())'''

    ast2 = parser.parse_string(class_code)
    refactor2 = pyrustor.Refactor(ast2)
    
    print("Original code:")
    print(class_code)
    
    # Rename class with formatting
    refactor2.rename_class_with_format("OldStyleClass", "Person", apply_formatting=True)
    formatted_result2 = refactor2.to_string()
    
    print("\nAfter class rename + formatting:")
    print(formatted_result2)
    
    # Example 3: Multiple operations with final formatting
    print("\n\n3. Multiple Operations + Final Formatting")
    print("-" * 50)
    
    complex_code = '''import   ConfigParser
from   imp   import reload

class   DataProcessor:
    def __init__(self,config_file):
        self.config=ConfigParser.ConfigParser()
        self.config.read(config_file)
    def old_process_method(self,data):
        return "Processed: %s"%(data)
        
def old_helper_function():
    return DataProcessor("config.ini")'''

    ast3 = parser.parse_string(complex_code)
    refactor3 = pyrustor.Refactor(ast3)
    
    print("Original complex code:")
    print(complex_code)
    
    # Apply multiple refactoring operations
    refactor3.replace_import("ConfigParser", "configparser")
    refactor3.replace_import("imp", "importlib")
    refactor3.rename_class("DataProcessor", "ModernProcessor")
    refactor3.rename_function("old_helper_function", "create_processor")
    refactor3.modernize_syntax()
    
    # Get final result with formatting
    final_result = refactor3.refactor_and_format()
    
    print("\nAfter all refactoring + formatting:")
    print(final_result)
    
    print("\nAll changes applied:")
    for i, change in enumerate(refactor3.change_summary(), 1):
        print(f"  {i}. {change}")
    
    # Example 4: Convert production code to test code with formatting
    print("\n\n4. Production to Test Code Conversion")
    print("-" * 45)
    
    production_code = '''from __future__ import absolute_import
from rez_builder import PipFromDownloadBuilder

SOURCES={
    "downloads":[
        {
            "file_name":"shiboken6-6.5.0-cp37-abi3-win_amd64.whl",
            "checksum":{
                "sha256":"aee9708517821aaef547c83d689bf524d6f217d47232cb313d9af9e630215eed"
            },
        }
    ]
}

if __name__=="__main__":
    BUILDER=PipFromDownloadBuilder(SOURCES)
    BUILDER.build()'''

    ast4 = parser.parse_string(production_code)
    refactor4 = pyrustor.Refactor(ast4)
    
    print("Original production code:")
    print(production_code)
    
    # Convert to test-friendly version
    refactor4.convert_to_test_code()
    test_code = refactor4.refactor_and_format()
    
    print("\nTest-friendly version with formatting:")
    print(test_code)
    
    print("\nConversion changes:")
    for change in refactor4.change_summary():
        print(f"  - {change}")
    
    # Example 5: Conditional formatting
    print("\n\n5. Conditional Formatting Control")
    print("-" * 40)
    
    sample_code = '''def example(x,y):
    return x+y'''

    ast5 = parser.parse_string(sample_code)
    refactor5 = pyrustor.Refactor(ast5)
    
    print("Original code:")
    print(sample_code)
    
    # Rename without formatting
    refactor5.rename_function_with_format("example", "add_numbers", apply_formatting=False)
    result_no_format = refactor5.to_string()
    
    print("\nAfter rename (no formatting):")
    print(result_no_format)
    
    # Now apply formatting separately
    refactor5.format_code()
    result_with_format = refactor5.to_string()
    
    print("\nAfter applying formatting:")
    print(result_with_format)
    
    print("\nFinal changes:")
    for change in refactor5.change_summary():
        print(f"  - {change}")
    
    # Example 6: Using to_string_with_format
    print("\n\n6. Flexible Output with to_string_with_format")
    print("-" * 50)
    
    code = '''def   messy_function(  a,b,c  ):
    result=a+b*c
    return result'''

    ast6 = parser.parse_string(code)
    refactor6 = pyrustor.Refactor(ast6)
    
    print("Original code:")
    print(code)
    
    # Get output without formatting
    output_raw = refactor6.to_string_with_format(apply_formatting=False)
    print("\nOutput without formatting:")
    print(output_raw)
    
    # Get output with formatting
    output_formatted = refactor6.to_string_with_format(apply_formatting=True)
    print("\nOutput with formatting:")
    print(output_formatted)
    
    print("\nFormatting changes:")
    for change in refactor6.change_summary():
        print(f"  - {change}")


if __name__ == "__main__":
    main()
