//! PyRustor Core Library
//!
//! A high-performance Python code parsing and refactoring library written in Rust.

#![allow(clippy::uninlined_format_args)]
//! This library provides comprehensive tools for analyzing, modifying, and modernizing
//! Python codebases while preserving original formatting and style.
//!
//! # Features
//!
//! - **Complete Python parsing**: Parse Python code into a full Abstract Syntax Tree (AST)
//! - **Format preservation**: Maintain original code formatting, comments, and whitespace
//! - **Code refactoring**: Perform precise code modifications and transformations
//! - **Batch operations**: Process entire codebases efficiently
//! - **Modern Python support**: Full compatibility with Python 3.8+ syntax
//!
//! # Example
//!
//! ```rust
//! use pyrustor_core::{Parser, Refactor};
//!
//! // Parse Python code
//! let parser = Parser::new();
//! let ast = parser.parse_string("def hello(): pass")?;
//!
//! // Create refactor instance
//! let mut refactor = Refactor::new(ast);
//! refactor.rename_function("hello", "greet")?;
//!
//! // Get the modified code
//! let result = refactor.to_string();
//! # Ok::<(), Box<dyn std::error::Error>>(())
//! ```

pub mod ast;
pub mod code_generator;
pub mod error;
pub mod formatter;
pub mod parser;
pub mod refactor;

// Re-export main types for convenience
pub use ast::{
    AssignmentNode, AstNodeRef, CallNode, ImportInfo, ImportNode, PythonAst, SourceLocation,
    TryExceptNode,
};
pub use code_generator::CodeGenerator;
pub use error::{PyRustorError, Result};
pub use formatter::Formatter;
pub use parser::Parser;
pub use refactor::Refactor;

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[allow(clippy::const_is_empty)]
    fn test_version() {
        // VERSION is a compile-time constant, so this check is always true
        assert!(!VERSION.is_empty());
    }

    #[test]
    fn test_basic_parsing() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def test(): pass")?;
        assert!(!ast.is_empty());
        Ok(())
    }
}
