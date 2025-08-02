#!/usr/bin/env python3
"""
Auto Version Management Demo for PyRustor

This script demonstrates how the automatic version management works with release-please.
It shows the complete workflow from commit to release.

Usage:
    python scripts/auto_version_demo.py
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd, capture_output=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=capture_output, text=True, check=True
        )
        return result.stdout.strip() if capture_output else ""
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None


def get_current_versions():
    """Get current versions from all files."""
    versions = {}
    
    # Release-please manifest
    try:
        with open(".release-please-manifest.json") as f:
            manifest = json.load(f)
        versions["release-please"] = manifest["."]
    except Exception as e:
        versions["release-please"] = f"Error: {e}"
    
    # Cargo.toml
    try:
        with open("Cargo.toml") as f:
            content = f.read()
        import re
        match = re.search(r'\[workspace\.package\].*?version\s*=\s*"([^"]+)"', content, re.DOTALL)
        versions["cargo"] = match.group(1) if match else "Not found"
    except Exception as e:
        versions["cargo"] = f"Error: {e}"
    
    # Python package
    try:
        with open("python/pyrustor/__init__.py") as f:
            content = f.read()
        import re
        match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
        versions["python"] = match.group(1) if match else "Not found"
    except Exception as e:
        versions["python"] = f"Error: {e}"
    
    return versions


def show_workflow_explanation():
    """Show explanation of the auto version workflow."""
    print("🚀 PyRustor Auto Version Management Workflow")
    print("=" * 50)
    print()
    print("📝 How it works:")
    print("1. Developers use conventional commits (feat:, fix:, etc.)")
    print("2. release-please analyzes commit history")
    print("3. Automatically determines version bump (patch/minor/major)")
    print("4. Creates release PR with updated versions")
    print("5. When merged, triggers automatic release")
    print()
    print("🔧 Conventional Commit Examples:")
    print("  feat: add new parsing feature        → minor version bump")
    print("  fix: resolve memory leak             → patch version bump")
    print("  feat!: breaking API change          → major version bump")
    print("  docs: update README                 → no version bump")
    print()
    print("📁 Files automatically updated:")
    print("  ✅ .release-please-manifest.json")
    print("  ✅ Cargo.toml (workspace.package.version)")
    print("  ✅ python/pyrustor/__init__.py (__version__)")
    print("  ✅ CHANGELOG.md")
    print()


def show_current_status():
    """Show current version status."""
    print("📊 Current Version Status:")
    print("-" * 30)
    
    versions = get_current_versions()
    
    for source, version in versions.items():
        print(f"  {source:15}: {version}")
    
    # Check if versions are in sync
    version_values = [v for v in versions.values() if not v.startswith("Error")]
    if len(set(version_values)) == 1:
        print(f"\n✅ All versions are synchronized: {version_values[0]}")
    else:
        print(f"\n⚠️  Version mismatch detected!")
        print("💡 This will be automatically fixed by release-please on next release")
    print()


def show_next_steps():
    """Show next steps for developers."""
    print("🎯 Next Steps for Auto Version Management:")
    print("-" * 40)
    print()
    print("1. 📝 Make your changes and commit with conventional commits:")
    print("   git commit -m 'feat: add awesome new feature'")
    print()
    print("2. 🚀 Push to main branch:")
    print("   git push origin main")
    print()
    print("3. 🤖 release-please automatically:")
    print("   - Analyzes your commits")
    print("   - Determines version bump")
    print("   - Creates release PR")
    print()
    print("4. ✅ Review and merge the release PR")
    print()
    print("5. 🎉 Automatic release is triggered!")
    print()
    print("🔍 Monitor release status:")
    print("   - Check GitHub Actions for release-please workflow")
    print("   - Look for release PR in pull requests")
    print("   - Verify release in GitHub releases page")
    print()


def check_git_status():
    """Check if there are uncommitted changes."""
    status = run_command("git status --porcelain")
    if status:
        print("⚠️  You have uncommitted changes:")
        print(status)
        print("\n💡 Commit your changes first for proper version tracking")
        return False
    return True


def main():
    """Main demo function."""
    print()
    show_workflow_explanation()
    show_current_status()
    
    if not check_git_status():
        print()
    
    show_next_steps()
    
    print("🔗 Useful Commands:")
    print("   python scripts/sync_versions.py --check-only  # Check version status")
    print("   git log --oneline -10                         # See recent commits")
    print("   gh pr list                                    # See open PRs")
    print()


if __name__ == "__main__":
    main()
