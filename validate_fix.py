#!/usr/bin/env python3
"""Validate that the GitHub Action fix works correctly."""

import subprocess
import sys
from pathlib import Path


def test_python_version_script():
    """Test the Python script for extracting Cargo.toml version."""
    try:
        # Test the new Python script
        cmd = ["python3", ".github/actions/sync-versions/extract_version.py"]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        if result.returncode != 0:
            print(f"❌ Python script failed: {result.stderr}")
            return False

        version = result.stdout.strip()
        if not version:
            print("❌ Python script returned empty version")
            return False

        print(f"✅ Python script extracted version: {version}")

        # Verify it matches expected format (semantic version)
        import re
        if not re.match(r'^\d+\.\d+\.\d+', version):
            print(f"❌ Invalid version format: {version}")
            return False

        return True

    except Exception as e:
        print(f"❌ Error testing Python script: {e}")
        return False


def test_python_version_extraction():
    """Test Python version extraction."""
    try:
        init_file = Path("python/pyrustor/__init__.py")
        if not init_file.exists():
            print("❌ Python __init__.py file not found")
            return False
        
        content = init_file.read_text()
        import re
        match = re.search(r'__version__ = "([^"]*)"', content)
        
        if not match:
            print("❌ Could not extract Python version")
            return False
        
        version = match.group(1)
        print(f"✅ Python version extracted: {version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Python version extraction: {e}")
        return False


def main():
    """Run validation tests."""
    print("🧪 Validating GitHub Action fix...")
    
    tests = [
        ("Python version script", test_python_version_script),
        ("Python version extraction", test_python_version_extraction),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if not test_func():
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validation tests passed!")
        print("✅ The GitHub Action fix should work correctly in CI")
        return 0
    else:
        print("\n❌ Some validation tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
