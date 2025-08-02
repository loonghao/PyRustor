#!/usr/bin/env python3
"""Extract version from Cargo.toml [workspace.package] section."""

import re
import sys
from pathlib import Path


def extract_cargo_version():
    """Extract version from Cargo.toml."""
    cargo_path = Path("Cargo.toml")
    if not cargo_path.exists():
        return None
    
    content = cargo_path.read_text()
    lines = content.split('\n')
    
    in_workspace_package = False
    for line in lines:
        line = line.strip()
        if line == '[workspace.package]':
            in_workspace_package = True
            continue
        elif line.startswith('[') and in_workspace_package:
            # Entered a new section
            break
        elif in_workspace_package and line.startswith('version'):
            # Extract version using regex
            match = re.search(r'"([^"]*)"', line)
            if match:
                return match.group(1)
    
    return None


if __name__ == "__main__":
    version = extract_cargo_version()
    if version:
        print(version)
    else:
        sys.exit(1)
