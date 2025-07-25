# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.3...pyrustor-v0.1.4) (2025-07-25)


### Features

* add CI optimization validation test suite ([382617b](https://github.com/loonghao/PyRustor/commit/382617b64e365703fcd7bfc05d89dcea55031b94))
* add comprehensive version synchronization system ([95017bf](https://github.com/loonghao/PyRustor/commit/95017bffbd257401fc94be379f8ea7f42fc9be2f))
* optimize CI configuration with reusable components ([f4733a0](https://github.com/loonghao/PyRustor/commit/f4733a062a783b0d8c08239099c34dcd833267a9))


### Bug Fixes

* add intelligent architecture compatibility checking for wheel tests ([1e1134a](https://github.com/loonghao/PyRustor/commit/1e1134a12b15b5e7e900ec9b3f6478b5dccb02b0))
* add robust wheel installation with manual extraction fallback ([21ac4e4](https://github.com/loonghao/PyRustor/commit/21ac4e4db3f15a44a8c8abd6e01e96a56b9ca96e))
* resolve macOS wheel platform compatibility issue ([fa3a08e](https://github.com/loonghao/PyRustor/commit/fa3a08e614a9b2620255026ad22e9315ff62dd9c))
* resolve Python 3.13 compatibility issues in CI ([4512d1b](https://github.com/loonghao/PyRustor/commit/4512d1b9f956247e3546874d5624503e5234f57c))
* resolve version consistency and improve CI error handling ([9aa344f](https://github.com/loonghao/PyRustor/commit/9aa344f216c6f314bea14112b330d9326efae6fe))
* resolve Windows wheel installation issue in CI ([f748b58](https://github.com/loonghao/PyRustor/commit/f748b58e4cfb677ac382b455de93b29ed1ca90b2))
* switch to Python 3.10 for better cross-platform compatibility ([920aa6c](https://github.com/loonghao/PyRustor/commit/920aa6c86c19fa18606322edeaeace3fed4ea3b3))


### Code Refactoring

* clean up CI workflows by renaming optimized versions ([683fe54](https://github.com/loonghao/PyRustor/commit/683fe549af9f3d55dd0f9df64b5683a4d9426d2f))


### Documentation

* update optimization summary with version sync system and test results ([be18cce](https://github.com/loonghao/PyRustor/commit/be18cce286657f69613c5795ac815f2799cceee3))

## [0.1.3](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.2...pyrustor-v0.1.3) (2025-07-25)


### Features

* add support for collections and for loops in AST generation ([f8e7c33](https://github.com/loonghao/PyRustor/commit/f8e7c336a25315bbead193eed00e260880c61e4e))
* comprehensive development infrastructure improvements ([00fbcf1](https://github.com/loonghao/PyRustor/commit/00fbcf1310fea4fb43f23b6922a70ca5b186a827))
* comprehensive test coverage improvements and bug fixes ([8f7b6fc](https://github.com/loonghao/PyRustor/commit/8f7b6fc2f93ad64ac9d404b1f6968d6476322ea3))
* implement comprehensive bottom-level API and fix all test failures ([31d5437](https://github.com/loonghao/PyRustor/commit/31d5437b5459832e58ffdde6d357af623c91d497))


### Bug Fixes

* allow CI tests to continue despite expected failures ([7aa6880](https://github.com/loonghao/PyRustor/commit/7aa68803cce0a3eddf1fdc6b28cca08fe62dee3d))
* correct coverage action configuration and CI command syntax ([78139f4](https://github.com/loonghao/PyRustor/commit/78139f4e9d511a0477703fbf6d6d9d8931a0b6bd))
* correct syntax error in ci-test-basic command ([e0f7765](https://github.com/loonghao/PyRustor/commit/e0f77653d652e1e86a927433670e934ce8cd1ca6))
* create virtual environment for maturin installation ([ffce75e](https://github.com/loonghao/PyRustor/commit/ffce75eaf84469f0919b3a00bfa0a9c00640c10d))
* implement proper get_code functionality and improve CI ([9832d23](https://github.com/loonghao/PyRustor/commit/9832d23f4bbae86d9f77b1fd7a22960e6ff5751e))
* improve coverage configuration for CI compatibility ([0052901](https://github.com/loonghao/PyRustor/commit/0052901cba1ec1663b23a524ce39e05a5c07337f))
* improve PR testing and version synchronization ([146dcd1](https://github.com/loonghao/PyRustor/commit/146dcd11100530a35ec87f3ec8624aaf5eba4a5b))
* resolve CI coverage failures after AST refactoring ([e6e6c62](https://github.com/loonghao/PyRustor/commit/e6e6c62bc5e95b3fbfb3d81399b128533a88bbc3))
* resolve CI failures and improve command compatibility ([e9bbe81](https://github.com/loonghao/PyRustor/commit/e9bbe81bd700a78d8a317b926881451a281bdba9))
* resolve coverage action failures with relative paths and permissions ([643b0f9](https://github.com/loonghao/PyRustor/commit/643b0f98af1e0479a8109a384702405c6c724eb7))
* resolve Unicode encoding errors and test failures in CI ([bc54cd4](https://github.com/loonghao/PyRustor/commit/bc54cd4ae5cd0c2d000033c3959504513b919695))
* use standard venv instead of uv venv in CI ([c7a8405](https://github.com/loonghao/PyRustor/commit/c7a840545c9f0508c388b248c4b9c2046e7ee874))


### Code Refactoring

* modularize AST code into separate modules ([9909497](https://github.com/loonghao/PyRustor/commit/99094975409149e2b8c93cede9cc56aad3dab1c0))

## [0.1.2](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.1...pyrustor-v0.1.2) (2025-07-22)


### Bug Fixes

* add manifest-path to all ABI3 builds and unify Python versions ([c7e2338](https://github.com/loonghao/PyRustor/commit/c7e23387cf4a68331339ec2839b766c4a37c05c5))
* add missing bindings configuration to crate pyproject.toml ([a6c5139](https://github.com/loonghao/PyRustor/commit/a6c51397f8ee14f88158e0a63e90e8802156a333))
* add python-packages configuration to include Python source files ([db93e08](https://github.com/loonghao/PyRustor/commit/db93e08e74d726c87aa427f371a9c89b4edb8ce3))
* comprehensive macOS ABI3 build fixes ([b0b3c36](https://github.com/loonghao/PyRustor/commit/b0b3c3683b1baea391ae918e504be5920e91cd4c))
* improve wheel building and testing infrastructure ([a6ebcfe](https://github.com/loonghao/PyRustor/commit/a6ebcfe0ab605ee1f82c8ae076cc0e589c7a0ced))
* simplify macOS ABI3 build configuration ([a51f900](https://github.com/loonghao/PyRustor/commit/a51f900dc9a56ae97e0b69d7698992b851ab57e5))


### Code Refactoring

* simplify project structure and fix wheel packaging ([36cdaf2](https://github.com/loonghao/PyRustor/commit/36cdaf22a8a4224f2ffc246a2a3fe16e9c0e1924))

## [0.1.1](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.0...pyrustor-v0.1.1) (2025-07-22)


### Bug Fixes

* disable clippy uninlined_format_args in CI ([65297ce](https://github.com/loonghao/PyRustor/commit/65297cef99c642980c0e35bcb7fc40e8b7ff4079))
* resolve clippy wrong_self_convention warnings ([8648ffa](https://github.com/loonghao/PyRustor/commit/8648ffac729953542f05174ee16dc71dfabbfae5))
* resolve macOS ABI3 build issues ([d5ce5b5](https://github.com/loonghao/PyRustor/commit/d5ce5b5daeddfc29fd8c39b86e20b40af0910246))
* update test files to use renamed methods ([53ebe45](https://github.com/loonghao/PyRustor/commit/53ebe45192a71486ff88d0ee202baec083f4b528))

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
