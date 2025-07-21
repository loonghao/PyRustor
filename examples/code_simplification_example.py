#!/usr/bin/env python3
"""
Example demonstrating PyRustor's code simplification capabilities.

This example shows how to convert complex production code into simplified
test-friendly versions using PyRustor's enhanced API.
"""

import pyrustor


def main():
    """Demonstrate code simplification features."""
    
    # Example 1: Simplify a complex Rez build file
    print("=== Example 1: Rez Build File Simplification ===")
    
    complex_rez_code = '''#! /usr/bin/env python
"""Rez build file, must cd to this directory and run "rez build"."""

# Import future modules
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import third-party modules
from rez_builder import PipFromDownloadBuilder

# Downloaded from <INSERT URL HERE>
SOURCES = {
    "downloads": [
        {
            "file_name": u"shiboken6-6.5.0-cp37-abi3-win_amd64.whl",  # noqa: E501
            "checksum": {
                "sha256": u"aee9708517821aaef547c83d689bf524d6f217d47232cb313d9af9e630215eed"  # noqa: E501
            },
        }
    ]
}

if __name__ == "__main__":
    BUILDER = PipFromDownloadBuilder(SOURCES)
    BUILDER.build()
'''

    # Parse and simplify
    parser = pyrustor.Parser()
    ast = parser.parse_string(complex_rez_code)
    refactor = pyrustor.Refactor(ast)
    
    # Apply our enhanced simplification API
    refactor.convert_to_test_code()
    
    # Get beautifully formatted result
    simplified_code = refactor.refactor_and_format()
    
    print("Original code length:", len(complex_rez_code))
    print("Simplified code length:", len(simplified_code))
    print("\nChanges made:")
    for change in refactor.change_summary():
        print(f"  - {change}")
    
    print("\nSimplified code:")
    print(simplified_code)
    
    # Example 2: Simplify configuration with sensitive data
    print("\n=== Example 2: Configuration Simplification ===")
    
    production_config = '''
import os
from datetime import datetime

# Production database configuration
DATABASE_CONFIG = {
    "host": "prod-db-cluster.company.internal",
    "port": 5432,
    "database": "production_app",
    "username": "prod_user_2024",
    "password": os.environ.get("DB_PASSWORD", "fallback_secret_123"),
    "ssl_cert": "/etc/ssl/certs/prod-db-cert.pem",
    "connection_pool": {
        "min_connections": 10,
        "max_connections": 100,
        "timeout": 30
    }
}

# API configuration
API_CONFIG = {
    "base_url": "https://api.production.company.com/v2",
    "api_key": os.environ.get("API_KEY", "sk-prod-key-abcd1234"),
    "rate_limit": 1000,
    "timeout": 60,
    "retry_attempts": 3
}

def get_database_connection():
    """Get database connection using production config."""
    return connect_to_database(DATABASE_CONFIG)

def make_api_request(endpoint):
    """Make API request using production config."""
    return request(f"{API_CONFIG['base_url']}/{endpoint}")
'''

    # Parse and convert to test version
    ast2 = parser.parse_string(production_config)
    refactor2 = pyrustor.Refactor(ast2)
    
    # Use individual methods for fine-grained control
    refactor2.remove_unused_imports()
    refactor2.replace_complex_data_with_mocks()
    refactor2.replace_real_data_with_mocks()
    
    # Format the result
    test_friendly_code = refactor2.refactor_and_format()
    
    print("Changes made:")
    for change in refactor2.change_summary():
        print(f"  - {change}")
    
    print("\nTest-friendly version:")
    print(test_friendly_code)
    
    # Example 3: Demonstrate formatting integration
    print("\n=== Example 3: Formatting Integration ===")
    
    messy_code = '''import   os,sys,json
def   badly_formatted_function(  x,y,z  ):
    result=x+y*z
    return result
        
class   BadlyFormattedClass:
    def __init__(self,name,value):
        self.name=name
        self.value=value
    def process(self):
        return self.name+str(self.value)'''

    ast3 = parser.parse_string(messy_code)
    refactor3 = pyrustor.Refactor(ast3)
    
    # Just apply formatting
    refactor3.format_code()
    formatted_result = refactor3.to_string()
    
    print("Original messy code:")
    print(messy_code)
    print("\nFormatted code:")
    print(formatted_result)
    
    print("\nFormatting changes:")
    for change in refactor3.change_summary():
        print(f"  - {change}")


if __name__ == "__main__":
    main()
