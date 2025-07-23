"""
Legacy pkg_resources usage example for testing PyRustor.

This file contains common patterns using pkg_resources that need
to be modernized to use importlib.metadata or custom solutions.
"""

from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution
from pkg_resources import resource_filename
from pkg_resources import resource_string
from pkg_resources import iter_entry_points
from pkg_resources import require
from pkg_resources import working_set
from pkg_resources import parse_version

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = "0.0.0-dev.1"

class PackageManager:
    """Package manager using legacy pkg_resources."""
    
    def __init__(self, package_name):
        self.package_name = package_name
        self.distribution = None
        try:
            self.distribution = get_distribution(package_name)
        except DistributionNotFound:
            self.distribution = None
    
    def get_version(self):
        """Get package version using pkg_resources."""
        if self.distribution:
            return self.distribution.version
        else:
            return "unknown"
    
    def get_resource_path(self, resource_name):
        """Get resource file path using pkg_resources."""
        try:
            return resource_filename(self.package_name, resource_name)
        except Exception as e:
            return f"Error getting resource: {e}"
    
    def get_resource_content(self, resource_name):
        """Get resource content using pkg_resources."""
        try:
            content = resource_string(self.package_name, resource_name)
            return content.decode('utf-8')
        except Exception as e:
            return f"Error reading resource: {e}"
    
    def check_requirements(self, requirements):
        """Check requirements using pkg_resources."""
        try:
            require(requirements)
            return "Requirements satisfied"
        except Exception as e:
            return f"Requirements not met: {e}"
    
    def list_entry_points(self, group_name):
        """List entry points using pkg_resources."""
        entry_points = []
        for ep in iter_entry_points(group_name):
            entry_points.append({
                'name': ep.name,
                'module': ep.module_name,
                'attrs': ep.attrs
            })
        return entry_points
    
    def compare_versions(self, version1, version2):
        """Compare versions using pkg_resources."""
        v1 = parse_version(version1)
        v2 = parse_version(version2)
        
        if v1 < v2:
            return f"{version1} is older than {version2}"
        elif v1 > v2:
            return f"{version1} is newer than {version2}"
        else:
            return f"{version1} equals {version2}"

def get_package_info(package_name):
    """Get package information using pkg_resources."""
    try:
        dist = get_distribution(package_name)
        return {
            'name': dist.project_name,
            'version': dist.version,
            'location': dist.location,
            'requires': [str(req) for req in dist.requires()],
            'metadata': dist.get_metadata('METADATA') if dist.has_metadata('METADATA') else None
        }
    except DistributionNotFound:
        return {'error': f'Package {package_name} not found'}

def load_config_from_package(package_name, config_file):
    """Load configuration file from package using pkg_resources."""
    try:
        config_path = resource_filename(package_name, config_file)
        with open(config_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading config: {e}"

def get_all_installed_packages():
    """Get all installed packages using pkg_resources."""
    packages = []
    for dist in working_set:
        packages.append({
            'name': dist.project_name,
            'version': dist.version,
            'location': dist.location
        })
    return packages

def find_plugins(plugin_group):
    """Find plugins using entry points."""
    plugins = {}
    for entry_point in iter_entry_points(plugin_group):
        try:
            plugin_class = entry_point.load()
            plugins[entry_point.name] = {
                'class': plugin_class,
                'module': entry_point.module_name,
                'name': entry_point.name
            }
        except Exception as e:
            plugins[entry_point.name] = {'error': str(e)}
    return plugins

def validate_package_version(package_name, min_version):
    """Validate that a package meets minimum version requirement."""
    try:
        dist = get_distribution(package_name)
        current_version = parse_version(dist.version)
        required_version = parse_version(min_version)
        
        if current_version >= required_version:
            return f"Package {package_name} version {dist.version} meets requirement >= {min_version}"
        else:
            return f"Package {package_name} version {dist.version} does not meet requirement >= {min_version}"
    except DistributionNotFound:
        return f"Package {package_name} not found"

class PluginLoader:
    """Plugin loader using pkg_resources entry points."""
    
    def __init__(self, plugin_group):
        self.plugin_group = plugin_group
        self.plugins = {}
        self.load_plugins()
    
    def load_plugins(self):
        """Load all plugins from entry points."""
        for entry_point in iter_entry_points(self.plugin_group):
            try:
                plugin_class = entry_point.load()
                self.plugins[entry_point.name] = plugin_class
            except Exception as e:
                print(f"Failed to load plugin {entry_point.name}: {e}")
    
    def get_plugin(self, plugin_name):
        """Get a specific plugin by name."""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self):
        """List all available plugins."""
        return list(self.plugins.keys())

def check_optional_dependencies():
    """Check for optional dependencies using pkg_resources."""
    optional_packages = ['numpy', 'pandas', 'matplotlib', 'requests']
    results = {}
    
    for package in optional_packages:
        try:
            dist = get_distribution(package)
            results[package] = {
                'installed': True,
                'version': dist.version,
                'location': dist.location
            }
        except DistributionNotFound:
            results[package] = {
                'installed': False,
                'version': None,
                'location': None
            }
    
    return results

# Example usage patterns
if __name__ == "__main__":
    # Get current package version
    print(f"Current package version: {__version__}")
    
    # Create package manager
    manager = PackageManager("setuptools")
    print(f"Setuptools version: {manager.get_version()}")
    
    # Get package info
    info = get_package_info("pip")
    print(f"Pip info: {info}")
    
    # Check optional dependencies
    deps = check_optional_dependencies()
    for pkg, info in deps.items():
        if info['installed']:
            print(f"{pkg}: {info['version']}")
        else:
            print(f"{pkg}: not installed")
    
    # Load plugins
    plugin_loader = PluginLoader("console_scripts")
    print(f"Found {len(plugin_loader.list_plugins())} console scripts")
