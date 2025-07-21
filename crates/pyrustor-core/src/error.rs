//! Error types for PyRustor Core

use thiserror::Error;

/// Result type alias for PyRustor operations
pub type Result<T> = std::result::Result<T, PyRustorError>;

/// Main error type for PyRustor operations
#[derive(Error, Debug)]
pub enum PyRustorError {
    /// Parsing errors when processing Python code
    #[error("Parse error: {message} at line {line}, column {column}")]
    ParseError {
        message: String,
        line: usize,
        column: usize,
    },

    /// IO errors when reading/writing files
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    /// Refactoring operation errors
    #[error("Refactor error: {0}")]
    RefactorError(String),

    /// AST manipulation errors
    #[error("AST error: {0}")]
    AstError(String),

    /// Formatting errors
    #[error("Format error: {0}")]
    FormatError(String),

    /// Invalid input errors
    #[error("Invalid input: {0}")]
    InvalidInput(String),

    /// Serialization/deserialization errors
    #[error("Serialization error: {0}")]
    SerializationError(#[from] serde_json::Error),

    /// File system walking errors
    #[error("Directory traversal error: {0}")]
    WalkDirError(#[from] walkdir::Error),

    /// Generic errors
    #[error("Error: {0}")]
    Other(#[from] anyhow::Error),
}

impl PyRustorError {
    /// Create a new parse error
    pub fn parse_error(message: impl Into<String>, line: usize, column: usize) -> Self {
        Self::ParseError {
            message: message.into(),
            line,
            column,
        }
    }

    /// Create a new refactor error
    pub fn refactor_error(message: impl Into<String>) -> Self {
        Self::RefactorError(message.into())
    }

    /// Create a new AST error
    pub fn ast_error(message: impl Into<String>) -> Self {
        Self::AstError(message.into())
    }

    /// Create a new format error
    pub fn format_error(message: impl Into<String>) -> Self {
        Self::FormatError(message.into())
    }

    /// Create a new invalid input error
    pub fn invalid_input(message: impl Into<String>) -> Self {
        Self::InvalidInput(message.into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_creation() {
        let error = PyRustorError::parse_error("test error", 1, 5);
        assert!(error.to_string().contains("test error"));
        assert!(error.to_string().contains("line 1"));
        assert!(error.to_string().contains("column 5"));
    }

    #[test]
    fn test_error_conversion() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let pyrustor_error: PyRustorError = io_error.into();
        assert!(matches!(pyrustor_error, PyRustorError::IoError(_)));
    }
}
