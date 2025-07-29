# Branch Protection Configuration

This document describes the recommended branch protection rules for the `main` branch to ensure code quality and prevent release failures.

## Required Status Checks

The following checks must pass before a PR can be merged:

### Essential Checks (from pr-checks.yml)
- `PR Ready for Merge` - Overall gate that ensures all essential checks pass
- `Pre-flight Checks` - Version consistency and basic syntax
- `Essential Tests` - Core functionality tests on Python 3.8, 3.10, 3.12
- `Code Quality` - Linting and formatting checks

### Optional Checks (triggered by labels)
- `Full Test Suite` - Comprehensive testing across all platforms (label: `full-ci`)
- `Wheel Test` - Wheel building and testing (label: `test-wheels`)
- `Security & Quality` - Security audits (label: `security-check`)
- `Benchmark Tests` - Performance testing (label: `benchmark`)

## Configuration Steps

1. Go to Repository Settings → Branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select these required checks:
   - `PR Ready for Merge`
5. Enable "Require branches to be up to date before merging"
6. Enable "Restrict pushes that create files"

## Benefits

- **Faster PR feedback**: Essential checks run quickly on every PR
- **Comprehensive testing**: Full test suite runs on main branch and when requested
- **Release confidence**: All critical issues caught before merge
- **Reduced CI costs**: Expensive tests only run when needed

## Workflow Separation

- **pr-checks.yml**: Fast, essential validations for every PR
- **ci.yml**: Comprehensive testing for main branch and labeled PRs
- **release.yml**: Build and publish only (no testing)

This separation ensures:
1. PRs get fast feedback on critical issues
2. Main branch gets comprehensive testing
3. Releases are fast and reliable (testing already done)
