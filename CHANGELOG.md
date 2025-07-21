# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2025-07-21)


### Bug Fixes

* add issues permission and disable clippy uninlined_format_args globally ([4ef781c](https://github.com/loonghao/PyRustor/commit/4ef781c60b1f77ca8848f6aeb1739fc68d22f669))
* simplify release-please config with full bootstrap-sha ([f54a8a7](https://github.com/loonghao/PyRustor/commit/f54a8a780b5772c36d8c8307ce36019f036c66b3))

## [Unreleased]

### Features

- Initial implementation of PyRustor - a blazingly fast Python code parsing and refactoring tool
- Rust-based Python AST parsing using Ruff's high-performance parser
- Python bindings with PyO3 for easy integration
- Core refactoring operations:
  - Function and class renaming
  - Import statement replacement and modernization
  - Python syntax modernization (% formatting to f-strings, etc.)
- Ruff formatter integration for high-quality code formatting
- Comprehensive API with optional formatting parameters
- Support for building pyupgrade-style modernization tools
- Complete CI/CD pipeline with multi-platform builds
- ABI3 wheel support for broad Python version compatibility

### Documentation

- Comprehensive README with examples and API reference
- Chinese translation of documentation
- Examples for building pyupgrade-style tools
- Proper attribution to Ruff project

### Performance

- Built on Ruff's blazing-fast Python parser (10-100x faster than traditional tools)
- Rust implementation for maximum performance and safety
- Efficient AST manipulation and code generation

### Testing

- Comprehensive test suite with 75+ tests
- Integration tests for formatting functionality
- Benchmark tests for performance validation
- Cross-platform testing on Linux, Windows, and macOS

[Unreleased]: https://github.com/loonghao/PyRustor/compare/HEAD
