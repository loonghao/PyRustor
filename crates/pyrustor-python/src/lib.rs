//! Python bindings for PyRustor
//!
//! This module provides Python bindings for the PyRustor core library,
//! enabling Python developers to use the high-performance Rust-based
//! Python code parsing and refactoring tools.

use pyo3::prelude::*;
use pyrustor_core::{Parser as CoreParser, PythonAst as CoreAst, Refactor as CoreRefactor};
use std::path::PathBuf;

/// Python wrapper for the Parser
#[pyclass]
struct Parser {
    inner: CoreParser,
}

#[pymethods]
impl Parser {
    /// Create a new parser
    #[new]
    fn new() -> Self {
        Self {
            inner: CoreParser::new(),
        }
    }

    /// Parse Python code from a string
    fn parse_string(&self, source: &str) -> PyResult<PythonAst> {
        match self.inner.parse_string(source) {
            Ok(ast) => Ok(PythonAst { inner: ast }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Parse error: {}",
                e
            ))),
        }
    }

    /// Parse Python code from a file
    fn parse_file(&self, path: &str) -> PyResult<PythonAst> {
        let path = PathBuf::from(path);
        match self.inner.parse_file(&path) {
            Ok(ast) => Ok(PythonAst { inner: ast }),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Parse error: {}",
                e
            ))),
        }
    }

    /// Parse multiple Python files from a directory
    fn parse_directory(
        &self,
        dir_path: &str,
        recursive: bool,
    ) -> PyResult<Vec<(String, PythonAst)>> {
        let path = PathBuf::from(dir_path);
        match self.inner.parse_directory(&path, recursive) {
            Ok(results) => {
                let py_results = results
                    .into_iter()
                    .map(|(path, ast)| (path, PythonAst { inner: ast }))
                    .collect();
                Ok(py_results)
            }
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Parse error: {}",
                e
            ))),
        }
    }

    fn __repr__(&self) -> String {
        "Parser()".to_string()
    }
}

/// Python wrapper for the PythonAst
#[pyclass]
struct PythonAst {
    inner: CoreAst,
}

#[pymethods]
impl PythonAst {
    /// Check if the AST is empty
    fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Get the number of statements
    fn statement_count(&self) -> usize {
        self.inner.statement_count()
    }

    /// Get function names
    fn function_names(&self) -> Vec<String> {
        self.inner
            .functions()
            .iter()
            .map(|f| f.name.to_string())
            .collect()
    }

    /// Get class names
    fn class_names(&self) -> Vec<String> {
        self.inner
            .classes()
            .iter()
            .map(|c| c.name.to_string())
            .collect()
    }

    /// Get import information
    fn imports(&self) -> Vec<String> {
        self.inner.imports().iter().map(|i| i.to_string()).collect()
    }

    /// Convert AST back to string
    fn to_string(&self) -> PyResult<String> {
        match self.inner.to_string() {
            Ok(s) => Ok(s),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Format error: {}",
                e
            ))),
        }
    }

    fn __repr__(&self) -> String {
        format!("PythonAst(statements={})", self.inner.statement_count())
    }
}

/// Python wrapper for the Refactor
#[pyclass]
struct Refactor {
    inner: CoreRefactor,
}

#[pymethods]
impl Refactor {
    /// Create a new refactor instance
    #[new]
    fn new(ast: &PythonAst) -> Self {
        Self {
            inner: CoreRefactor::new(ast.inner.clone()),
        }
    }

    /// Rename a function
    fn rename_function(&mut self, old_name: &str, new_name: &str) -> PyResult<()> {
        match self.inner.rename_function(old_name, new_name) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Rename a class
    fn rename_class(&mut self, old_name: &str, new_name: &str) -> PyResult<()> {
        match self.inner.rename_class(old_name, new_name) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Replace import statements
    fn replace_import(&mut self, old_module: &str, new_module: &str) -> PyResult<()> {
        match self.inner.replace_import(old_module, new_module) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Modernize syntax
    fn modernize_syntax(&mut self) -> PyResult<()> {
        match self.inner.modernize_syntax() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Get the refactored code as string
    fn to_string(&mut self) -> PyResult<String> {
        match self.inner.to_string() {
            Ok(s) => Ok(s),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Format error: {}",
                e
            ))),
        }
    }

    /// Save to file
    fn save_to_file(&mut self, path: &str) -> PyResult<()> {
        let path = PathBuf::from(path);
        match self.inner.save_to_file(&path) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "IO error: {}",
                e
            ))),
        }
    }

    /// Get change summary
    fn change_summary(&self) -> String {
        self.inner.change_summary()
    }

    /// Rename function with optional formatting
    fn rename_function_with_format(
        &mut self,
        old_name: &str,
        new_name: &str,
        apply_formatting: bool,
    ) -> PyResult<()> {
        match self
            .inner
            .rename_function_with_format(old_name, new_name, apply_formatting)
        {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Rename class with optional formatting
    fn rename_class_with_format(
        &mut self,
        old_name: &str,
        new_name: &str,
        apply_formatting: bool,
    ) -> PyResult<()> {
        match self
            .inner
            .rename_class_with_format(old_name, new_name, apply_formatting)
        {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Modernize syntax with optional formatting
    fn modernize_syntax_with_format(&mut self, apply_formatting: bool) -> PyResult<()> {
        match self.inner.modernize_syntax_with_format(apply_formatting) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Format code using Ruff's formatter
    fn format_code(&mut self) -> PyResult<()> {
        match self.inner.format_code() {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Convert to string with optional formatting
    fn to_string_with_format(&mut self, apply_formatting: bool) -> PyResult<String> {
        match self.inner.to_string_with_format(apply_formatting) {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    /// Apply refactoring and format the result in one step
    fn refactor_and_format(&mut self) -> PyResult<String> {
        match self.inner.refactor_and_format() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Refactor error: {}",
                e
            ))),
        }
    }

    fn __repr__(&self) -> String {
        format!("Refactor(changes={})", self.inner.changes().len())
    }
}

/// PyRustor Python module
#[pymodule]
fn _pyrustor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Parser>()?;
    m.add_class::<PythonAst>()?;
    m.add_class::<Refactor>()?;

    // Add version information
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}
