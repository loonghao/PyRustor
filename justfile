# justfile for PyRustor development
# Run `just --list` to see all available commands

# Set shell for Windows compatibility
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["sh", "-c"]

# Default recipe to display help
default:
    @just --list

# Install dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync --group dev

# Build the extension module
build:
    @echo "🔧 Building extension module..."
    uvx maturin develop

# Build with release optimizations
build-release:
    @echo "🚀 Building release version..."
    uvx maturin develop --release

# Run tests
test:
    @echo "🧪 Running Rust tests..."
    cargo test --workspace --exclude pyrustor-python
    @echo "🧪 Running Python tests..."
    uv run python -m pytest tests/ -v

# Run tests with coverage
test-cov:
    @echo "🧪 Running tests with coverage..."
    uv run python -m pytest tests/ -v --cov=pyrustor --cov-report=html --cov-report=term-missing

# Run only fast tests (exclude benchmarks and slow tests)
test-fast:
    @echo "🧪 Running fast tests..."
    uv run python -m pytest tests/ -v -m "not benchmark and not slow"

# Run only benchmark tests
test-bench:
    @echo "⚡ Running benchmark tests..."
    uv run python -m pytest tests/ -v -m benchmark

# Run tests in parallel
test-parallel:
    @echo "🧪 Running tests in parallel..."
    uv run python -m pytest tests/ -v -n auto

# Run specific test file
test-file FILE:
    @echo "🧪 Running tests in {{FILE}}..."
    uv run python -m pytest {{FILE}} -v

# Run tests with specific marker
test-marker MARKER:
    @echo "🧪 Running tests with marker {{MARKER}}..."
    uv run python -m pytest tests/ -v -m {{MARKER}}

# Run coverage and open HTML report
test-cov-open: test-cov
    @echo "📊 Opening coverage report..."
    @if [ "$(uname)" = "Darwin" ]; then open htmlcov/index.html; elif [ "$(uname)" = "Linux" ]; then xdg-open htmlcov/index.html; else start htmlcov/index.html; fi

# Generate Python type stub files using pyo3-stubgen
stubs:
    @echo "📝 Generating type stubs with pyo3-stubgen..."
    uvx maturin develop
    uv run pyo3-stubgen pyrustor._pyrustor python/pyrustor/
    @echo "✅ Type stubs generated successfully"

# Format code
format:
    @echo "🎨 Formatting Rust code..."
    cargo fmt --all
    @echo "🎨 Formatting Python code..."
    uv run ruff format .

# Run linting
lint:
    @echo "🔍 Linting Rust code..."
    cargo clippy --all-targets --all-features -- -D warnings
    @echo "🔍 Linting Python code..."
    uv run ruff check .

# Fix linting issues automatically
fix:
    @echo "🔧 Fixing linting issues..."
    cargo clippy --fix --allow-dirty --allow-staged
    uv run ruff check --fix .

# Run all checks (format, lint, test)
check: format lint test
    @echo "✅ All checks passed!"

# Clean build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    cargo clean
    @echo "Cleaning Python artifacts..."
    python -c "import shutil, os; [shutil.rmtree(p, ignore_errors=True) for p in ['target', 'dist', 'python/pyrustor/__pycache__']]"

# Setup development environment
dev: install build stubs
    @echo "🚀 Development environment ready!"
    @echo "💡 Try: just test"

# Build release wheels for all platforms
release:
    @echo "📦 Building release wheels..."
    uvx maturin build --release
    @echo "🔍 Verifying wheel contents..."
    @powershell -Command "Get-ChildItem target/wheels/*.whl | ForEach-Object { python -m zipfile -l $_.FullName }"

# Build ABI3 wheels (compatible with Python 3.8+)
release-abi3:
    @echo "📦 Building ABI3 wheels..."
    uvx maturin build --release --features abi3
    @echo "🔍 Verifying wheel contents..."
    @powershell -Command "Get-ChildItem target/wheels/*.whl | ForEach-Object { python -m zipfile -l $_.FullName }"

# Test built wheel functionality
test-wheel:
    @echo "🧪 Testing built wheel..."
    uv pip install pyrustor --find-links target/wheels --force-reinstall
    python scripts/test_wheel_integrity.py
    @echo "🧪 Running pytest on installed wheel..."
    uv run python -m pytest tests/ -v --tb=short -m "not benchmark and not slow"

# Build and publish to PyPI (requires authentication)
publish: release
    @echo "🚀 Publishing to PyPI..."
    uvx maturin publish

# Run benchmarks
bench:
    @echo "⚡ Running benchmarks..."
    uv run python -m pytest tests/ -v -k benchmark

# Update dependencies
update:
    @echo "⬆️ Updating dependencies..."
    uv sync --upgrade

# Show project info
info:
    @echo "📊 Project Information:"
    @echo " Rust version: $(rustc --version)"
    @echo " Python version: $(python --version)"
    @echo " UV version: $(uv --version)"
    @echo " Maturin version: $(uvx maturin --version)"

# Run security audit
audit:
    @echo "🔒 Running security audit..."
    cargo audit

# Commitizen commands
commit:
    @echo "📝 Creating conventional commit..."
    uvx --from commitizen cz commit

bump:
    @echo "🚀 Bumping version with commitizen..."
    uvx --from commitizen cz bump

changelog:
    @echo "📋 Generating changelog..."
    uvx --from commitizen cz changelog

# Check version consistency across all files
check-version:
    @echo "🔍 Checking version consistency..."
    uv run python scripts/sync_versions.py --check-only

# Synchronize all version files with release-please manifest
sync-version:
    @echo "🔄 Synchronizing version files..."
    uv run python scripts/sync_versions.py

# Check commitizen version consistency
check-cz-version:
    @echo "🔍 Checking commitizen version consistency..."
    uvx --from commitizen cz check --rev-range HEAD~1..HEAD

# Verify stub files are included in wheel
verify-stubs:
    @echo "🔍 Verifying stub files in wheel..."
    uvx maturin build --release
    python -m zipfile -l target/wheels/*.whl | grep "\\.pyi"
    @echo "✅ Stub files verified in wheel package"

# Run examples
example EXAMPLE:
    @echo "🚀 Running example: {{EXAMPLE}}"
    uv run python examples/{{EXAMPLE}}.py

# Run all examples
examples:
    @echo "🚀 Running all examples..."
    @for example in examples/*.py; do echo "Running $example"; uv run python "$example"; done
