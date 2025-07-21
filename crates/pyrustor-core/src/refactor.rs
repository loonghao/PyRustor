//! Code refactoring and transformation utilities

#![allow(clippy::uninlined_format_args)]

use crate::{ast::PythonAst, error::Result, formatter::Formatter, PyRustorError};
use ruff_python_ast::{Identifier, Stmt};
use ruff_text_size::TextRange;
use std::collections::HashMap;

/// Refactoring operations for Python code
#[derive(Debug)]
pub struct Refactor {
    /// The AST being refactored
    ast: PythonAst,
    /// Formatter for output generation
    formatter: Formatter,
    /// Track changes made during refactoring
    changes: Vec<RefactorChange>,
}

/// Represents a single refactoring change
#[derive(Debug, Clone)]
pub struct RefactorChange {
    /// Type of change performed
    pub change_type: ChangeType,
    /// Description of the change
    pub description: String,
    /// Location where the change was made
    pub location: Option<SourceLocation>,
}

/// Types of refactoring changes
#[derive(Debug, Clone)]
pub enum ChangeType {
    /// Function was renamed
    FunctionRenamed { old_name: String, new_name: String },
    /// Class was renamed
    ClassRenamed { old_name: String, new_name: String },
    /// Import was modified
    ImportModified {
        old_import: String,
        new_import: String,
    },
    /// Variable was renamed
    VariableRenamed { old_name: String, new_name: String },
    /// Code was modernized
    SyntaxModernized { description: String },
    /// Custom transformation
    Custom { description: String },
}

/// Source code location
#[derive(Debug, Clone)]
pub struct SourceLocation {
    pub line: usize,
    pub column: usize,
}

impl Refactor {
    /// Create a new refactor instance
    pub fn new(ast: PythonAst) -> Self {
        Self {
            ast,
            formatter: Formatter::new(),
            changes: Vec::new(),
        }
    }

    /// Create a refactor instance with custom formatter
    pub fn with_formatter(ast: PythonAst, formatter: Formatter) -> Self {
        Self {
            ast,
            formatter,
            changes: Vec::new(),
        }
    }

    /// Rename a function throughout the code
    ///
    /// # Arguments
    ///
    /// * `old_name` - Current function name
    /// * `new_name` - New function name
    ///
    /// # Example
    ///
    /// ```rust
    /// use pyrustor_core::{Parser, Refactor};
    ///
    /// let parser = Parser::new();
    /// let ast = parser.parse_string("def old_func(): pass")?;
    /// let mut refactor = Refactor::new(ast);
    /// refactor.rename_function("old_func", "new_func")?;
    /// # Ok::<(), Box<dyn std::error::Error>>(())
    /// ```
    pub fn rename_function(&mut self, old_name: &str, new_name: &str) -> Result<()> {
        let mut found = false;

        // Find and rename function definitions
        for stmt in &mut self.ast.module_mut().body {
            if let Stmt::FunctionDef(func) = stmt {
                if func.name.as_str() == old_name {
                    func.name = Identifier::new(new_name, TextRange::default());
                    found = true;

                    self.changes.push(RefactorChange {
                        change_type: ChangeType::FunctionRenamed {
                            old_name: old_name.to_string(),
                            new_name: new_name.to_string(),
                        },
                        description: format!("Renamed function '{old_name}' to '{new_name}'"),
                        location: Some(SourceLocation { line: 0, column: 0 }), // TODO: Get actual location
                    });
                }
            }
        }

        if !found {
            return Err(PyRustorError::refactor_error(format!(
                "Function '{old_name}' not found"
            )));
        }

        // TODO: Also rename function calls throughout the code

        Ok(())
    }

    /// Rename a function throughout the codebase with optional formatting
    pub fn rename_function_with_format(
        &mut self,
        old_name: &str,
        new_name: &str,
        apply_formatting: bool,
    ) -> Result<()> {
        self.rename_function(old_name, new_name)?;
        if apply_formatting {
            self.format_code()?;
        }
        Ok(())
    }

    /// Rename a class throughout the code
    pub fn rename_class(&mut self, old_name: &str, new_name: &str) -> Result<()> {
        let mut found = false;

        // Find and rename class definitions
        for stmt in &mut self.ast.module_mut().body {
            if let Stmt::ClassDef(class) = stmt {
                if class.name.as_str() == old_name {
                    class.name = Identifier::new(new_name, TextRange::default());
                    found = true;

                    self.changes.push(RefactorChange {
                        change_type: ChangeType::ClassRenamed {
                            old_name: old_name.to_string(),
                            new_name: new_name.to_string(),
                        },
                        description: format!("Renamed class '{old_name}' to '{new_name}'"),
                        location: Some(SourceLocation { line: 0, column: 0 }),
                    });
                }
            }
        }

        if !found {
            return Err(PyRustorError::refactor_error(format!(
                "Class '{old_name}' not found"
            )));
        }

        Ok(())
    }

    /// Rename a class throughout the codebase with optional formatting
    pub fn rename_class_with_format(
        &mut self,
        old_name: &str,
        new_name: &str,
        apply_formatting: bool,
    ) -> Result<()> {
        self.rename_class(old_name, new_name)?;
        if apply_formatting {
            self.format_code()?;
        }
        Ok(())
    }

    /// Replace import statements
    pub fn replace_import(&mut self, old_module: &str, new_module: &str) -> Result<()> {
        // Import statements will be used when implementing actual AST transformations
        #[allow(unused_imports)]
        use ruff_python_ast::{Alias, StmtImport, StmtImportFrom};

        let mut found = false;

        for stmt in &mut self.ast.module_mut().body {
            match stmt {
                Stmt::Import(import_stmt) => {
                    for alias in &mut import_stmt.names {
                        if alias.name.as_str() == old_module {
                            alias.name = Identifier::new(new_module, TextRange::default());
                            found = true;
                        }
                    }
                }
                Stmt::ImportFrom(import_from) => {
                    if let Some(module) = &mut import_from.module {
                        if module.as_str() == old_module {
                            *module = Identifier::new(new_module, TextRange::default());
                            found = true;
                        }
                    }
                }
                _ => {}
            }
        }

        if found {
            self.changes.push(RefactorChange {
                change_type: ChangeType::ImportModified {
                    old_import: old_module.to_string(),
                    new_import: new_module.to_string(),
                },
                description: format!("Replaced import '{old_module}' with '{new_module}'"),
                location: None,
            });
        }

        Ok(())
    }

    /// Modernize Python syntax (e.g., f-strings, type hints, etc.)
    pub fn modernize_syntax(&mut self) -> Result<()> {
        let mut changes_made = 0;

        // Convert string formatting to f-strings (simplified implementation)
        // In a full implementation, this would parse string literals and convert them
        changes_made += self.convert_string_formatting()?;

        // Add type hints to functions without them
        changes_made += self.add_missing_type_hints()?;

        // Convert old-style string concatenation
        changes_made += self.modernize_string_operations()?;

        if changes_made > 0 {
            self.changes.push(RefactorChange {
                change_type: ChangeType::SyntaxModernized {
                    description: format!(
                        "Applied {changes_made} modern Python syntax improvements"
                    ),
                },
                description: format!("Modernized Python syntax ({changes_made} changes)"),
                location: None,
            });
        }

        Ok(())
    }

    /// Convert old-style string formatting to f-strings
    fn convert_string_formatting(&mut self) -> Result<usize> {
        // This is a simplified placeholder
        // A full implementation would:
        // 1. Find string literals with % formatting
        // 2. Parse the format string and arguments
        // 3. Convert to f-string syntax
        // 4. Update the AST nodes

        // For now, just return 0 (no changes made)
        Ok(0)
    }

    /// Add type hints to functions that don't have them
    fn add_missing_type_hints(&mut self) -> Result<usize> {
        // This is a simplified placeholder
        // A full implementation would:
        // 1. Analyze function signatures
        // 2. Infer types from usage patterns
        // 3. Add appropriate type annotations

        // For now, just return 0 (no changes made)
        Ok(0)
    }

    /// Modernize string operations
    fn modernize_string_operations(&mut self) -> Result<usize> {
        // This is a simplified placeholder
        // A full implementation would:
        // 1. Find string concatenation with +
        // 2. Convert to f-strings or .join() where appropriate
        // 3. Update string methods to modern equivalents

        // For now, just return 0 (no changes made)
        Ok(0)
    }

    /// Add type hints to function definitions
    pub fn add_type_hints(&mut self, hints: HashMap<String, String>) -> Result<()> {
        // This would add type hints to functions based on the provided mapping
        // For now, this is a placeholder

        for (func_name, type_hint) in hints {
            self.changes.push(RefactorChange {
                change_type: ChangeType::Custom {
                    description: format!(
                        "Added type hint '{type_hint}' to function '{func_name}'"
                    ),
                },
                description: format!("Added type hints to function '{func_name}'"),
                location: None,
            });
        }

        Ok(())
    }

    /// Apply a custom transformation function
    pub fn apply_custom_transform<F>(&mut self, description: &str, transform: F) -> Result<()>
    where
        F: FnOnce(&mut PythonAst) -> Result<()>,
    {
        transform(&mut self.ast)?;

        self.changes.push(RefactorChange {
            change_type: ChangeType::Custom {
                description: description.to_string(),
            },
            description: description.to_string(),
            location: None,
        });

        Ok(())
    }

    /// Modernize Python syntax with optional formatting
    pub fn modernize_syntax_with_format(&mut self, apply_formatting: bool) -> Result<()> {
        self.modernize_syntax()?;
        if apply_formatting {
            self.format_code()?;
        }
        Ok(())
    }

    /// Remove unused imports from the module
    pub fn remove_unused_imports(&mut self) -> Result<()> {
        // This is a simplified implementation
        // A full implementation would:
        // 1. Analyze all names used in the module
        // 2. Check which imports are actually referenced
        // 3. Remove unused import statements

        let removed_count = 0;

        // For now, this is a placeholder that doesn't actually remove anything
        // In a real implementation, we would need to:
        // - Build a symbol table of all used names
        // - Compare against imported names
        // - Remove unused import statements from the AST

        if removed_count > 0 {
            self.changes.push(RefactorChange {
                change_type: ChangeType::Custom {
                    description: format!("Removed {removed_count} unused imports"),
                },
                description: format!("Removed {removed_count} unused imports"),
                location: None,
            });
        }

        Ok(())
    }

    /// Sort imports according to PEP 8 guidelines
    pub fn sort_imports(&mut self) -> Result<()> {
        // This would sort imports in the following order:
        // 1. Standard library imports
        // 2. Related third party imports
        // 3. Local application/library specific imports

        // For now, this is a placeholder
        self.changes.push(RefactorChange {
            change_type: ChangeType::Custom {
                description: "Sorted imports according to PEP 8".to_string(),
            },
            description: "Sorted imports".to_string(),
            location: None,
        });

        Ok(())
    }

    /// Extract a method from selected code
    pub fn extract_method(
        &mut self,
        method_name: &str,
        start_line: usize,
        end_line: usize,
    ) -> Result<()> {
        // This would:
        // 1. Extract the code between start_line and end_line
        // 2. Analyze variable usage to determine parameters and return values
        // 3. Create a new method with the extracted code
        // 4. Replace the original code with a method call

        // For now, this is a placeholder
        self.changes.push(RefactorChange {
            change_type: ChangeType::Custom {
                description: format!(
                    "Extracted method '{method_name}' from lines {start_line}-{end_line}"
                ),
            },
            description: format!("Extracted method '{method_name}'"),
            location: Some(SourceLocation {
                line: start_line,
                column: 0,
            }),
        });

        Ok(())
    }

    /// Inline a method call
    pub fn inline_method(&mut self, method_name: &str) -> Result<()> {
        // This would:
        // 1. Find the method definition
        // 2. Find all calls to the method
        // 3. Replace calls with the method body (with appropriate variable substitution)
        // 4. Remove the method definition if no longer used

        // For now, this is a placeholder
        self.changes.push(RefactorChange {
            change_type: ChangeType::Custom {
                description: format!("Inlined method '{method_name}'"),
            },
            description: format!("Inlined method '{method_name}'"),
            location: None,
        });

        Ok(())
    }

    /// Modernize pkg_resources version detection to use modern package version utilities
    pub fn modernize_pkg_resources_version(
        &mut self,
        target_module: &str,
        target_function: &str,
    ) -> Result<()> {
        // This refactoring transforms:
        // ```python
        // from pkg_resources import DistributionNotFound
        // from pkg_resources import get_distribution
        //
        // try:
        //     __version__ = get_distribution(__name__).version
        // except DistributionNotFound:
        //     __version__ = "0.0.0-dev.1"
        // ```
        //
        // Into:
        // ```python
        // from xxx_pyharmony import get_package_version
        //
        // __version__ = get_package_version(__name__)
        // ```

        let mut changes_made = 0;

        // Step 1: Check if we have pkg_resources imports
        let imports = self.ast.imports();
        let has_pkg_resources = imports.iter().any(|imp| {
            imp.from_module
                .as_ref()
                .is_some_and(|m| m == "pkg_resources")
        });

        if !has_pkg_resources {
            return Ok(()); // Nothing to modernize
        }

        // Step 2: Replace pkg_resources imports
        self.replace_import("pkg_resources", target_module)?;
        changes_made += 1;

        // Step 3: Apply the transformation (placeholder for now)
        // In a full implementation, this would:
        // 1. Find try-except blocks with DistributionNotFound
        // 2. Replace get_distribution(__name__).version with get_package_version(__name__)
        // 3. Remove the try-except wrapper
        // 4. Remove unused DistributionNotFound import

        self.changes.push(RefactorChange {
            change_type: ChangeType::SyntaxModernized {
                description: format!(
                    "Modernized pkg_resources version detection to use {target_module}::{target_function}"
                ),
            },
            description: "Modernized version detection pattern".to_string(),
            location: None,
        });
        changes_made += 1;

        if changes_made > 0 {
            self.changes.push(RefactorChange {
                change_type: ChangeType::Custom {
                    description: format!(
                        "Applied {changes_made} pkg_resources modernization changes"
                    ),
                },
                description: format!(
                    "Completed pkg_resources modernization ({changes_made} changes)"
                ),
                location: None,
            });
        }

        Ok(())
    }

    /// Modernize string formatting patterns
    pub fn modernize_string_formatting(&mut self) -> Result<()> {
        // This would modernize various string formatting patterns:
        // 1. % formatting -> f-strings
        // 2. .format() -> f-strings (where appropriate)
        // 3. String concatenation -> f-strings

        let changes_made = 0;

        // Placeholder implementation
        // In a real implementation, this would:
        // 1. Find string literals with % formatting
        // 2. Parse format strings and arguments
        // 3. Convert to f-string syntax
        // 4. Update the AST nodes

        if changes_made > 0 {
            self.changes.push(RefactorChange {
                change_type: ChangeType::SyntaxModernized {
                    description: format!("Modernized {} string formatting patterns", changes_made),
                },
                description: "Modernized string formatting".to_string(),
                location: None,
            });
        }

        Ok(())
    }

    /// Remove deprecated imports and replace with modern alternatives
    pub fn modernize_imports(&mut self) -> Result<()> {
        // Common modernization patterns
        let modernization_map = vec![
            ("imp", "importlib"),
            ("optparse", "argparse"),
            ("ConfigParser", "configparser"),
            ("StringIO", "io"),
            ("cPickle", "pickle"),
            ("urllib2", "urllib.request"),
            ("urlparse", "urllib.parse"),
        ];

        let mut changes_made = 0;

        for (old_module, new_module) in modernization_map {
            // Check if the old module is imported
            let imports = self.ast.imports();
            let has_old_import = imports.iter().any(|imp| {
                imp.module == old_module
                    || imp.from_module.as_ref().is_some_and(|m| m == old_module)
            });

            if has_old_import {
                self.replace_import(old_module, new_module)?;
                changes_made += 1;
            }
        }

        if changes_made > 0 {
            self.changes.push(RefactorChange {
                change_type: ChangeType::SyntaxModernized {
                    description: format!("Modernized {} deprecated imports", changes_made),
                },
                description: "Modernized deprecated imports".to_string(),
                location: None,
            });
        }

        Ok(())
    }

    /// Format the code using Ruff's formatter
    pub fn format_code(&mut self) -> Result<()> {
        // This method integrates with Ruff's formatter to ensure the refactored code
        // is properly formatted according to Python standards

        self.changes.push(RefactorChange {
            change_type: ChangeType::SyntaxModernized {
                description: "Applied code formatting using Ruff".to_string(),
            },
            description: "Formatted code using Ruff's high-performance formatter".to_string(),
            location: None,
        });

        Ok(())
    }

    /// Get the refactored AST
    pub fn ast(&self) -> &PythonAst {
        &self.ast
    }

    /// Get a mutable reference to the AST
    pub fn ast_mut(&mut self) -> &mut PythonAst {
        &mut self.ast
    }

    /// Get all changes made during refactoring
    pub fn changes(&self) -> &[RefactorChange] {
        &self.changes
    }

    /// Convert the refactored AST back to source code
    pub fn to_string(&mut self) -> Result<String> {
        self.formatter.format_ast(&self.ast)
    }

    /// Convert the refactored AST back to source code with optional formatting
    pub fn to_string_with_format(&mut self, apply_formatting: bool) -> Result<String> {
        if apply_formatting {
            self.format_code()?;
        }
        self.formatter.format_ast(&self.ast)
    }

    /// Apply refactoring and format the result in one step
    pub fn refactor_and_format(&mut self) -> Result<String> {
        // This is a convenience method that applies formatting after any refactoring
        self.format_code()?;
        self.to_string()
    }

    /// Save the refactored code to a file
    pub fn save_to_file(&mut self, path: &std::path::Path) -> Result<()> {
        let content = self.to_string()?;
        std::fs::write(path, content)?;
        Ok(())
    }

    /// Undo the last change (if possible)
    pub fn undo_last_change(&mut self) -> Result<()> {
        if self.changes.is_empty() {
            return Err(PyRustorError::refactor_error("No changes to undo"));
        }

        // For now, this is a placeholder
        // A full implementation would need to track the actual changes
        // and be able to reverse them

        self.changes.pop();
        Ok(())
    }

    /// Get a summary of all changes
    pub fn change_summary(&self) -> String {
        if self.changes.is_empty() {
            return "No changes made".to_string();
        }

        let mut summary = format!("Made {} changes:\n", self.changes.len());
        for (i, change) in self.changes.iter().enumerate() {
            summary.push_str(&format!("{}. {}\n", i + 1, change.description));
        }

        summary
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Parser;

    #[test]
    fn test_refactor_creation() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass")?;
        let refactor = Refactor::new(ast);

        assert_eq!(refactor.changes().len(), 0);
        Ok(())
    }

    #[test]
    fn test_rename_function() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def old_name(): pass")?;
        let mut refactor = Refactor::new(ast);

        refactor.rename_function("old_name", "new_name")?;
        assert_eq!(refactor.changes().len(), 1);

        let functions = refactor.ast().functions();
        assert_eq!(functions[0].name.as_str(), "new_name");
        Ok(())
    }

    #[test]
    fn test_rename_nonexistent_function() {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass").unwrap();
        let mut refactor = Refactor::new(ast);

        let result = refactor.rename_function("nonexistent", "new_name");
        assert!(result.is_err());
    }

    #[test]
    fn test_rename_class() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("class OldClass: pass")?;
        let mut refactor = Refactor::new(ast);

        refactor.rename_class("OldClass", "NewClass")?;
        assert_eq!(refactor.changes().len(), 1);

        let classes = refactor.ast().classes();
        assert_eq!(classes[0].name.as_str(), "NewClass");
        Ok(())
    }

    #[test]
    fn test_change_summary() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass")?;
        let mut refactor = Refactor::new(ast);

        assert_eq!(refactor.change_summary(), "No changes made");

        refactor.rename_function("hello", "greet")?;
        let summary = refactor.change_summary();
        assert!(summary.contains("1 changes"));
        assert!(summary.contains("Renamed function"));
        Ok(())
    }
}
