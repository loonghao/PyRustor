//! Core AST functionality

use crate::{error::Result, PyRustorError};
use ruff_python_ast::{Expr, ModModule, Stmt};

/// Represents a Python Abstract Syntax Tree with formatting information
#[derive(Debug, Clone)]
pub struct PythonAst {
    /// The root module AST node
    pub(crate) module: ModModule,
    /// Original source code for preserving formatting
    pub(crate) source: String,
    /// Whether comments are preserved
    #[allow(dead_code)]
    pub(crate) preserve_comments: bool,
    /// Whether formatting is preserved
    #[allow(dead_code)]
    pub(crate) preserve_formatting: bool,
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

    /// Get the underlying module
    pub fn module(&self) -> &ModModule {
        &self.module
    }

    /// Get mutable reference to the underlying module
    pub fn module_mut(&mut self) -> &mut ModModule {
        &mut self.module
    }

    /// Get the original source code
    pub fn source(&self) -> &str {
        &self.source
    }

    /// Check if the AST is empty (no statements)
    pub fn is_empty(&self) -> bool {
        self.module.body.is_empty()
    }

    /// Check if the AST contains only comments and docstrings (no executable code)
    pub fn is_comments_only(&self) -> bool {
        if self.module.body.is_empty() {
            return true;
        }

        // Check if all statements are just string literals (docstrings)
        for stmt in &self.module.body {
            match stmt {
                Stmt::Expr(expr) => {
                    // Check if this is a string literal (docstring)
                    match &*expr.value {
                        Expr::StringLiteral(_) => {
                            // This is a string literal (docstring), continue checking
                        }
                        _ => {
                            // Any other expression is meaningful
                            return false;
                        }
                    }
                }
                _ => {
                    // Any non-expression statement is meaningful
                    return false;
                }
            }
        }

        // All statements are string literals (docstrings), so consider it comments-only
        true
    }

    /// Get the number of statements in the module
    pub fn statement_count(&self) -> usize {
        self.module.body.len()
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

    /// Get names of all classes in the module
    pub fn class_names(&self) -> Vec<String> {
        self.classes()
            .iter()
            .map(|class| class.name.to_string())
            .collect()
    }

    /// Get names of all functions in the module (including methods in classes)
    pub fn function_names(&self) -> Vec<String> {
        let mut names = Vec::new();
        Self::collect_function_names_recursive(&self.module.body, &mut names);
        names
    }

    /// Recursively collect function names from statements
    fn collect_function_names_recursive(stmts: &[Stmt], names: &mut Vec<String>) {
        for stmt in stmts {
            match stmt {
                Stmt::FunctionDef(func) => {
                    names.push(func.name.to_string());
                }
                Stmt::ClassDef(class) => {
                    // Recursively search in class body for methods
                    Self::collect_function_names_recursive(&class.body, names);
                }
                _ => {}
            }
        }
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
