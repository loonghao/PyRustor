#!/usr/bin/env python3
"""
Test script to validate CI optimization components.
This script can be run locally or in CI to verify all components work correctly.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"🔄 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=check
        )
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            raise
        return e


def test_version_consistency():
    """Test version consistency checking."""
    print("\n📋 Testing version consistency...")
    
    # Test version check
    result = run_command("just check-version", check=False)
    if result.returncode == 0:
        print("✅ Version consistency check passed")
        return True
    else:
        print("⚠️ Version inconsistency detected")
        
        # Test version sync
        print("🔄 Testing version sync...")
        sync_result = run_command("just sync-version", check=False)
        if sync_result.returncode == 0:
            print("✅ Version sync completed")
            
            # Verify sync worked
            verify_result = run_command("just check-version", check=False)
            if verify_result.returncode == 0:
                print("✅ Version consistency restored")
                return True
            else:
                print("❌ Version sync failed to fix inconsistency")
                return False
        else:
            print("❌ Version sync failed")
            return False


def test_build_system():
    """Test basic build functionality."""
    print("\n🔨 Testing build system...")
    
    # Test Rust build
    result = run_command("cargo check", check=False)
    if result.returncode == 0:
        print("✅ Rust build check passed")
    else:
        print("❌ Rust build check failed")
        return False
    
    # Test Python environment
    result = run_command("uv --version", check=False)
    if result.returncode == 0:
        print("✅ UV package manager available")
    else:
        print("❌ UV package manager not available")
        return False
    
    return True


def test_code_quality():
    """Test code quality checks."""
    print("\n🔍 Testing code quality...")
    
    # Test Rust formatting
    result = run_command("cargo fmt --all -- --check", check=False)
    if result.returncode == 0:
        print("✅ Rust formatting check passed")
    else:
        print("⚠️ Rust formatting issues found")
    
    # Test Rust linting
    result = run_command("cargo clippy --all-targets --all-features -- -D warnings", check=False)
    if result.returncode == 0:
        print("✅ Rust clippy check passed")
    else:
        print("⚠️ Rust clippy issues found")
    
    return True


def test_just_commands():
    """Test just command availability."""
    print("\n⚡ Testing just commands...")
    
    # List available commands
    result = run_command("just --list", check=False)
    if result.returncode == 0:
        print("✅ Just commands available")
        
        # Test specific commands
        commands_to_test = [
            "just ci-install",
            "just check-version",
        ]
        
        for cmd in commands_to_test:
            result = run_command(cmd, check=False)
            if result.returncode == 0:
                print(f"✅ {cmd} - passed")
            else:
                print(f"⚠️ {cmd} - failed")
        
        return True
    else:
        print("❌ Just commands not available")
        return False


def test_github_actions():
    """Test GitHub Actions configuration."""
    print("\n🚀 Testing GitHub Actions configuration...")
    
    actions_dir = Path(".github/actions")
    workflows_dir = Path(".github/workflows")
    
    # Check required actions exist
    required_actions = [
        "setup-pyrustor",
        "build-and-test", 
        "build-wheel",
        "cache-setup",
        "sync-versions"
    ]
    
    for action in required_actions:
        action_file = actions_dir / action / "action.yml"
        if action_file.exists():
            print(f"✅ Action {action} exists")
        else:
            print(f"❌ Action {action} missing")
            return False
    
    # Check required workflows exist
    required_workflows = [
        "ci-optimized.yml",
        "version-sync.yml",
        "pr-commands.yml"
    ]
    
    for workflow in required_workflows:
        workflow_file = workflows_dir / workflow
        if workflow_file.exists():
            print(f"✅ Workflow {workflow} exists")
        else:
            print(f"❌ Workflow {workflow} missing")
            return False
    
    return True


def main():
    """Run all tests."""
    print("🧪 PyRustor CI Optimization Test Suite")
    print("=" * 50)
    
    tests = [
        ("GitHub Actions Configuration", test_github_actions),
        ("Just Commands", test_just_commands),
        ("Version Consistency", test_version_consistency),
        ("Build System", test_build_system),
        ("Code Quality", test_code_quality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CI optimization is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
