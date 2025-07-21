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
result = refactor.to_string()
print(result)  # def greet(): pass
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
print(refactor.to_string())
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

### Code Simplification for Testing

```python
import pyrustor

# Convert complex production code to test-friendly version
production_code = '''
from __future__ import absolute_import
from rez_builder import PipFromDownloadBuilder

SOURCES = {
    "downloads": [
        {
            "file_name": "shiboken6-6.5.0-cp37-abi3-win_amd64.whl",
            "checksum": {
                "sha256": "aee9708517821aaef547c83d689bf524d6f217d47232cb313d9af9e630215eed"
            },
        }
    ]
}

if __name__ == "__main__":
    BUILDER = PipFromDownloadBuilder(SOURCES)
    BUILDER.build()
'''

parser = pyrustor.Parser()
ast = parser.parse_string(production_code)
refactor = pyrustor.Refactor(ast)

# Convert to test-friendly version with formatting
refactor.convert_to_test_code()
simplified_code = refactor.refactor_and_format()

print("Simplified test code:")
print(simplified_code)
# Output: Clean, formatted code with mock data
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

# Advanced refactoring
refactor.modernize_syntax()
refactor.modernize_imports()

# Code simplification for testing
refactor.convert_to_test_code()
refactor.replace_complex_data_with_mocks()

# Get results with formatting
refactored_code = refactor.refactor_and_format()
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
