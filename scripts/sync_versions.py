#!/usr/bin/env python3
"""
Version synchronization script for PyRustor.

This script ensures all version files are synchronized with the release-please manifest.
It updates:
- Cargo.toml (workspace version)
- python/pyrustor/__init__.py (__version__)

Usage:
    python scripts/sync_versions.py [--check-only]

    --check-only: Only check if versions are synchronized, don't update
"""

import json
import sys
import argparse
from pathlib import Path
import re


def get_release_please_version():
    """Get version from release-please manifest."""
    manifest_path = Path(".release-please-manifest.json")
    if not manifest_path.exists():
        raise FileNotFoundError("Release-please manifest not found")

    with open(manifest_path) as f:
        manifest = json.load(f)

    return manifest["."]


def update_release_please_version(new_version):
    """Update version in release-please manifest."""
    manifest_path = Path(".release-please-manifest.json")

    with open(manifest_path) as f:
        manifest = json.load(f)

    manifest["."] = new_version

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        f.write('\n')  # Add trailing newline

    print(f"✅ Updated release-please manifest version to {new_version}")


def get_cargo_version():
    """Get version from Cargo.toml."""
    cargo_path = Path("Cargo.toml")
    if not cargo_path.exists():
        raise FileNotFoundError("Cargo.toml not found")
    
    with open(cargo_path) as f:
        content = f.read()
    
    # Find workspace.package.version - allow for content between [workspace.package] and version
    match = re.search(r'\[workspace\.package\].*?version\s*=\s*"([^"]+)"', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find workspace.package.version in Cargo.toml")
    
    return match.group(1)


def get_python_version():
    """Get version from Python package."""
    init_path = Path("python/pyrustor/__init__.py")
    if not init_path.exists():
        raise FileNotFoundError("Python __init__.py not found")
    
    with open(init_path) as f:
        content = f.read()
    
    # Find __version__ = "..."
    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find __version__ in __init__.py")
    
    return match.group(1)


def update_cargo_version(new_version):
    """Update version in Cargo.toml."""
    cargo_path = Path("Cargo.toml")
    
    with open(cargo_path) as f:
        content = f.read()
    
    # Replace workspace.package.version - allow for content between [workspace.package] and version
    new_content = re.sub(
        r'(\[workspace\.package\].*?version\s*=\s*)"[^"]+"',
        rf'\1"{new_version}"',
        content,
        flags=re.DOTALL
    )
    
    if new_content == content:
        raise ValueError("Could not update version in Cargo.toml")
    
    with open(cargo_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated Cargo.toml version to {new_version}")


def update_python_version(new_version):
    """Update version in Python package."""
    init_path = Path("python/pyrustor/__init__.py")
    
    with open(init_path) as f:
        content = f.read()
    
    # Replace __version__ = "..."
    new_content = re.sub(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    if new_content == content:
        raise ValueError("Could not update version in __init__.py")
    
    with open(init_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Updated Python package version to {new_version}")


def check_versions():
    """Check if all versions are synchronized."""
    try:
        release_version = get_release_please_version()
        cargo_version = get_cargo_version()
        python_version = get_python_version()

        print(f"📋 Version Status:")
        print(f"  Release-please: {release_version}")
        print(f"  Cargo.toml:     {cargo_version}")
        print(f"  Python package: {python_version}")

        if release_version == cargo_version == python_version:
            print(f"✅ All versions are synchronized: {release_version}")
            return True, release_version
        else:
            print("❌ Version mismatch detected!")
            print("💡 Note: release-please will auto-update versions on next release")
            return False, release_version

    except Exception as e:
        print(f"❌ Error checking versions: {e}")
        return False, None


def sync_versions():
    """Synchronize all versions with release-please manifest."""
    try:
        release_version = get_release_please_version()
        cargo_version = get_cargo_version()
        python_version = get_python_version()
        
        print(f"🔄 Synchronizing versions to {release_version}...")
        
        # Update Cargo.toml if needed
        if cargo_version != release_version:
            update_cargo_version(release_version)
        else:
            print(f"✅ Cargo.toml version already correct: {cargo_version}")
        
        # Update Python package if needed
        if python_version != release_version:
            update_python_version(release_version)
        else:
            print(f"✅ Python package version already correct: {python_version}")
        
        print(f"🎉 All versions synchronized to {release_version}")
        return True
        
    except Exception as e:
        print(f"❌ Error synchronizing versions: {e}")
        return False


def main():
    """Main function for version synchronization."""
    parser = argparse.ArgumentParser(description="Synchronize PyRustor version files")
    parser.add_argument(
        "--check-only", 
        action="store_true", 
        help="Only check if versions are synchronized, don't update"
    )
    
    args = parser.parse_args()
    
    if args.check_only:
        is_synced, _ = check_versions()
        sys.exit(0 if is_synced else 1)
    else:
        # First check current status
        is_synced, target_version = check_versions()
        
        if is_synced:
            print("🎉 All versions are already synchronized!")
            sys.exit(0)
        else:
            # Attempt to synchronize
            if sync_versions():
                print("🎉 Version synchronization completed successfully!")
                sys.exit(0)
            else:
                print("❌ Version synchronization failed!")
                sys.exit(1)


if __name__ == "__main__":
    main()
