//! Abstract Syntax Tree (AST) representation and manipulation

use crate::{error::Result, PyRustorError};
use ruff_python_ast::ModModule;
use serde::{Deserialize, Serialize};
use std::fmt;

/// Represents a Python Abstract Syntax Tree with formatting information
#[derive(Debug, Clone)]
pub struct PythonAst {
    /// The root module AST node
    module: ModModule,
    /// Original source code for preserving formatting
    source: String,
    /// Whether comments are preserved
    preserve_comments: bool,
    /// Whether formatting is preserved
    preserve_formatting: bool,
}

impl PythonAst {
    /// Create a new PythonAst instance
    pub fn new(
        module: ModModule,
        source: String,
        preserve_comments: bool,
        preserve_formatting: bool,
    ) -> Self {
        Self {
            module,
            source,
            preserve_comments,
            preserve_formatting,
        }
    }

    /// Get the root module
    pub fn module(&self) -> &ModModule {
        &self.module
    }

    /// Get a mutable reference to the root module
    pub fn module_mut(&mut self) -> &mut ModModule {
        &mut self.module
    }

    /// Get the source code
    pub fn source(&self) -> &str {
        &self.source
    }

    /// Check if the AST is empty (no statements)
    pub fn is_empty(&self) -> bool {
        self.module.body.is_empty()
    }

    /// Get the number of statements in the module
    pub fn statement_count(&self) -> usize {
        self.module.body.len()
    }

    /// Convert the AST back to Python source code
    pub fn to_string(&self) -> Result<String> {
        // For now, we'll use a simple approach
        // In a full implementation, this would use a proper code generator
        // that preserves formatting based on the original source
        Ok(format!("{:#?}", self.module))
    }

    /// Get all function definitions in the module
    pub fn functions(&self) -> Vec<&ruff_python_ast::StmtFunctionDef> {
        use ruff_python_ast::Stmt;

        self.module
            .body
            .iter()
            .filter_map(|stmt| match stmt {
                Stmt::FunctionDef(func) => Some(func),
                _ => None,
            })
            .collect()
    }

    /// Get mutable references to all function definitions
    pub fn functions_mut(&mut self) -> Vec<&mut ruff_python_ast::StmtFunctionDef> {
        use ruff_python_ast::Stmt;

        self.module
            .body
            .iter_mut()
            .filter_map(|stmt| match stmt {
                Stmt::FunctionDef(func) => Some(func),
                _ => None,
            })
            .collect()
    }

    /// Get all class definitions in the module
    pub fn classes(&self) -> Vec<&ruff_python_ast::StmtClassDef> {
        use ruff_python_ast::Stmt;

        self.module
            .body
            .iter()
            .filter_map(|stmt| match stmt {
                Stmt::ClassDef(class) => Some(class),
                _ => None,
            })
            .collect()
    }

    /// Get mutable references to all class definitions
    pub fn classes_mut(&mut self) -> Vec<&mut ruff_python_ast::StmtClassDef> {
        use ruff_python_ast::Stmt;

        self.module
            .body
            .iter_mut()
            .filter_map(|stmt| match stmt {
                Stmt::ClassDef(class) => Some(class),
                _ => None,
            })
            .collect()
    }

    /// Get all import statements in the module
    pub fn imports(&self) -> Vec<ImportInfo> {
        use ruff_python_ast::Stmt;

        let mut imports = Vec::new();

        for stmt in &self.module.body {
            match stmt {
                Stmt::Import(import_stmt) => {
                    for alias in &import_stmt.names {
                        imports.push(ImportInfo {
                            module: alias.name.to_string(),
                            alias: alias.asname.as_ref().map(|name| name.to_string()),
                            is_from_import: false,
                            from_module: None,
                        });
                    }
                }
                Stmt::ImportFrom(import_from) => {
                    let from_module = import_from.module.as_ref().map(|m| m.to_string());
                    for alias in &import_from.names {
                        imports.push(ImportInfo {
                            module: alias.name.to_string(),
                            alias: alias.asname.as_ref().map(|name| name.to_string()),
                            is_from_import: true,
                            from_module: from_module.clone(),
                        });
                    }
                }
                _ => {}
            }
        }

        imports
    }

    /// Validate the AST structure
    pub fn validate(&self) -> Result<()> {
        // Basic validation - in a full implementation this would be more comprehensive
        if self.module.body.is_empty() {
            return Err(PyRustorError::ast_error("Empty module"));
        }
        Ok(())
    }
}

/// Information about an import statement
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ImportInfo {
    /// The imported module or name
    pub module: String,
    /// Optional alias for the import
    pub alias: Option<String>,
    /// Whether this is a "from ... import ..." statement
    pub is_from_import: bool,
    /// The module being imported from (for from imports)
    pub from_module: Option<String>,
}

/// Generic AST node trait for common operations
pub trait AstNode {
    /// Get the type name of the node
    fn node_type(&self) -> &'static str;

    /// Get the line number where this node starts
    fn line_number(&self) -> Option<usize>;

    /// Get the column number where this node starts
    fn column_number(&self) -> Option<usize>;
}

impl fmt::Display for ImportInfo {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.is_from_import {
            if let Some(from_module) = &self.from_module {
                write!(f, "from {} import {}", from_module, self.module)?;
            } else {
                write!(f, "from . import {}", self.module)?;
            }
        } else {
            write!(f, "import {}", self.module)?;
        }

        if let Some(alias) = &self.alias {
            write!(f, " as {}", alias)?;
        }

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Parser;

    #[test]
    fn test_ast_creation() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass")?;

        assert!(!ast.is_empty());
        assert_eq!(ast.statement_count(), 1);
        Ok(())
    }

    #[test]
    fn test_function_extraction() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass\ndef world(): return 42")?;

        let functions = ast.functions();
        assert_eq!(functions.len(), 2);
        assert_eq!(functions[0].name.as_str(), "hello");
        assert_eq!(functions[1].name.as_str(), "world");
        Ok(())
    }

    #[test]
    fn test_import_extraction() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("import os\nfrom sys import path\nimport json as js")?;

        let imports = ast.imports();
        assert_eq!(imports.len(), 3);

        assert_eq!(imports[0].module, "os");
        assert!(!imports[0].is_from_import);

        assert_eq!(imports[1].module, "path");
        assert!(imports[1].is_from_import);
        assert_eq!(imports[1].from_module.as_ref().unwrap(), "sys");

        assert_eq!(imports[2].module, "json");
        assert_eq!(imports[2].alias.as_ref().unwrap(), "js");
        Ok(())
    }

    #[test]
    fn test_class_extraction() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("class MyClass: pass\nclass AnotherClass(object): pass")?;

        let classes = ast.classes();
        assert_eq!(classes.len(), 2);
        assert_eq!(classes[0].name.as_str(), "MyClass");
        assert_eq!(classes[1].name.as_str(), "AnotherClass");
        Ok(())
    }
}
