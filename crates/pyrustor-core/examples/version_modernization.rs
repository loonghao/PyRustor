//! Example: Modernizing pkg_resources version detection
//!
//! This example demonstrates how to use PyRustor to modernize
//! old pkg_resources version detection patterns to modern alternatives.

use pyrustor_core::{Parser, Refactor, Result};

fn main() -> Result<()> {
    println!("🔧 PyRustor Version Modernization Example");
    println!("==========================================\n");

    // Show the transformation concept
    show_transformation_concept();

    println!("✅ Example completed successfully!");
    println!("\n💡 To use PyRustor in your project:");
    println!("   1. Add pyrustor to your Cargo.toml");
    println!("   2. Use Parser to parse Python code");
    println!("   3. Use Refactor to apply transformations");
    println!("   4. Get the modernized code back");

    Ok(())
}

fn show_transformation_concept() {
    println!("📝 Transformation Concept");
    println!("-------------------------");

    let original = r#"
# BEFORE: Old pkg_resources pattern
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
"#;

    let modernized = r#"
# AFTER: Modern pattern
from xxx_pyharmony import get_package_version

__version__ = get_package_version(__name__)
"#;

    println!("🔴 BEFORE (old pkg_resources pattern):");
    println!("{}", original);

    println!("🟢 AFTER (modern pattern):");
    println!("{}", modernized);

    println!("🔄 What PyRustor does:");
    println!("  1. Parses the Python AST");
    println!("  2. Identifies pkg_resources imports");
    println!("  3. Replaces with modern alternatives");
    println!("  4. Simplifies the version detection logic");
    println!("  5. Removes unnecessary try-except blocks");
}

fn _example_basic_modernization() -> Result<()> {
    println!("📝 Example 1: Basic pkg_resources modernization");
    println!("------------------------------------------------");

    let original_code = r#"
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = "0.0.0-dev.1"

def get_version():
    return __version__
"#;

    println!("Original code:");
    println!("{}", original_code);

    // Parse the code
    let parser = Parser::new();
    let ast = parser.parse_string(original_code)?;

    println!("📊 Analysis:");
    println!("  - Statements: {}", ast.statement_count());
    println!("  - Functions: {}", ast.functions().len());
    println!("  - Imports: {}", ast.imports().len());

    // Show imports
    println!("  - Import details:");
    for import in ast.imports() {
        println!("    * {}", import);
    }

    // Create refactor instance and apply modernization
    let mut refactor = Refactor::new(ast);

    println!("\n🔄 Applying modernization...");
    refactor.modernize_pkg_resources_version("xxx_pyharmony", "get_package_version")?;

    // Show changes
    let changes = refactor.changes();
    println!("✨ Changes applied ({}):", changes.len());
    for (i, change) in changes.iter().enumerate() {
        println!("  {}. {}", i + 1, change.description);
    }

    println!("\n📋 Change summary:");
    println!("{}", refactor.change_summary());

    println!("{}", "=".repeat(60));
    Ok(())
}

fn _example_multiple_files() -> Result<()> {
    println!("\n📝 Example 2: Multiple files modernization");
    println!("-------------------------------------------");

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
            "utils.py",
            r#"
import sys
from pkg_resources import get_distribution

def get_package_info():
    try:
        dist = get_distribution("mypackage")
        return {
            "version": dist.version,
            "location": dist.location
        }
    except:
        return {"version": "unknown", "location": None}
"#,
        ),
        (
            "cli.py",
            r#"
import argparse
from pkg_resources import get_distribution, DistributionNotFound

def create_parser():
    parser = argparse.ArgumentParser()
    try:
        version = get_distribution(__name__).version
    except DistributionNotFound:
        version = "dev"
    parser.add_argument("--version", action="version", version=version)
    return parser
"#,
        ),
    ];

    let parser = Parser::new();
    let mut total_changes = 0;

    for (filename, code) in files {
        println!("\n📁 Processing: {}", filename);

        let ast = parser.parse_string(code)?;
        let mut refactor = Refactor::new(ast);

        // Apply modernization
        refactor.modernize_pkg_resources_version("xxx_pyharmony", "get_package_version")?;

        let changes = refactor.changes();
        total_changes += changes.len();

        println!("  ✅ Applied {} changes", changes.len());
        for change in changes {
            println!("    - {}", change.description);
        }
    }

    println!(
        "\n📊 Summary: {} total changes across {} files",
        total_changes, 3
    );
    println!("{}", "=".repeat(60));
    Ok(())
}

fn _example_custom_patterns() -> Result<()> {
    println!("\n📝 Example 3: Custom modernization patterns");
    println!("--------------------------------------------");

    let code_with_deprecated = r#"
import imp
import optparse
from ConfigParser import ConfigParser
import StringIO
from pkg_resources import get_distribution

class MyConfig:
    def __init__(self):
        self.parser = optparse.OptionParser()
        self.config = ConfigParser()
        self.buffer = StringIO.StringIO()
        
    def get_version(self):
        return get_distribution("mypackage").version
"#;

    println!("Code with deprecated imports:");
    println!("{}", code_with_deprecated);

    let parser = Parser::new();
    let ast = parser.parse_string(code_with_deprecated)?;
    let mut refactor = Refactor::new(ast);

    println!("\n🔄 Applying multiple modernization patterns...");

    // Apply different modernization strategies
    refactor.modernize_imports()?;
    refactor.modernize_pkg_resources_version("xxx_pyharmony", "get_package_version")?;
    refactor.modernize_syntax()?;

    let changes = refactor.changes();
    println!("✨ Total changes applied: {}", changes.len());

    // Group changes by type
    let mut import_changes = 0;
    let mut syntax_changes = 0;
    let mut other_changes = 0;

    for change in changes {
        if change.description.contains("import") {
            import_changes += 1;
        } else if change.description.contains("syntax") || change.description.contains("Modernized")
        {
            syntax_changes += 1;
        } else {
            other_changes += 1;
        }
    }

    println!("📊 Change breakdown:");
    println!("  - Import modernizations: {}", import_changes);
    println!("  - Syntax modernizations: {}", syntax_changes);
    println!("  - Other changes: {}", other_changes);

    println!("\n📋 Detailed changes:");
    for (i, change) in changes.iter().enumerate() {
        println!("  {}. {}", i + 1, change.description);
    }

    println!("\n📝 Final summary:");
    println!("{}", refactor.change_summary());

    println!("{}", "=".repeat(60));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_examples_run_without_error() {
        // Test that all examples can run without panicking
        assert!(_example_basic_modernization().is_ok());
        assert!(_example_multiple_files().is_ok());
        assert!(_example_custom_patterns().is_ok());
    }
}
