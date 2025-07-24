//! Python bindings for PyRustor
//!
//! This module provides Python bindings for the PyRustor core library,
//! enabling Python developers to use the high-performance Rust-based
//! Python code parsing and refactoring tools.

use pyo3::prelude::*;
use pyrustor_core::{
    AssignmentNode as CoreAssignmentNode, AstNodeRef as CoreAstNodeRef, CallNode as CoreCallNode,
    CodeGenerator as CoreCodeGenerator, ImportNode as CoreImportNode, Parser as CoreParser,
    PythonAst as CoreAst, Refactor as CoreRefactor, TryExceptNode as CoreTryExceptNode,
};
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

    /// Check if the AST contains only comments and docstrings
    fn is_comments_only(&self) -> bool {
        self.inner.is_comments_only()
    }

    /// Get the number of statements
    fn statement_count(&self) -> usize {
        self.inner.statement_count()
    }

    /// Get function names (including methods in classes)
    fn function_names(&self) -> Vec<String> {
        self.inner.function_names()
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
        self.inner
            .find_imports(None)
            .iter()
            .map(|i| i.module.clone())
            .collect()
    }

    /// Convert AST back to string
    fn to_string(&self) -> PyResult<String> {
        match self.inner.to_code() {
            Ok(s) => Ok(s),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Format error: {}",
                e
            ))),
        }
    }

    // ========== Bottom-level API methods ==========

    /// Find nodes matching specific criteria (bottom-level API)
    #[pyo3(signature = (node_type=None))]
    fn find_nodes(&self, node_type: Option<&str>) -> Vec<AstNodeRef> {
        self.inner
            .find_nodes(node_type)
            .into_iter()
            .map(|node| AstNodeRef { inner: node })
            .collect()
    }

    /// Find import statements
    #[pyo3(signature = (module_pattern=None))]
    fn find_imports(&self, module_pattern: Option<&str>) -> Vec<ImportNode> {
        self.inner
            .find_imports(module_pattern)
            .into_iter()
            .map(|node| ImportNode { inner: node })
            .collect()
    }

    /// Find function calls
    fn find_function_calls(&self, function_name: &str) -> Vec<CallNode> {
        self.inner
            .find_function_calls(Some(function_name))
            .into_iter()
            .map(|node| CallNode { inner: node })
            .collect()
    }

    /// Find try-except blocks
    #[pyo3(signature = (exception_type=None))]
    fn find_try_except_blocks(&self, exception_type: Option<&str>) -> Vec<TryExceptNode> {
        self.inner
            .find_try_except_blocks(exception_type)
            .into_iter()
            .map(|node| TryExceptNode { inner: node })
            .collect()
    }

    /// Find assignment statements
    #[pyo3(signature = (target_pattern=None))]
    fn find_assignments(&self, target_pattern: Option<&str>) -> Vec<AssignmentNode> {
        self.inner
            .find_assignments(target_pattern)
            .into_iter()
            .map(|node| AssignmentNode { inner: node })
            .collect()
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

    /// Rename a function with optional error on not found
    #[pyo3(signature = (old_name, new_name, error_if_not_found=true))]
    fn rename_function_optional(
        &mut self,
        old_name: &str,
        new_name: &str,
        error_if_not_found: bool,
    ) -> PyResult<()> {
        match self
            .inner
            .rename_function_optional(old_name, new_name, error_if_not_found)
        {
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

    /// Rename a class with optional error on not found
    #[pyo3(signature = (old_name, new_name, error_if_not_found=true))]
    fn rename_class_optional(
        &mut self,
        old_name: &str,
        new_name: &str,
        error_if_not_found: bool,
    ) -> PyResult<()> {
        match self
            .inner
            .rename_class_optional(old_name, new_name, error_if_not_found)
        {
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
    fn get_code(&mut self) -> PyResult<String> {
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
    fn get_code_with_format(&mut self, apply_formatting: bool) -> PyResult<String> {
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

    /// Convert the refactored AST back to source code
    fn to_string(&mut self) -> PyResult<String> {
        match self.inner.to_string() {
            Ok(result) => Ok(result),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Format error: {}",
                e
            ))),
        }
    }

    // ========== Bottom-level API methods ==========

    /// Get access to the underlying AST for low-level operations
    fn ast(&self) -> PythonAst {
        PythonAst {
            inner: self.inner.ast().clone(),
        }
    }

    /// Find nodes matching specific criteria (bottom-level API)
    #[pyo3(signature = (node_type=None))]
    fn find_nodes(&self, node_type: Option<&str>) -> Vec<AstNodeRef> {
        self.inner
            .find_nodes(node_type)
            .into_iter()
            .map(|node| AstNodeRef { inner: node })
            .collect()
    }

    /// Find import statements
    #[pyo3(signature = (module_pattern=None))]
    fn find_imports(&self, module_pattern: Option<&str>) -> Vec<ImportNode> {
        self.inner
            .find_imports(module_pattern)
            .into_iter()
            .map(|node| ImportNode { inner: node })
            .collect()
    }

    /// Find function calls
    fn find_function_calls(&self, function_name: &str) -> Vec<CallNode> {
        self.inner
            .find_function_calls(function_name)
            .into_iter()
            .map(|node| CallNode { inner: node })
            .collect()
    }

    /// Find try-except blocks
    #[pyo3(signature = (exception_type=None))]
    fn find_try_except_blocks(&self, exception_type: Option<&str>) -> Vec<TryExceptNode> {
        self.inner
            .find_try_except_blocks(exception_type)
            .into_iter()
            .map(|node| TryExceptNode { inner: node })
            .collect()
    }

    /// Find assignment statements
    #[pyo3(signature = (target_pattern=None))]
    fn find_assignments(&self, target_pattern: Option<&str>) -> Vec<AssignmentNode> {
        self.inner
            .find_assignments(target_pattern)
            .into_iter()
            .map(|node| AssignmentNode { inner: node })
            .collect()
    }

    /// Replace a specific AST node with new code (bottom-level API)
    fn replace_node(&mut self, node_ref: &AstNodeRef, new_code: &str) -> PyResult<()> {
        match self.inner.replace_node(&node_ref.inner, new_code) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Replace node error: {}",
                e
            ))),
        }
    }

    /// Remove a specific AST node (bottom-level API)
    fn remove_node(&mut self, node_ref: &AstNodeRef) -> PyResult<()> {
        match self.inner.remove_node(&node_ref.inner) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Remove node error: {}",
                e
            ))),
        }
    }

    /// Insert code before a specific AST node (bottom-level API)
    fn insert_before(&mut self, node_ref: &AstNodeRef, new_code: &str) -> PyResult<()> {
        match self.inner.insert_before(&node_ref.inner, new_code) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Insert before error: {}",
                e
            ))),
        }
    }

    /// Insert code after a specific AST node (bottom-level API)
    fn insert_after(&mut self, node_ref: &AstNodeRef, new_code: &str) -> PyResult<()> {
        match self.inner.insert_after(&node_ref.inner, new_code) {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Insert after error: {}",
                e
            ))),
        }
    }

    /// Replace code in a specific line range (bottom-level API)
    fn replace_code_range(
        &mut self,
        start_line: usize,
        end_line: usize,
        new_code: &str,
    ) -> PyResult<()> {
        match self
            .inner
            .replace_code_range(start_line, end_line, new_code)
        {
            Ok(()) => Ok(()),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Replace range error: {}",
                e
            ))),
        }
    }

    /// Get a code generator for creating Python code snippets (bottom-level API)
    fn code_generator(&self) -> CodeGenerator {
        CodeGenerator {
            inner: self.inner.code_generator(),
        }
    }

    fn __repr__(&self) -> String {
        format!("Refactor(changes={})", self.inner.changes().len())
    }
}

/// Python wrapper for AST node references (bottom-level API)
#[pyclass]
#[derive(Clone)]
struct AstNodeRef {
    inner: CoreAstNodeRef,
}

#[pymethods]
impl AstNodeRef {
    /// Get the node type
    #[getter]
    fn node_type(&self) -> String {
        self.inner.node_type.clone()
    }

    /// Get the path to this node
    #[getter]
    fn path(&self) -> Vec<usize> {
        self.inner.path.clone()
    }

    fn __repr__(&self) -> String {
        format!(
            "AstNodeRef(type='{}', path={:?})",
            self.inner.node_type, self.inner.path
        )
    }
}

/// Python wrapper for import nodes (bottom-level API)
#[pyclass]
#[derive(Clone)]
struct ImportNode {
    inner: CoreImportNode,
}

#[pymethods]
impl ImportNode {
    /// Get the module name
    #[getter]
    fn module(&self) -> String {
        self.inner.module.clone()
    }

    /// Get the imported items
    #[getter]
    fn items(&self) -> Vec<String> {
        self.inner.items.clone()
    }

    /// Get the node reference
    #[getter]
    fn node_ref(&self) -> AstNodeRef {
        AstNodeRef {
            inner: self.inner.node_ref.clone(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "ImportNode(module='{}', items={:?})",
            self.inner.module, self.inner.items
        )
    }
}

/// Python wrapper for function call nodes (bottom-level API)
#[pyclass]
#[derive(Clone)]
struct CallNode {
    inner: CoreCallNode,
}

#[pymethods]
impl CallNode {
    /// Get the function name
    #[getter]
    fn function_name(&self) -> String {
        self.inner.function_name.clone()
    }

    /// Get the arguments
    #[getter]
    fn args(&self) -> Vec<String> {
        self.inner.args.clone()
    }

    /// Get the node reference
    #[getter]
    fn node_ref(&self) -> AstNodeRef {
        AstNodeRef {
            inner: self.inner.node_ref.clone(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "CallNode(function='{}', args={:?})",
            self.inner.function_name, self.inner.args
        )
    }
}

/// Python wrapper for try-except nodes (bottom-level API)
#[pyclass]
#[derive(Clone)]
struct TryExceptNode {
    inner: CoreTryExceptNode,
}

#[pymethods]
impl TryExceptNode {
    /// Get the exception types
    #[getter]
    fn exception_types(&self) -> Vec<String> {
        self.inner.exception_types.clone()
    }

    /// Get the node reference
    #[getter]
    fn node_ref(&self) -> AstNodeRef {
        AstNodeRef {
            inner: self.inner.node_ref.clone(),
        }
    }

    fn __repr__(&self) -> String {
        format!("TryExceptNode(exceptions={:?})", self.inner.exception_types)
    }
}

/// Python wrapper for assignment nodes (bottom-level API)
#[pyclass]
#[derive(Clone)]
struct AssignmentNode {
    inner: CoreAssignmentNode,
}

#[pymethods]
impl AssignmentNode {
    /// Get the target variable
    #[getter]
    fn target(&self) -> String {
        self.inner.target.clone()
    }

    /// Get the value expression
    #[getter]
    fn value(&self) -> String {
        self.inner.value.clone()
    }

    /// Get the node reference
    #[getter]
    fn node_ref(&self) -> AstNodeRef {
        AstNodeRef {
            inner: self.inner.node_ref.clone(),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "AssignmentNode(target='{}', value='{}')",
            self.inner.target, self.inner.value
        )
    }
}

/// Python wrapper for code generator (bottom-level API)
#[pyclass]
struct CodeGenerator {
    inner: CoreCodeGenerator,
}

#[pymethods]
impl CodeGenerator {
    /// Create a new code generator
    #[new]
    fn new() -> Self {
        Self {
            inner: CoreCodeGenerator::new(),
        }
    }

    /// Generate an import statement
    #[pyo3(signature = (module, items=None, alias=None))]
    fn create_import(
        &self,
        module: &str,
        items: Option<Vec<String>>,
        alias: Option<&str>,
    ) -> PyResult<String> {
        match self.inner.create_import(module, items, alias) {
            Ok(code) => Ok(code),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Code generation error: {}",
                e
            ))),
        }
    }

    /// Generate an assignment statement
    fn create_assignment(&self, target: &str, value: &str) -> PyResult<String> {
        match self.inner.create_assignment(target, value) {
            Ok(code) => Ok(code),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Code generation error: {}",
                e
            ))),
        }
    }

    /// Generate a function call
    fn create_function_call(&self, function: &str, args: Vec<String>) -> PyResult<String> {
        match self.inner.create_function_call(function, args) {
            Ok(code) => Ok(code),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Code generation error: {}",
                e
            ))),
        }
    }

    /// Generate a try-except block
    fn create_try_except(
        &self,
        try_body: &str,
        except_type: &str,
        except_body: &str,
    ) -> PyResult<String> {
        match self
            .inner
            .create_try_except(try_body, except_type, except_body)
        {
            Ok(code) => Ok(code),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Code generation error: {}",
                e
            ))),
        }
    }

    fn __repr__(&self) -> String {
        "CodeGenerator()".to_string()
    }
}

/// PyRustor Python module
#[pymodule]
fn _pyrustor(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Main API classes
    m.add_class::<Parser>()?;
    m.add_class::<PythonAst>()?;
    m.add_class::<Refactor>()?;

    // Bottom-level API classes
    m.add_class::<AstNodeRef>()?;
    m.add_class::<ImportNode>()?;
    m.add_class::<CallNode>()?;
    m.add_class::<TryExceptNode>()?;
    m.add_class::<AssignmentNode>()?;
    m.add_class::<CodeGenerator>()?;

    // Add version information
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;

    Ok(())
}
