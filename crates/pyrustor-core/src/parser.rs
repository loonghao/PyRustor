//! Python code parser implementation

use crate::{ast::PythonAst, error::Result, PyRustorError};
use ruff_python_parser::parse_module;
use std::path::Path;

/// Python code parser
///
/// The parser converts Python source code into an Abstract Syntax Tree (AST)
/// while preserving formatting information for later reconstruction.
#[derive(Debug, Clone)]
pub struct Parser {
    /// Whether to preserve comments in the AST
    preserve_comments: bool,
    /// Whether to preserve formatting information
    preserve_formatting: bool,
}

impl Default for Parser {
    fn default() -> Self {
        Self::new()
    }
}

impl Parser {
    /// Create a new parser with default settings
    pub fn new() -> Self {
        Self {
            preserve_comments: true,
            preserve_formatting: true,
        }
    }

    /// Create a parser with custom settings
    pub fn with_options(preserve_comments: bool, preserve_formatting: bool) -> Self {
        Self {
            preserve_comments,
            preserve_formatting,
        }
    }

    /// Parse Python code from a string
    ///
    /// # Arguments
    ///
    /// * `source` - The Python source code to parse
    ///
    /// # Returns
    ///
    /// A `Result` containing the parsed AST or an error
    ///
    /// # Example
    ///
    /// ```rust
    /// use pyrustor_core::Parser;
    ///
    /// let parser = Parser::new();
    /// let ast = parser.parse_string("def hello(): pass")?;
    /// # Ok::<(), Box<dyn std::error::Error>>(())
    /// ```
    pub fn parse_string(&self, source: &str) -> Result<PythonAst> {
        match parse_module(source) {
            Ok(parsed) => Ok(PythonAst::new(
                parsed.into_syntax(),
                source.to_string(),
                self.preserve_comments,
                self.preserve_formatting,
            )),
            Err(parse_error) => {
                Err(PyRustorError::parse_error(
                    format!("Parse error: {}", parse_error),
                    0, // We'll improve location tracking later
                    0,
                ))
            }
        }
    }

    /// Parse Python code from a file
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the Python file to parse
    ///
    /// # Returns
    ///
    /// A `Result` containing the parsed AST or an error
    ///
    /// # Example
    ///
    /// ```rust,no_run
    /// use pyrustor_core::Parser;
    /// use std::path::Path;
    ///
    /// let parser = Parser::new();
    /// let ast = parser.parse_file(Path::new("example.py"))?;
    /// # Ok::<(), Box<dyn std::error::Error>>(())
    /// ```
    pub fn parse_file(&self, path: &Path) -> Result<PythonAst> {
        let source = std::fs::read_to_string(path)?;

        match parse_module(&source) {
            Ok(parsed) => Ok(PythonAst::new(
                parsed.into_syntax(),
                source,
                self.preserve_comments,
                self.preserve_formatting,
            )),
            Err(parse_error) => Err(PyRustorError::parse_error(
                format!("Parse error in {}: {}", path.display(), parse_error),
                0,
                0,
            )),
        }
    }

    /// Parse multiple Python files from a directory
    ///
    /// # Arguments
    ///
    /// * `dir_path` - Path to the directory containing Python files
    /// * `recursive` - Whether to search subdirectories recursively
    ///
    /// # Returns
    ///
    /// A `Result` containing a vector of parsed ASTs or an error
    pub fn parse_directory(
        &self,
        dir_path: &Path,
        recursive: bool,
    ) -> Result<Vec<(String, PythonAst)>> {
        let mut results: Vec<(String, PythonAst)> = Vec::new();

        if recursive {
            for entry in walkdir::WalkDir::new(dir_path) {
                let entry = entry?;
                if entry.path().extension().map_or(false, |ext| ext == "py") {
                    match self.parse_file(entry.path()) {
                        Ok(ast) => {
                            results.push((entry.path().to_string_lossy().to_string(), ast));
                        }
                        Err(e) => {
                            eprintln!("Warning: Failed to parse {}: {}", entry.path().display(), e);
                        }
                    }
                }
            }
        } else {
            for entry in std::fs::read_dir(dir_path)? {
                let entry = entry?;
                if entry.path().extension().map_or(false, |ext| ext == "py") {
                    match self.parse_file(&entry.path()) {
                        Ok(ast) => {
                            results.push((entry.path().to_string_lossy().to_string(), ast));
                        }
                        Err(e) => {
                            eprintln!("Warning: Failed to parse {}: {}", entry.path().display(), e);
                        }
                    }
                }
            }
        }

        Ok(results)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_parse_simple_function() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("def hello(): pass")?;
        assert!(!ast.is_empty());
        Ok(())
    }

    #[test]
    fn test_parse_invalid_syntax() {
        let parser = Parser::new();
        let result = parser.parse_string("def hello( pass");
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_file() -> Result<()> {
        let dir = tempdir()?;
        let file_path = dir.path().join("test.py");
        fs::write(&file_path, "def test(): return 42")?;

        let parser = Parser::new();
        let ast = parser.parse_file(&file_path)?;
        assert!(!ast.is_empty());
        Ok(())
    }

    #[test]
    fn test_parser_options() -> Result<()> {
        let parser = Parser::with_options(false, false);
        let ast = parser.parse_string("# comment\ndef hello(): pass")?;
        assert!(!ast.is_empty());
        Ok(())
    }
}
