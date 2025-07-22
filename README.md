# PyRustor

[![PyPI version](https://img.shields.io/pypi/v/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.87+-orange.svg)](https://www.rust-lang.org)
[![CI](https://github.com/loonghao/PyRustor/workflows/CI/badge.svg)](https://github.com/loonghao/PyRustor/actions)

English | [中文](README_zh.md)

A **blazingly fast** Python code parsing and refactoring tool written in Rust with Python bindings.

## 🚀 Features

### 🌟 **Core Advantages**

- **⚡ Superior Performance**: Built on Ruff's blazing-fast Python parser - 10-100x faster than traditional Python tools
- **🔄 Python AST Parsing**: Parse Python code into AST for analysis using Ruff's proven parsing engine
- **🛠️ Code Refactoring**: Rename functions, classes, modernize syntax
- **🧵 Safe Concurrency**: Built with Rust's fearless concurrency
- **🐍 Python Bindings**: Easy-to-use Python API

### 🎛️ **Refactoring Operations**

- **Function Renaming**: Rename functions throughout codebase
- **Class Renaming**: Rename classes and update references
- **Import Modernization**: Update deprecated imports to modern alternatives
- **Syntax Modernization**: Convert old Python syntax to modern patterns
- **Custom Transformations**: Apply custom AST transformations

## 🚀 Quick Start

```bash
pip install pyrustor
```

```python
import pyrustor

# Parse Python code
parser = pyrustor.Parser()
ast = parser.parse_string("def hello(): pass")

# Create refactor instance
refactor = pyrustor.Refactor(ast)
refactor.rename_function("hello", "greet")

# Get the modified code
result = refactor.get_code()
print(result)  # def greet(): pass
```

### ✨ Key Features Demonstration

```python
import pyrustor

# 1. Function and Class Renaming
code = '''
def old_function(x, y):
    return x + y

class OldClass:
    def method(self):
        return old_function(1, 2)
'''

parser = pyrustor.Parser()
ast = parser.parse_string(code)
refactor = pyrustor.Refactor(ast)

# Rename function and class
refactor.rename_function("old_function", "new_function")
refactor.rename_class("OldClass", "NewClass")

print("Refactored code:")
print(refactor.get_code())

# 2. Import Modernization
legacy_code = '''
import ConfigParser
import imp
from urllib2 import urlopen
'''

ast2 = parser.parse_string(legacy_code)
refactor2 = pyrustor.Refactor(ast2)

# Modernize imports
refactor2.replace_import("ConfigParser", "configparser")
refactor2.replace_import("imp", "importlib")
refactor2.replace_import("urllib2", "urllib.request")

print("Modernized imports:")
print(refactor2.get_code())

# 3. Get detailed change information
print("Changes made:")
for change in refactor2.change_summary():
    print(f"  - {change}")
```

## 📦 Installation

### From PyPI (Recommended)

```bash
# Standard installation (Python version-specific wheels)
pip install pyrustor

# ABI3 installation (compatible with Python 3.8+)
pip install pyrustor --prefer-binary
```

### Prerequisites (Building from Source)

- Rust 1.87+ (for building from source)
- Python 3.8+
- maturin (for building Python bindings)

### Build from Source

```bash
# Clone the repository
git clone https://github.com/loonghao/PyRustor.git
cd PyRustor

# Install dependencies
just install

# Build the extension
just build
```

## 🔧 Usage Examples

### Basic Operations

```python
import pyrustor

# Parse Python code
parser = pyrustor.Parser()
ast = parser.parse_string("""
def old_function():
    return "Hello, World!"

class OldClass:
    pass
""")

# Create refactor instance
refactor = pyrustor.Refactor(ast)

# Rename function
refactor.rename_function("old_function", "new_function")

# Rename class
refactor.rename_class("OldClass", "NewClass")

# Get refactored code
print(refactor.get_code())
```

### File Operations

```python
import pyrustor

# Parse from file
parser = pyrustor.Parser()
ast = parser.parse_file("example.py")

# Apply refactoring
refactor = pyrustor.Refactor(ast)
refactor.modernize_syntax()

# Save to file
refactor.save_to_file("refactored_example.py")

# Get change summary
print(refactor.change_summary())
```

### Complete Refactoring Workflow

```python
import pyrustor

def modernize_legacy_code(source_code: str) -> str:
    """Complete workflow for modernizing legacy Python code."""
    parser = pyrustor.Parser()
    ast = parser.parse_string(source_code)
    refactor = pyrustor.Refactor(ast)

    # Step 1: Modernize imports
    refactor.replace_import("ConfigParser", "configparser")
    refactor.replace_import("urllib2", "urllib.request")
    refactor.replace_import("imp", "importlib")

    # Step 2: Rename outdated functions/classes
    refactor.rename_function("old_function", "new_function")
    refactor.rename_class("LegacyClass", "ModernClass")

    # Step 3: Apply syntax modernization
    refactor.modernize_syntax()

    # Step 4: Get the final result
    return refactor.get_code()

# Example usage
legacy_code = '''
import ConfigParser
import urllib2

def old_function():
    config = ConfigParser.ConfigParser()
    response = urllib2.urlopen("http://example.com")
    return response.read()

class LegacyClass:
    def __init__(self):
        self.data = old_function()
'''

modernized = modernize_legacy_code(legacy_code)
print("Modernized code:")
print(modernized)

# Get detailed change information
parser = pyrustor.Parser()
ast = parser.parse_string(legacy_code)
refactor = pyrustor.Refactor(ast)
refactor.replace_import("ConfigParser", "configparser")
refactor.rename_function("old_function", "new_function")

print("\nChanges made:")
for change in refactor.change_summary():
    print(f"  - {change}")
```

### Error Handling and Validation

```python
import pyrustor

def safe_refactor(code: str, old_name: str, new_name: str) -> tuple[str, bool]:
    """Safely refactor code with error handling."""
    try:
        parser = pyrustor.Parser()
        ast = parser.parse_string(code)
        refactor = pyrustor.Refactor(ast)

        # Attempt to rename function
        refactor.rename_function(old_name, new_name)

        return refactor.get_code(), True

    except Exception as e:
        print(f"Refactoring failed: {e}")
        return code, False  # Return original code if refactoring fails

# Example usage
code = "def hello(): pass"
result, success = safe_refactor(code, "hello", "greet")

if success:
    print("Refactoring successful:")
    print(result)
else:
    print("Refactoring failed, original code preserved")
```

### Advanced Refactoring

```python
import pyrustor

parser = pyrustor.Parser()
ast = parser.parse_string("""
import ConfigParser
from imp import reload

def format_string(name, age):
    return "Name: %s, Age: %d" % (name, age)
""")

refactor = pyrustor.Refactor(ast)

# Modernize imports
refactor.replace_import("ConfigParser", "configparser")
refactor.replace_import("imp", "importlib")

# Modernize syntax
refactor.modernize_syntax()

print(refactor.to_string())
print("Changes made:")
print(refactor.change_summary())
```

### Ruff Formatter Integration

```python
import pyrustor

# Messy code that needs refactoring and formatting
messy_code = '''def   old_function(  x,y  ):
    return x+y

class   OldClass:
    def __init__(self,name):
        self.name=name'''

parser = pyrustor.Parser()
ast = parser.parse_string(messy_code)
refactor = pyrustor.Refactor(ast)

# Refactor with automatic formatting
refactor.rename_function_with_format("old_function", "new_function", apply_formatting=True)
refactor.rename_class_with_format("OldClass", "NewClass", apply_formatting=True)

# Or apply formatting at the end
refactor.modernize_syntax()
formatted_result = refactor.refactor_and_format()

print("Beautifully formatted result:")
print(formatted_result)
```

### Building pyupgrade-style Tools

```python
import pyrustor

def modernize_python_code(source_code: str) -> str:
    """Build a pyupgrade-style modernization tool."""
    parser = pyrustor.Parser()
    ast = parser.parse_string(source_code)
    refactor = pyrustor.Refactor(ast)

    # Apply common modernizations
    refactor.replace_import("ConfigParser", "configparser")
    refactor.replace_import("urllib2", "urllib.request")
    refactor.modernize_syntax()  # % formatting -> f-strings, etc.

    # Return beautifully formatted result
    return refactor.refactor_and_format()

# Example usage
legacy_code = '''import ConfigParser
def greet(name):
    return "Hello, %s!" % name'''

modernized = modernize_python_code(legacy_code)
print(modernized)
# Output: Clean, modern Python code with f-strings and updated imports
```

## 📚 API Reference

### Parser Class

```python
parser = pyrustor.Parser()

# Parse from string
ast = parser.parse_string(source_code)

# Parse from file
ast = parser.parse_file("path/to/file.py")

# Parse directory
results = parser.parse_directory("path/to/dir", recursive=True)
```

### PythonAst Class

```python
# Check if AST is empty
if ast.is_empty():
    print("No code found")

# Get statistics
print(f"Statements: {ast.statement_count()}")
print(f"Functions: {ast.function_names()}")
print(f"Classes: {ast.class_names()}")
print(f"Imports: {ast.imports()}")

# Convert back to string
source_code = ast.to_string()
```

### Refactor Class

```python
refactor = pyrustor.Refactor(ast)

# Basic refactoring
refactor.rename_function("old_name", "new_name")
refactor.rename_class("OldClass", "NewClass")
refactor.replace_import("old_module", "new_module")

# Refactoring with automatic formatting
refactor.rename_function_with_format("old_name", "new_name", apply_formatting=True)
refactor.rename_class_with_format("OldClass", "NewClass", apply_formatting=True)
refactor.modernize_syntax_with_format(apply_formatting=True)

# Advanced refactoring
refactor.modernize_syntax()
refactor.modernize_imports()

# Formatting options
refactor.format_code()  # Apply Ruff formatting
formatted_result = refactor.refactor_and_format()  # Refactor + format in one step
conditional_format = refactor.to_string_with_format(apply_formatting=True)

# Get results
refactored_code = refactor.to_string()
changes = refactor.change_summary()

# Save to file
refactor.save_to_file("output.py")
```

## 🧪 Development

### Setup Development Environment

```bash
# Install just (command runner)
cargo install just

# Setup development environment
just dev

# Run tests
just test

# Format code
just format

# Run linting
just lint

# Build release
just release
```

### Testing

PyRustor has comprehensive test coverage with 257+ tests across Rust and Python components.

```bash
# Run all tests (Rust + Python)
just test

# Run specific test categories
just test-rust          # 91 Rust tests
just test-python        # 166 Python tests

# Run with coverage reporting
just coverage-all       # Generate coverage reports for both languages
just coverage-python    # Python coverage only
just coverage-rust      # Rust coverage only

# Run specific test types
pytest tests/ -m "unit"           # Unit tests only
pytest tests/ -m "integration"    # Integration tests only
pytest tests/ -m "benchmark"      # Performance benchmarks
pytest tests/ -m "not slow"       # Skip slow tests
```

#### Test Categories

- **Unit Tests**: Core functionality testing
- **Integration Tests**: End-to-end workflow testing
- **Edge Case Tests**: Boundary conditions and error handling
- **Performance Tests**: Benchmarking and regression detection
- **Unicode Tests**: International character support
- **Error Handling Tests**: Robust error recovery

#### Coverage Reports

After running coverage tests, view detailed reports:
- **Python**: `htmlcov/index.html`
- **Rust**: `target/tarpaulin/tarpaulin-report.html`

### Quality Assurance

```bash
# Run all quality checks
just check-all

# Individual quality checks
just quality            # Code quality analysis
just security           # Security vulnerability scanning
just performance        # Performance benchmarking
just docs-check         # Documentation validation

# CI-specific checks
just ci-check-all       # All checks optimized for CI
```

### Available Commands

```bash
just --list  # Show all available commands
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [**Ruff**](https://github.com/astral-sh/ruff) - PyRustor is built on Ruff's high-performance Python AST parsing engine (`ruff_python_ast`). Ruff is an extremely fast Python linter and code formatter written in Rust, developed by [Astral](https://astral.sh). We leverage Ruff's proven parsing technology to deliver blazing-fast Python code analysis and refactoring capabilities.
- [PyO3](https://github.com/PyO3/pyo3) for excellent Python-Rust bindings
- [maturin](https://github.com/PyO3/maturin) for seamless Python package building
