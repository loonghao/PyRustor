# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.13](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.12...pyrustor-v0.1.13) (2025-08-02)


### Features

* implement automatic version management with release-please ([42b0064](https://github.com/loonghao/PyRustor/commit/42b0064670cee9c1c33f879b207fb76325b31097))
* improve version extraction with Python script and fallback ([7bf7ee9](https://github.com/loonghao/PyRustor/commit/7bf7ee925a351ed9564a7efb73b8981eb272a86b))


### Bug Fixes

* resolve CI pre-flight checks by ensuring Python environment for PyO3 ([e4389e7](https://github.com/loonghao/PyRustor/commit/e4389e7ca61baa3e65d3df1209c52632bbf5cf2d))
* resolve sed regex backreference issue in version sync action ([0b12418](https://github.com/loonghao/PyRustor/commit/0b124188275c572f47812f33014c17be88b7847e))
* sync Python package version to 0.1.11 for consistency ([7bb957c](https://github.com/loonghao/PyRustor/commit/7bb957c26833a45fee869a8de65e21f3c56e6c12))
* synchronize Python package version to 0.1.12 ([299d8c1](https://github.com/loonghao/PyRustor/commit/299d8c13997e4a34b4fcd5e58896473033a9f1e3))


### Documentation

* improve version sync script documentation ([3068301](https://github.com/loonghao/PyRustor/commit/3068301d49f5dfcba2550471b1690333dea303be))

## [0.1.12](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.11...pyrustor-v0.1.12) (2025-07-31)


### Bug Fixes

* skip wheel testing on incompatible architecture in macOS ABI3 builds ([f64409f](https://github.com/loonghao/PyRustor/commit/f64409f180eb4c16661c3f52b2797c66ddb9874d))

## [0.1.11](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.10...pyrustor-v0.1.11) (2025-07-31)


### Bug Fixes

* resolve macOS Python gettext dependency issues in release workflows ([a3b07d6](https://github.com/loonghao/PyRustor/commit/a3b07d6d845a22e7460fbea2332d6b78a50f6a99))

## [0.1.10](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.9...pyrustor-v0.1.10) (2025-07-31)


### Bug Fixes

* correct Cargo.toml version extraction in GitHub Actions ([4f46149](https://github.com/loonghao/PyRustor/commit/4f46149420edc81022eaac4fc58044e1292a518b))

## [0.1.9](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.8...pyrustor-v0.1.9) (2025-07-31)


### Bug Fixes

* improve version synchronization script and clean build artifacts ([3d0f7ab](https://github.com/loonghao/PyRustor/commit/3d0f7ab9d6fc8575c77212e594b97adc9ca2fa8d))
* resolve macOS Python 3.9 gettext dependency issue ([56ab7d1](https://github.com/loonghao/PyRustor/commit/56ab7d162a1300751cd85add307d810caccc9cbb))

## [0.1.8](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.7...pyrustor-v0.1.8) (2025-07-30)


### Features

* simplify CI configuration for better PR-Release consistency ([52c5ce3](https://github.com/loonghao/PyRustor/commit/52c5ce3f8e4f4919eae7d3e2dcf82239dc23f14c))


### Bug Fixes

* resolve Windows wheel compatibility and artifact naming conflicts ([8cf3f8e](https://github.com/loonghao/PyRustor/commit/8cf3f8eeddd6d308b910557eb9566418bf139495))

## [0.1.7](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.6...pyrustor-v0.1.7) (2025-07-29)


### Features

* add comprehensive test coverage to PR checks ([0069bf8](https://github.com/loonghao/PyRustor/commit/0069bf86e3113f76e56a5b999ab65967573c509b))
* improve CI/CD pipeline to prevent release failures ([80e551e](https://github.com/loonghao/PyRustor/commit/80e551ed974e0c7b6df16b9391e817c10a02c63f))


### Code Refactoring

* optimize test coverage strategy for Rust-Python hybrid project ([9107890](https://github.com/loonghao/PyRustor/commit/91078908461a96a476e747e9f2ecf5e6aaf2864b))

## [0.1.6](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.5...pyrustor-v0.1.6) (2025-07-29)


### Bug Fixes

* add comprehensive AST statement and expression support ([e1a14a2](https://github.com/loonghao/PyRustor/commit/e1a14a223844ade80c65cb82d045156ffe10c8ab))
* add missing psutil dependency for ABI3 wheel tests ([7f97d0f](https://github.com/loonghao/PyRustor/commit/7f97d0feaccc7b9a4b78fea831256134be6346c9))
* add support for augmented assignment statements ([7a08edc](https://github.com/loonghao/PyRustor/commit/7a08edcc18693fcea809e072c64784832de69154))
* add test dependency group to CI installation ([2100ada](https://github.com/loonghao/PyRustor/commit/2100ada17a4101271a4d67f0918e69f6467a1d16))
* handle permission errors consistently across platforms ([ffad3ae](https://github.com/loonghao/PyRustor/commit/ffad3aeeb65341db30fe66faa720423d0e3aacb5))
* optimize CI cache configuration to resolve cache warnings ([afb8053](https://github.com/loonghao/PyRustor/commit/afb80535323f3892cb76c5cacfaa5c952e367c11))
* pin Ruff dependencies to stable version 0.12.5 ([115dd8a](https://github.com/loonghao/PyRustor/commit/115dd8ad7be43404b5590b1a77cbcdc15f028ab9))
* remove duplicate Expr::Set pattern and debug file ([fd4c4a6](https://github.com/loonghao/PyRustor/commit/fd4c4a6c0f490e39c2a50962d52eca012f2a98d9))
* resolve cargo-audit installation conflicts in CI ([f48b81f](https://github.com/loonghao/PyRustor/commit/f48b81fe57d4a633ea4341e096ac7ad6374baeb8))
* resolve platform-specific test failures ([722f0a9](https://github.com/loonghao/PyRustor/commit/722f0a94ac34e8591a88b5088fa80382c8cac7fd))
* resolve PR and release version inconsistency issues ([2688aa6](https://github.com/loonghao/PyRustor/commit/2688aa6804e535288b812499ca42de70f5de6423))
* unify CI environments across PR and release stages ([a9be491](https://github.com/loonghao/PyRustor/commit/a9be4910fb6b8d84f301a801cb500850058b2fa2))

## [0.1.5](https://github.com/loonghao/PyRustor/compare/pyrustor-v0.1.4...pyrustor-v0.1.5) (2025-07-27)


### Bug Fixes

* add pytest-cov dependency for ABI3 builds and update Python version ([dbb21db](https://github.com/loonghao/PyRustor/commit/dbb21db39e4aea895129c3464b6503f53790da76))
* sync Python package version to 0.1.4 ([19a70db](https://github.com/loonghao/PyRustor/commit/19a70db02c59da1dc9484f924a7480f8b6604fb6))

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
