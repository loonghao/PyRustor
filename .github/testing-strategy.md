# Testing Strategy

This document outlines the comprehensive testing strategy for PyRustor to ensure code quality and prevent release failures.

## Test Levels

### 1. PR Checks (Fast & Essential)
**Workflow**: `pr-checks.yml`
**Trigger**: Every PR
**Duration**: ~5-10 minutes

#### Pre-flight Checks
- ✅ Version consistency across all files
- ✅ Basic syntax validation (Rust + Python)

#### Essential Tests
- ✅ Unit tests on Python 3.8, 3.10, 3.12
- ✅ Rust tests (`cargo test`)
- ✅ Python tests (`pytest` with strict mode)
- ✅ Import and basic functionality tests

#### Coverage Requirements
- ✅ Python coverage ≥70% (enforced)
- ✅ Rust coverage report generated
- ✅ Coverage reports uploaded as artifacts
- ✅ PR comments with coverage details

#### Code Quality
- ✅ Rust formatting (`cargo fmt`)
- ✅ Rust linting (`cargo clippy`)
- ✅ Python formatting (`ruff format`)
- ✅ Python linting (`ruff check`)

### 2. Comprehensive CI (Full Testing)
**Workflow**: `ci.yml`
**Trigger**: Main branch, labeled PRs
**Duration**: ~15-30 minutes

#### Extended Testing
- All platforms: Ubuntu, Windows, macOS
- All Python versions: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Benchmark tests
- Wheel building and testing
- Security audits

### 3. Coverage Monitoring
**Workflow**: `coverage.yml`
**Trigger**: Code changes in core paths
**Duration**: ~8-12 minutes

#### Detailed Coverage Analysis
- Line-by-line coverage reports
- Branch coverage analysis
- Codecov integration
- Historical coverage tracking

## Test Commands

### Development Commands
```bash
# Quick tests during development
just test-fast                    # Fast tests only
just test-cov                     # Tests with coverage
just coverage-python-dev          # Coverage with failure tolerance

# Specific test types
just test-marker "not slow"       # Tests without slow marker
just test-file tests/test_api.py  # Single test file
```

### CI Commands
```bash
# Strict CI commands (used in workflows)
just ci-test-python-strict        # All Python tests must pass
just coverage-python-ci           # Coverage with strict requirements
just ci-test-rust                 # Rust tests
just ci-test-basic                # Import and basic functionality
```

## Coverage Thresholds

### Minimum Requirements (PR Blocking)
- **Python**: 70% line coverage
- **Rust**: Coverage report generated (no minimum enforced yet)

### Target Goals
- **Python**: 85% line coverage
- **Rust**: 80% line coverage
- **Integration**: 90% of public API covered

### Coverage Exclusions
- Generated code (stubs, bindings)
- Test files themselves
- Development scripts
- Example code

## Test Organization

### Test Structure
```
tests/
├── test_api_compatibility.py     # Public API tests
├── test_basic.py                 # Core functionality
├── test_benchmarks.py            # Performance tests
├── test_edge_cases_*.py          # Edge case testing
├── test_error_handling.py        # Error scenarios
├── test_integration.py           # Integration tests
├── test_parser_*.py              # Parser-specific tests
├── test_performance_*.py         # Performance validation
└── data/                         # Test data files
```

### Test Markers
- `benchmark`: Performance tests (slow)
- `slow`: Tests that take >1 second
- `integration`: Integration tests
- `unit`: Pure unit tests

## Failure Handling

### PR Checks (Strict)
- Any test failure blocks PR merge
- Coverage below threshold blocks PR merge
- Linting issues block PR merge
- Version inconsistency blocks PR merge

### Development Mode (Tolerant)
- Use `coverage-python-dev` for local development
- Allows some test failures during refactoring
- Generates reports even with failures

## Quality Gates

### Required for PR Merge
1. ✅ All pre-flight checks pass
2. ✅ Essential tests pass on all Python versions
3. ✅ Coverage meets minimum threshold (70%)
4. ✅ Code quality checks pass
5. ✅ No linting issues

### Optional (Triggered by Labels)
- `full-ci`: Run comprehensive test suite
- `test-wheels`: Test wheel building
- `benchmark`: Run performance tests
- `security-check`: Run security audits

## Monitoring and Reporting

### Artifacts Generated
- Coverage reports (HTML + XML)
- Test results and logs
- Performance benchmarks
- Security audit reports

### Integration
- Codecov for coverage tracking
- GitHub PR comments for coverage
- Artifact uploads for debugging
- Step summaries for quick overview

This strategy ensures high code quality while maintaining fast feedback loops for developers.
