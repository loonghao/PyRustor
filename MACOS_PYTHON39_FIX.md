# macOS Python 3.9 Gettext Dependency Fix Implementation Guide

## Problem

Python 3.9 installation fails on macOS runners with a gettext library dependency error:

```
Error: dyld[1405]: Library not loaded: /usr/local/opt/gettext/lib/libintl.8.dylib
  Referenced from: /Users/runner/hostedtoolcache/Python/3.9.23/x64/bin/python3.9
  Reason: tried: '/usr/local/opt/gettext/lib/libintl.8.dylib' (no such file)
```

The issue was only discovered in main branch CI because PR checks only ran on Ubuntu, missing platform-specific problems.

## Solution

### 1. Fix macOS Python 3.9 Dependencies

In `.github/actions/setup-pyrustor/action.yml`, add this step before the "Setup Python" step:

```yaml
    - name: Fix macOS dependencies for Python 3.9
      if: runner.os == 'macOS' && startsWith(inputs.python-version, '3.9')
      shell: bash
      run: |
        echo "💧 Installing gettext for Python 3.9 on macOS..."
        brew install gettext
        # Create symlink to ensure Python can find the library
        sudo ln -sf /opt/homebrew/lib/libintl.8.dylib /usr/local/lib/libintl.8.dylib 2>/dev/null || true
        sudo ln -sf /usr/local/opt/gettext/lib/libintl.8.dylib /usr/local/lib/libintl.8.dylib 2>/dev/null || true
```

### 2. Improve PR Testing Strategy

In `.github/workflows/pr-checks.yml`, replace the essential-tests job matrix: 

```yaml
  essential-tests:
    name: Essential Tests (${{ matrix.os }}, Python ${{ matrix.python-version }})
    runs-on: ${{ matrix.os }}
    needs: pre-checks
    strategy:
      fail-fast: false  # Don't fail fast - we want to see all results
      matrix:
        # Test critical combinations that often fail
        include:
          # Ubuntu tests - our primary platform
          - os: ubuntu-latest
            python-version: "3.8"
          - os: ubuntu-latest
            python-version: "3.10"
          - os: ubuntu-latest
            python-version: "3.12"
          # macOS tests - catch platform-specific issues like Python 3.9 gettext problem
          - os: macos-latest
            python-version: "3.9"  # This was failing before
          - os: macos-latest
            python-version: "3.10"
          # Windows tests - catch Windows-specific issues
          - os: windows-latest
            python-version: "3.10"
```

And update the cache-key-suffix and artifact-name:

```yaml
          cache-key-suffix: 'essential-test-${{ matrix.os }}'
          artifact-name: 'essential-test-results-${{ matrix.os }}-py${ { matrix.python-version }}'
```

### 3. Add Verification Workflow

Create `.github/workflows/test-macos-python39.yml` for targeted testing:

```yaml
name: Test macOS Python 3.9 Fix

on:
  workflow_dispatch:
  pull_request:
    paths:
      - '.github/actions/setup-pyrustor/**'
      - '.github/workflows/pr-checks.yml'
      - '.github/workflows/test-macos-python39.yml'

permissions:
  contents: read

jobs:
  test-macos-python39:
    name: Test Python 3.9 on macOS
    runs-on: macos-latest
    
    steps:
      - uses: actions/checkout@v4

      - name: Setup PyRustor Environment
        uses: ./.github/actions/setup-pyrustor
        with:
          python-version: "3.9"
          cache-key-suffix: 'macos-python39-test'

      - name: Verify Python 3.9 works
        run: |
          echo "🔍 Testing Python 3.9 functionality..."
          python --version
          python -c "import sys; print(f'Python executable: {sys.executable}')"
          python -c "import platform; print(f'Platform: {platform.platform()}')"
          
          # Test that Python can import basic modules
          python -c "import json, os, sys, subprocess"
          echo "✅ Python 3.9 basic functionality works"

      - name: Test uv functionality
        run: |
          echo "🔍 Testing uv functionality..."
          uv --version
          uv python list
          echo "✅ uv works with Python 3.9"

      - name: Build and Test (Basic)
        uses: ./.github/actions/build-and-test
        with:
          test-type: 'basic'
          generate-stubs: 'false'
```

## Benefits

- ✅ **Early Problem Detection**: Platform-specific issues caught at PR stage
- ✅ **Reliable macOS Support**: Python 3.9 now works correctly on macOS
- ✅ **Better Test Coverage**: Critical platform combinations tested in PRs
- ✅ **Faster Feedback**: No more waiting for main branch CI to find platform issues

This change ensures that future PRs will catch platform-specific issues before they reach the main branch, significantly improving CI reliability and developer experience.
