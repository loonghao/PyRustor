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
                if entry.path().extension().is_some_and(|ext| ext == "py") {
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
                if entry.path().extension().is_some_and(|ext| ext == "py") {
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
        assert_eq!(ast.statement_count(), 1);
        Ok(())
    }

    #[test]
    fn test_parse_function_with_parameters() -> Result<()> {
        let parser = Parser::new();
        let code = "def greet(name, age=25): return f'Hello {name}, age {age}'";
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());
        let functions = ast.function_names();
        assert_eq!(functions.len(), 1);
        assert_eq!(functions[0], "greet");
        Ok(())
    }

    #[test]
    fn test_parse_multiple_functions() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
def func1():
    return 1

def func2():
    return 2

def func3():
    return 3
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());
        assert_eq!(ast.statement_count(), 3);

        let functions = ast.function_names();
        assert_eq!(functions.len(), 3);
        assert!(functions.contains(&"func1".to_string()));
        assert!(functions.contains(&"func2".to_string()));
        assert!(functions.contains(&"func3".to_string()));
        Ok(())
    }

    #[test]
    fn test_parse_class() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
class TestClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());
        let classes = ast.class_names();
        assert_eq!(classes.len(), 1);
        assert_eq!(classes[0], "TestClass");
        Ok(())
    }

    #[test]
    fn test_parse_class_with_inheritance() -> Result<()> {
        let parser = Parser::new();
        let code = "class Child(Parent): pass";
        let ast = parser.parse_string(code)?;

        let classes = ast.class_names();
        assert!(classes.contains(&"Child".to_string()));
        Ok(())
    }

    #[test]
    fn test_parse_imports() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
import os
import sys
from pathlib import Path
from typing import List, Dict
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());
        let imports = ast.find_imports(None);
        assert!(!imports.is_empty());
        Ok(())
    }

    #[test]
    fn test_parse_empty_string() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("")?;
        assert!(ast.is_empty());
        assert_eq!(ast.statement_count(), 0);
        Ok(())
    }

    #[test]
    fn test_parse_whitespace_only() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("   \n\t  \n  ")?;
        assert!(ast.is_empty());
        Ok(())
    }

    #[test]
    fn test_parse_comments_only() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
# This is a comment
# Another comment
"#;
        let ast = parser.parse_string(code)?;
        assert!(ast.is_empty());
        Ok(())
    }

    #[test]
    fn test_parse_invalid_syntax() {
        let parser = Parser::new();

        let invalid_codes = vec![
            "def hello( pass",
            "def incomplete_function(",
            "class InvalidClass",
            "if True",
            "import",
        ];

        for code in invalid_codes {
            let result = parser.parse_string(code);
            assert!(result.is_err(), "Expected error for code: {}", code);
        }
    }

    #[test]
    fn test_parse_complex_code() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
import os
from typing import List, Optional

class DataProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.data = []

    def process(self, items: List[str]) -> Optional[List[str]]:
        result = []
        for item in items:
            if item.strip():
                result.append(item.upper())
        return result if result else None

def main():
    processor = DataProcessor({'debug': True})
    data = ['hello', 'world', '']
    result = processor.process(data)
    print(result)

if __name__ == '__main__':
    main()
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());

        let functions = ast.function_names();
        assert!(functions.contains(&"main".to_string()));

        let classes = ast.class_names();
        assert!(classes.contains(&"DataProcessor".to_string()));

        let imports = ast.find_imports(None);
        assert!(!imports.is_empty());

        Ok(())
    }

    #[test]
    fn test_parse_file() -> Result<()> {
        let dir = tempdir()?;
        let file_path = dir.path().join("test.py");
        fs::write(&file_path, "def test(): return 42")?;

        let parser = Parser::new();
        let ast = parser.parse_file(&file_path)?;
        assert!(!ast.is_empty());

        let functions = ast.function_names();
        assert_eq!(functions.len(), 1);
        assert_eq!(functions[0], "test");
        Ok(())
    }

    #[test]
    fn test_parse_nonexistent_file() {
        use std::path::Path;
        let parser = Parser::new();
        let result = parser.parse_file(Path::new("nonexistent_file.py"));
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_directory() -> Result<()> {
        let dir = tempdir()?;

        // Create test files
        let file1 = dir.path().join("file1.py");
        let file2 = dir.path().join("file2.py");
        fs::write(&file1, "def func1(): pass")?;
        fs::write(&file2, "def func2(): pass")?;

        let parser = Parser::new();
        let results = parser.parse_directory(dir.path(), false)?;

        assert_eq!(results.len(), 2);
        for (_, ast) in results {
            assert!(!ast.is_empty());
        }
        Ok(())
    }

    #[test]
    fn test_parser_options() -> Result<()> {
        let parser = Parser::with_options(false, false);
        let ast = parser.parse_string("# comment\ndef hello(): pass")?;
        assert!(!ast.is_empty());
        Ok(())
    }

    #[test]
    fn test_unicode_handling() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
def greet_世界():
    return "Hello 世界! 🌍"

class UnicodeClass_测试:
    pass
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());

        let functions = ast.function_names();
        assert!(functions.contains(&"greet_世界".to_string()));

        let classes = ast.class_names();
        assert!(classes.contains(&"UnicodeClass_测试".to_string()));

        Ok(())
    }

    #[test]
    fn test_large_file_parsing() -> Result<()> {
        let parser = Parser::new();

        // Generate a large Python file
        let mut large_code = String::new();
        for i in 0..1000 {
            large_code.push_str(&format!("def function_{}(): return {}\n", i, i));
        }

        let ast = parser.parse_string(&large_code)?;

        assert!(!ast.is_empty());
        assert_eq!(ast.statement_count(), 1000);

        let functions = ast.function_names();
        assert_eq!(functions.len(), 1000);
        assert!(functions.contains(&"function_0".to_string()));
        assert!(functions.contains(&"function_999".to_string()));

        Ok(())
    }
}
