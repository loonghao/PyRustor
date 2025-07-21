//! Test for version import refactoring
//!
//! This test verifies that we can refactor old pkg_resources version detection
//! to modern package version utilities.

use pyrustor_core::{Parser, Refactor, Result};

#[test]
fn test_pkg_resources_to_modern_version_refactor() -> Result<()> {
    // Original code using pkg_resources
    let original_code = r#"
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = "0.0.0-dev.1"
"#;

    // Parse the original code
    let parser = Parser::new();
    let ast = parser.parse_string(original_code)?;

    // Verify we parsed the imports correctly
    let imports = ast.imports();
    println!("Found {} imports:", imports.len());
    for import in &imports {
        println!("  - {}", import);
    }

    // Should find the pkg_resources imports
    let pkg_resources_imports: Vec<_> = imports
        .iter()
        .filter(|imp| {
            imp.from_module
                .as_ref()
                .is_some_and(|m| m == "pkg_resources")
        })
        .collect();

    assert_eq!(
        pkg_resources_imports.len(),
        2,
        "Should find 2 pkg_resources imports"
    );

    // Verify specific imports
    let distribution_not_found = imports
        .iter()
        .find(|imp| imp.module == "DistributionNotFound")
        .expect("Should find DistributionNotFound import");
    assert!(distribution_not_found.is_from_import);
    assert_eq!(
        distribution_not_found.from_module.as_ref().unwrap(),
        "pkg_resources"
    );

    let get_distribution = imports
        .iter()
        .find(|imp| imp.module == "get_distribution")
        .expect("Should find get_distribution import");
    assert!(get_distribution.is_from_import);
    assert_eq!(
        get_distribution.from_module.as_ref().unwrap(),
        "pkg_resources"
    );

    // Create refactor instance
    let mut refactor = Refactor::new(ast);

    // Apply refactoring transformations
    // 1. Replace pkg_resources imports with modern alternative
    refactor.replace_import("pkg_resources", "xxx_pyharmony")?;

    // 2. Apply custom transformation for the version detection pattern
    refactor.apply_custom_transform(
        "Replace pkg_resources version detection with modern approach",
        |_ast| {
            // In a real implementation, this would:
            // 1. Find the try-except block
            // 2. Replace it with a simple function call
            // 3. Remove the DistributionNotFound import
            // 4. Add the new import for get_package_version

            // For now, this is a placeholder that represents the transformation
            Ok(())
        },
    )?;

    // Verify changes were recorded
    let changes = refactor.changes();
    assert!(
        changes.len() >= 2,
        "Should have at least 2 changes recorded"
    );

    // Check change descriptions
    let change_descriptions: Vec<_> = changes.iter().map(|c| &c.description).collect();

    println!("Refactoring changes:");
    for desc in &change_descriptions {
        println!("  - {}", desc);
    }

    // Should have import replacement
    assert!(change_descriptions
        .iter()
        .any(|desc| desc.contains("import")));

    // Should have custom transformation
    assert!(change_descriptions
        .iter()
        .any(|desc| desc.contains("pkg_resources version detection")));

    Ok(())
}

#[test]
fn test_version_pattern_detection() -> Result<()> {
    // Test various version detection patterns
    let test_cases = [
        // Case 1: Basic pkg_resources pattern
        r#"
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0"
"#,
        // Case 2: With package name
        r#"
from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution("mypackage").version
except DistributionNotFound:
    __version__ = "unknown"
"#,
        // Case 3: Different variable name
        r#"
from pkg_resources import get_distribution, DistributionNotFound
try:
    VERSION = get_distribution(__name__).version
except DistributionNotFound:
    VERSION = "dev"
"#,
    ];

    let parser = Parser::new();

    for (i, code) in test_cases.iter().enumerate() {
        println!("Testing case {}", i + 1);

        let ast = parser.parse_string(code)?;
        let imports = ast.imports();

        // Each case should have pkg_resources imports
        let pkg_imports: Vec<_> = imports
            .iter()
            .filter(|imp| {
                imp.from_module
                    .as_ref()
                    .is_some_and(|m| m == "pkg_resources")
            })
            .collect();

        assert!(
            !pkg_imports.is_empty(),
            "Case {} should have pkg_resources imports",
            i + 1
        );

        // Should be able to create refactor instance
        let mut refactor = Refactor::new(ast);

        // Apply the same refactoring pattern
        refactor.replace_import("pkg_resources", "xxx_pyharmony")?;

        let changes = refactor.changes();
        assert!(!changes.is_empty(), "Case {} should have changes", i + 1);
    }

    Ok(())
}

#[test]
fn test_modern_version_import_pattern() -> Result<()> {
    // Test that we can parse the target modern pattern
    let modern_code = r#"
from xxx_pyharmony import get_package_version

__version__ = get_package_version(__name__)
"#;

    let parser = Parser::new();
    let ast = parser.parse_string(modern_code)?;

    // Verify the modern import is parsed correctly
    let imports = ast.imports();
    assert_eq!(imports.len(), 1);

    let modern_import = &imports[0];
    assert_eq!(modern_import.module, "get_package_version");
    assert!(modern_import.is_from_import);
    assert_eq!(modern_import.from_module.as_ref().unwrap(), "xxx_pyharmony");
    assert!(modern_import.alias.is_none());

    // Verify we have the right number of statements
    assert!(ast.statement_count() >= 2); // import + assignment

    Ok(())
}

#[test]
fn test_complex_version_refactor_workflow() -> Result<()> {
    // Test a more complex scenario with multiple files
    let files = vec![
        (
            "__init__.py",
            r#"
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"

from .core import main_function
"#,
        ),
        (
            "core.py",
            r#"
import sys
from pkg_resources import get_distribution

def get_version():
    try:
        return get_distribution("mypackage").version
    except:
        return "unknown"

def main_function():
    print(f"Version: {get_version()}")
"#,
        ),
    ];

    let parser = Parser::new();

    for (filename, code) in files {
        println!("Processing {}", filename);

        let ast = parser.parse_string(code)?;
        let mut refactor = Refactor::new(ast);

        // Apply consistent refactoring across all files
        refactor.replace_import("pkg_resources", "xxx_pyharmony")?;

        // Add custom transformation for version detection
        refactor.apply_custom_transform(
            &format!("Modernize version detection in {}", filename),
            |_ast| {
                // This would implement the actual AST transformation
                Ok(())
            },
        )?;

        let changes = refactor.changes();
        println!("  Applied {} changes to {}", changes.len(), filename);

        // Each file should have at least one change
        assert!(!changes.is_empty());
    }

    Ok(())
}

#[test]
fn test_modernize_pkg_resources_version_method() -> Result<()> {
    // Test the new dedicated method for pkg_resources modernization
    let original_code = r#"
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
"#;

    let parser = Parser::new();
    let ast = parser.parse_string(original_code)?;
    let mut refactor = Refactor::new(ast);

    // Use the new dedicated method
    refactor.modernize_pkg_resources_version("xxx_pyharmony", "get_package_version")?;

    let changes = refactor.changes();
    println!("Changes made:");
    for change in changes {
        println!("  - {}", change.description);
    }

    // Should have multiple changes:
    // 1. Import replacement
    // 2. Syntax modernization
    // 3. Summary change
    assert!(changes.len() >= 2);

    // Check that we have the right types of changes
    let has_import_change = changes.iter().any(|c| c.description.contains("import"));
    let has_modernization = changes
        .iter()
        .any(|c| c.description.contains("Modernized version detection"));

    assert!(has_import_change, "Should have import replacement change");
    assert!(
        has_modernization,
        "Should have version detection modernization"
    );

    Ok(())
}

#[test]
fn test_modernize_imports_method() -> Result<()> {
    // Test the modernize_imports method with deprecated modules
    let code_with_deprecated = r#"
import imp
import optparse
from ConfigParser import ConfigParser
import StringIO
"#;

    let parser = Parser::new();
    let ast = parser.parse_string(code_with_deprecated)?;
    let mut refactor = Refactor::new(ast);

    // Apply import modernization
    refactor.modernize_imports()?;

    let changes = refactor.changes();
    println!("Import modernization changes:");
    for change in changes {
        println!("  - {}", change.description);
    }

    // Should have changes for the deprecated imports
    assert!(!changes.is_empty());

    // Should mention deprecated imports
    let has_deprecated_change = changes
        .iter()
        .any(|c| c.description.contains("deprecated") || c.description.contains("import"));
    assert!(has_deprecated_change);

    Ok(())
}

#[test]
fn test_no_changes_when_no_pkg_resources() -> Result<()> {
    // Test that the method doesn't make changes when there are no pkg_resources imports
    let modern_code = r#"
from xxx_pyharmony import get_package_version

__version__ = get_package_version(__name__)
"#;

    let parser = Parser::new();
    let ast = parser.parse_string(modern_code)?;
    let mut refactor = Refactor::new(ast);

    // Try to modernize (should do nothing)
    refactor.modernize_pkg_resources_version("xxx_pyharmony", "get_package_version")?;

    let changes = refactor.changes();

    // Should have no changes since the code is already modern
    assert_eq!(
        changes.len(),
        0,
        "Should not make changes to already modern code"
    );

    Ok(())
}

#[test]
fn test_edge_cases() -> Result<()> {
    // Test edge cases and error conditions

    // Case 1: No pkg_resources imports (should not change anything)
    let no_pkg_resources = r#"
import os
import sys

__version__ = "1.0.0"
"#;

    let parser = Parser::new();
    let ast = parser.parse_string(no_pkg_resources)?;
    let mut refactor = Refactor::new(ast);

    // This should not make any changes
    refactor.replace_import("pkg_resources", "xxx_pyharmony")?;

    let changes = refactor.changes();
    // Should have no changes since there are no pkg_resources imports
    assert_eq!(changes.len(), 0);

    // Case 2: Already modern pattern (should not need changes)
    let already_modern = r#"
from xxx_pyharmony import get_package_version

__version__ = get_package_version(__name__)
"#;

    let ast = parser.parse_string(already_modern)?;
    let imports = ast.imports();

    // Should already have the modern import
    let modern_import = imports
        .iter()
        .find(|imp| imp.module == "get_package_version")
        .expect("Should find get_package_version import");

    assert_eq!(modern_import.from_module.as_ref().unwrap(), "xxx_pyharmony");

    Ok(())
}
