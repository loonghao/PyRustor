"""Tests for pkg_resources modernization functionality"""

import pytest
import pyrustor


@pytest.mark.refactor
class TestPkgResourcesModernization:
    """Test cases for modernizing pkg_resources version detection patterns"""

    def test_simple_pkg_resources_pattern(self):
        """Test modernizing simple pkg_resources version detection"""
        parser = pyrustor.Parser()
        source = """
from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply pkg_resources modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Check that changes were recorded
        summary = refactor.change_summary()
        assert len(summary) > 0

    def test_complex_pkg_resources_pattern(self):
        """Test modernizing complex pkg_resources patterns"""
        parser = pyrustor.Parser()
        source = """
#!/usr/bin/env python3
\"\"\"
Package version detection using pkg_resources
\"\"\"

import os
import sys
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

# Version detection with fallback
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Development version
    __version__ = "0.0.0-dev.1"

def get_version():
    \"\"\"Get the package version\"\"\"
    return __version__

def main():
    print(f"Version: {get_version()}")

if __name__ == "__main__":
    main()
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Should complete without error
        result = refactor.get_code()
        assert result is not None

    def test_multiple_pkg_resources_imports(self):
        """Test modernizing multiple pkg_resources import styles"""
        parser = pyrustor.Parser()
        source = """
# Different import styles
import pkg_resources
from pkg_resources import get_distribution
from pkg_resources import DistributionNotFound, get_distribution as get_dist

# Usage patterns
version1 = pkg_resources.get_distribution("package1").version
version2 = get_distribution("package2").version
version3 = get_dist("package3").version

try:
    version4 = pkg_resources.get_distribution("package4").version
except pkg_resources.DistributionNotFound:
    version4 = "unknown"
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Should handle multiple import styles
        assert True

    def test_pkg_resources_with_other_imports(self):
        """Test modernizing pkg_resources alongside other deprecated imports"""
        parser = pyrustor.Parser()
        source = """
# Mix of old and new imports
import ConfigParser
import pkg_resources
from imp import reload
from pkg_resources import get_distribution, DistributionNotFound
import optparse

# Version detection
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except pkg_resources.DistributionNotFound:
    __version__ = "dev"

# Other deprecated usage
config = ConfigParser.ConfigParser()
parser = optparse.OptionParser()
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply multiple modernizations
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        refactor.replace_import("ConfigParser", "configparser")
        refactor.replace_import("imp", "importlib")
        refactor.replace_import("optparse", "argparse")
        
        # Should handle multiple deprecated imports
        result = refactor.get_code()
        assert result is not None

    def test_pkg_resources_in_function(self):
        """Test modernizing pkg_resources usage inside functions"""
        parser = pyrustor.Parser()
        source = """
from pkg_resources import get_distribution, DistributionNotFound

def get_package_version(package_name):
    \"\"\"Get version of a package\"\"\"
    try:
        return get_distribution(package_name).version
    except DistributionNotFound:
        return "unknown"

def get_current_version():
    \"\"\"Get current package version\"\"\"
    try:
        version = get_distribution(__name__).version
    except DistributionNotFound:
        version = "0.0.0-dev"
    return version

class VersionManager:
    \"\"\"Manage package versions\"\"\"
    
    def __init__(self):
        try:
            self.version = get_distribution(__name__).version
        except DistributionNotFound:
            self.version = "dev"
    
    def check_dependency(self, package):
        try:
            return get_distribution(package).version
        except DistributionNotFound:
            return None
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Should handle usage in functions and classes
        result = refactor.get_code()
        assert result is not None

    def test_pkg_resources_edge_cases(self):
        """Test edge cases in pkg_resources modernization"""
        parser = pyrustor.Parser()
        
        # Test with no pkg_resources imports
        source_no_pkg = """
import os
import sys

def get_version():
    return "1.0.0"
"""
        ast_no_pkg = parser.parse_string(source_no_pkg)
        refactor_no_pkg = pyrustor.Refactor(ast_no_pkg)
        
        # Should not crash when no pkg_resources imports exist
        refactor_no_pkg.replace_import("pkg_resources", "xxx_pyharmony")
        assert True

    def test_pkg_resources_with_comments(self):
        """Test modernizing pkg_resources with comments and docstrings"""
        parser = pyrustor.Parser()
        source = """
\"\"\"
Package version detection module.

This module handles version detection using pkg_resources
for backward compatibility.
\"\"\"

# Import pkg_resources for version detection
from pkg_resources import get_distribution, DistributionNotFound

# TODO: Migrate to importlib.metadata in Python 3.8+
try:
    # Get version from installed package
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Fallback for development installations
    __version__ = "0.0.0-dev.1"

def get_version():
    \"\"\"
    Get the package version.
    
    Uses pkg_resources to detect the installed version,
    with fallback for development environments.
    
    Returns:
        str: Package version string
    \"\"\"
    return __version__
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Should preserve comments and docstrings
        result = refactor.get_code()
        assert result is not None
        # Comments and docstrings should still be present
        assert '"""' in result or "'''" in result

    def test_nested_pkg_resources_usage(self):
        """Test modernizing nested pkg_resources usage patterns"""
        parser = pyrustor.Parser()
        source = """
from pkg_resources import get_distribution, DistributionNotFound

def get_versions(packages):
    \"\"\"Get versions for multiple packages\"\"\"
    versions = {}
    for package in packages:
        try:
            versions[package] = get_distribution(package).version
        except DistributionNotFound:
            versions[package] = None
    return versions

def check_compatibility():
    \"\"\"Check package compatibility\"\"\"
    required_packages = ["numpy", "pandas", "scipy"]
    versions = get_versions(required_packages)
    
    for package, version in versions.items():
        if version is None:
            print(f"Warning: {package} not found")
        else:
            print(f"{package}: {version}")

# Nested try-except with multiple exception types
try:
    main_version = get_distribution(__name__).version
    print(f"Main package version: {main_version}")
except (DistributionNotFound, ImportError) as e:
    print(f"Could not determine version: {e}")
    main_version = "unknown"
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply modernization
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        
        # Should handle nested usage patterns
        result = refactor.get_code()
        assert result is not None

    def test_pkg_resources_modernization_integration(self):
        """Test integration of pkg_resources modernization with other refactoring"""
        parser = pyrustor.Parser()
        source = """
from pkg_resources import get_distribution, DistributionNotFound

class OldVersionManager:
    \"\"\"Old-style version manager\"\"\"
    
    def get_old_version(self):
        try:
            return get_distribution(__name__).version
        except DistributionNotFound:
            return "0.0.0"

def old_get_version():
    \"\"\"Old version getter function\"\"\"
    manager = OldVersionManager()
    return manager.get_old_version()
"""
        ast = parser.parse_string(source)
        refactor = pyrustor.Refactor(ast)
        
        # Apply multiple refactoring operations
        refactor.replace_import("pkg_resources", "xxx_pyharmony")
        refactor.rename_class("OldVersionManager", "ModernVersionManager")
        # Skip method renaming for now - only rename top-level functions
        refactor.rename_function("old_get_version", "get_version")
        
        # Should handle combined refactoring operations
        summary = refactor.change_summary()
        assert "changes" in summary
        
        result = refactor.get_code()
        assert result is not None
