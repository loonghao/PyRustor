//! Abstract Syntax Tree (AST) representation and manipulation

use crate::{error::Result, PyRustorError};
use ruff_python_ast::{ModModule, Stmt, Expr};
use serde::{Deserialize, Serialize};
use std::fmt;

/// Reference to an AST node for low-level operations
#[derive(Debug, Clone)]
pub struct AstNodeRef {
    /// Index path to the node in the AST
    pub path: Vec<usize>,
    /// Type of the node
    pub node_type: String,
    /// Source location information
    pub location: Option<SourceLocation>,
}

/// Source code location
#[derive(Debug, Clone)]
pub struct SourceLocation {
    pub line: usize,
    pub column: usize,
}

/// Import node information
#[derive(Debug, Clone)]
pub struct ImportNode {
    /// The import statement
    pub module: String,
    /// Imported items (for 'from' imports)
    pub items: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Function call node information
#[derive(Debug, Clone)]
pub struct CallNode {
    /// Function name
    pub function_name: String,
    /// Arguments (simplified)
    pub args: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Try-except block information
#[derive(Debug, Clone)]
pub struct TryExceptNode {
    /// Exception types handled
    pub exception_types: Vec<String>,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Assignment node information
#[derive(Debug, Clone)]
pub struct AssignmentNode {
    /// Target variable name
    pub target: String,
    /// Value expression (simplified)
    pub value: String,
    /// Node reference
    pub node_ref: AstNodeRef,
}

/// Represents a Python Abstract Syntax Tree with formatting information
#[derive(Debug, Clone)]
pub struct PythonAst {
    /// The root module AST node
    module: ModModule,
    /// Original source code for preserving formatting
    source: String,
    /// Whether comments are preserved
    #[allow(dead_code)]
    preserve_comments: bool,
    /// Whether formatting is preserved
    #[allow(dead_code)]
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

    /// Convert the AST back to Python source code
    pub fn to_string(&self) -> Result<String> {
        if self.module.body.is_empty() {
            return Ok(String::new());
        }

        // Generate Python code from the AST
        self.generate_code()
    }

    /// Generate Python code from the AST
    fn generate_code(&self) -> Result<String> {
        let mut code = String::new();

        for (i, stmt) in self.module.body.iter().enumerate() {
            if i > 0 {
                code.push('\n');
            }
            code.push_str(&self.generate_statement(stmt, 0)?);
        }

        Ok(code)
    }

    /// Generate code for a single statement
    fn generate_statement(&self, stmt: &ruff_python_ast::Stmt, indent: usize) -> Result<String> {
        use ruff_python_ast::Stmt;

        let indent_str = "    ".repeat(indent);

        match stmt {
            Stmt::FunctionDef(func) => {
                let mut result = format!("{}def {}(", indent_str, func.name);

                // Add parameters (simplified - defaults not fully supported yet)
                for (i, arg) in func.parameters.args.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&arg.parameter.name);

                    // Note: Default values are complex to extract from the AST
                    // For now, we'll just show the parameter name
                }

                result.push_str("):\n");

                // Add body
                if func.body.is_empty() {
                    result.push_str(&format!("{}    pass", indent_str));
                } else {
                    for (i, body_stmt) in func.body.iter().enumerate() {
                        if i > 0 {
                            result.push('\n');
                        }
                        result.push_str(&self.generate_statement(body_stmt, indent + 1)?);
                    }
                }

                Ok(result)
            }

            Stmt::ClassDef(class) => {
                let mut result = format!("{}class {}", indent_str, class.name);

                // Add base classes
                if !class.bases().is_empty() {
                    result.push('(');
                    for (i, base) in class.bases().iter().enumerate() {
                        if i > 0 {
                            result.push_str(", ");
                        }
                        result.push_str(&self.generate_expression(base)?);
                    }
                    result.push(')');
                }

                result.push_str(":\n");

                // Add body
                if class.body.is_empty() {
                    result.push_str(&format!("{}    pass", indent_str));
                } else {
                    for (i, body_stmt) in class.body.iter().enumerate() {
                        if i > 0 {
                            result.push('\n');
                        }
                        result.push_str(&self.generate_statement(body_stmt, indent + 1)?);
                    }
                }

                Ok(result)
            }

            Stmt::Return(ret) => {
                let mut result = format!("{}return", indent_str);
                if let Some(value) = &ret.value {
                    result.push(' ');
                    result.push_str(&self.generate_expression(value)?);
                }
                Ok(result)
            }

            Stmt::Pass(_) => Ok(format!("{}pass", indent_str)),

            Stmt::Expr(expr) => {
                let expr_code = self.generate_expression(&expr.value)?;
                Ok(format!("{}{}", indent_str, expr_code))
            }

            Stmt::Import(import) => {
                let mut result = format!("{}import ", indent_str);
                for (i, alias) in import.names.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&alias.name);
                    if let Some(asname) = &alias.asname {
                        result.push_str(" as ");
                        result.push_str(asname);
                    }
                }
                Ok(result)
            }

            Stmt::ImportFrom(import_from) => {
                let mut result = String::new();
                result.push_str(&indent_str);
                result.push_str("from ");

                if let Some(module) = &import_from.module {
                    result.push_str(module);
                } else {
                    result.push('.');
                }

                result.push_str(" import ");

                for (i, alias) in import_from.names.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&alias.name);
                    if let Some(asname) = &alias.asname {
                        result.push_str(" as ");
                        result.push_str(asname);
                    }
                }
                Ok(result)
            }

            Stmt::Assign(assign) => {
                let mut result = format!("{}", indent_str);

                // Handle targets (left side of assignment)
                for (i, target) in assign.targets.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&self.generate_expression(target)?);
                }

                result.push_str(" = ");
                result.push_str(&self.generate_expression(&assign.value)?);
                Ok(result)
            }

            // Add more statement types as needed
            _ => {
                // For unsupported statements, return a placeholder
                Ok(format!("{}# Unsupported statement type", indent_str))
            }
        }
    }

    /// Generate code for an expression
    fn generate_expression(&self, expr: &ruff_python_ast::Expr) -> Result<String> {
        use ruff_python_ast::Expr;

        match expr {
            Expr::Name(name) => Ok(name.id.to_string()),
            Expr::StringLiteral(s) => {
                // Handle string literals with proper escaping
                let content = s.value.to_str();
                let escaped = content
                    .replace('\\', "\\\\")
                    .replace('"', "\\\"")
                    .replace('\n', "\\n")
                    .replace('\r', "\\r")
                    .replace('\t', "\\t");
                Ok(format!("\"{}\"", escaped))
            }
            Expr::NumberLiteral(n) => {
                use ruff_python_ast::Number;
                match &n.value {
                    Number::Int(i) => Ok(i.to_string()),
                    Number::Float(f) => Ok(f.to_string()),
                    Number::Complex { real, imag } => Ok(format!("({real}+{imag}j)")),
                }
            }
            Expr::Call(call) => {
                let mut result = self.generate_expression(&call.func)?;
                result.push('(');

                for (i, arg) in call.arguments.args.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&self.generate_expression(arg)?);
                }

                result.push(')');
                Ok(result)
            }

            Expr::FString(_f_string) => {
                // F-string literal - simplified representation
                // For now, just return a placeholder since f-strings are complex
                Ok("f\"...\"".to_string())
            }

            Expr::BinOp(binop) => {
                // Binary operations like +, -, *, etc.
                let left = self.generate_expression(&binop.left)?;
                let right = self.generate_expression(&binop.right)?;
                let op = match binop.op {
                    ruff_python_ast::Operator::Add => "+",
                    ruff_python_ast::Operator::Sub => "-",
                    ruff_python_ast::Operator::Mult => "*",
                    ruff_python_ast::Operator::Div => "/",
                    ruff_python_ast::Operator::Mod => "%",
                    ruff_python_ast::Operator::Pow => "**",
                    ruff_python_ast::Operator::LShift => "<<",
                    ruff_python_ast::Operator::RShift => ">>",
                    ruff_python_ast::Operator::BitOr => "|",
                    ruff_python_ast::Operator::BitXor => "^",
                    ruff_python_ast::Operator::BitAnd => "&",
                    ruff_python_ast::Operator::FloorDiv => "//",
                    ruff_python_ast::Operator::MatMult => "@",
                };
                Ok(format!("{} {} {}", left, op, right))
            }

            Expr::Attribute(attr) => {
                // Attribute access like obj.attr
                let value = self.generate_expression(&attr.value)?;
                Ok(format!("{}.{}", value, attr.attr))
            }

            Expr::Subscript(subscript) => {
                // Subscript access like obj[key]
                let value = self.generate_expression(&subscript.value)?;
                let slice = self.generate_expression(&subscript.slice)?;
                Ok(format!("{}[{}]", value, slice))
            }

            // Add more expression types as needed
            _ => Ok("# Unsupported expression".to_string()),
        }
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

    /// Get names of all functions in the module (including methods in classes)
    pub fn function_names(&self) -> Vec<String> {
        let mut names = Vec::new();
        self.collect_function_names_recursive(&self.module.body, &mut names);
        names
    }

    /// Recursively collect function names from statements
    fn collect_function_names_recursive(&self, stmts: &[Stmt], names: &mut Vec<String>) {
        for stmt in stmts {
            match stmt {
                Stmt::FunctionDef(func) => {
                    names.push(func.name.to_string());
                }
                Stmt::ClassDef(class) => {
                    // Recursively search in class body for methods
                    self.collect_function_names_recursive(&class.body, names);
                }
                _ => {}
            }
        }
    }

    /// Get names of all classes in the module
    pub fn class_names(&self) -> Vec<String> {
        self.classes()
            .iter()
            .map(|class| class.name.to_string())
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

    /// Find nodes matching specific criteria (bottom-level API)
    pub fn find_nodes(&self, node_type: Option<&str>) -> Vec<AstNodeRef> {
        let mut nodes = Vec::new();
        self.find_nodes_recursive(&self.module.body, &mut Vec::new(), &mut nodes, node_type);
        nodes
    }

    /// Find import statements
    pub fn find_imports(&self, module_pattern: Option<&str>) -> Vec<ImportNode> {
        let mut imports = Vec::new();

        for (i, stmt) in self.module.body.iter().enumerate() {
            match stmt {
                Stmt::Import(import_stmt) => {
                    for alias in &import_stmt.names {
                        let module_name = alias.name.to_string();
                        if module_pattern.is_none() || module_name.contains(module_pattern.unwrap()) {
                            imports.push(ImportNode {
                                module: module_name,
                                items: vec![],
                                node_ref: AstNodeRef {
                                    path: vec![i],
                                    node_type: "import".to_string(),
                                    location: None,
                                },
                            });
                        }
                    }
                }
                Stmt::ImportFrom(from_import) => {
                    if let Some(module) = &from_import.module {
                        let module_name = module.to_string();
                        if module_pattern.is_none() || module_name.contains(module_pattern.unwrap()) {
                            let items: Vec<String> = from_import.names.iter()
                                .map(|alias| alias.name.to_string())
                                .collect();

                            imports.push(ImportNode {
                                module: module_name,
                                items,
                                node_ref: AstNodeRef {
                                    path: vec![i],
                                    node_type: "import_from".to_string(),
                                    location: None,
                                },
                            });
                        }
                    }
                }
                _ => {}
            }
        }

        imports
    }

    /// Find function calls
    pub fn find_function_calls(&self, function_name: &str) -> Vec<CallNode> {
        let mut calls = Vec::new();
        self.find_function_calls_recursive(&self.module.body, &mut Vec::new(), &mut calls, function_name);
        calls
    }

    /// Find try-except blocks
    pub fn find_try_except_blocks(&self, exception_type: Option<&str>) -> Vec<TryExceptNode> {
        let mut blocks = Vec::new();
        self.find_try_except_recursive(&self.module.body, &mut Vec::new(), &mut blocks, exception_type);
        blocks
    }

    /// Find assignment statements
    pub fn find_assignments(&self, target_pattern: Option<&str>) -> Vec<AssignmentNode> {
        let mut assignments = Vec::new();
        self.find_assignments_recursive(&self.module.body, &mut Vec::new(), &mut assignments, target_pattern);
        assignments
    }

    /// Validate the AST structure
    pub fn validate(&self) -> Result<()> {
        // Basic validation - in a full implementation this would be more comprehensive
        if self.module.body.is_empty() {
            return Err(PyRustorError::ast_error("Empty module"));
        }
        Ok(())
    }

    // Private helper methods for recursive AST traversal

    fn find_nodes_recursive(
        &self,
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        nodes: &mut Vec<AstNodeRef>,
        node_type: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            let stmt_type = match stmt {
                Stmt::FunctionDef(_) => "function_def",
                Stmt::ClassDef(_) => "class_def",
                Stmt::Import(_) => "import",
                Stmt::ImportFrom(_) => "import_from",
                Stmt::Try(_) => "try_except",
                Stmt::Assign(_) => "assign",
                _ => "other",
            };

            if node_type.is_none() || node_type == Some(stmt_type) {
                nodes.push(AstNodeRef {
                    path: path.clone(),
                    node_type: stmt_type.to_string(),
                    location: None,
                });
            }

            // Recursively search nested statements
            match stmt {
                Stmt::FunctionDef(func) => {
                    self.find_nodes_recursive(&func.body, path, nodes, node_type);
                }
                Stmt::ClassDef(class) => {
                    self.find_nodes_recursive(&class.body, path, nodes, node_type);
                }
                Stmt::Try(try_stmt) => {
                    self.find_nodes_recursive(&try_stmt.body, path, nodes, node_type);
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                self.find_nodes_recursive(&eh.body, path, nodes, node_type);
                            }
                        }
                    }
                    self.find_nodes_recursive(&try_stmt.orelse, path, nodes, node_type);
                    self.find_nodes_recursive(&try_stmt.finalbody, path, nodes, node_type);
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_function_calls_recursive(
        &self,
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        calls: &mut Vec<CallNode>,
        function_name: &str,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            // Search for function calls in expressions
            self.find_calls_in_stmt(stmt, path, calls, function_name);

            // Recursively search nested statements
            match stmt {
                Stmt::FunctionDef(func) => {
                    self.find_function_calls_recursive(&func.body, path, calls, function_name);
                }
                Stmt::ClassDef(class) => {
                    self.find_function_calls_recursive(&class.body, path, calls, function_name);
                }
                Stmt::Try(try_stmt) => {
                    self.find_function_calls_recursive(&try_stmt.body, path, calls, function_name);
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                self.find_function_calls_recursive(&eh.body, path, calls, function_name);
                            }
                        }
                    }
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_calls_in_stmt(
        &self,
        stmt: &Stmt,
        path: &[usize],
        calls: &mut Vec<CallNode>,
        function_name: &str,
    ) {
        match stmt {
            Stmt::Assign(assign) => {
                self.find_calls_in_expr(&assign.value, path, calls, function_name);
            }
            Stmt::Expr(expr) => {
                self.find_calls_in_expr(&expr.value, path, calls, function_name);
            }
            _ => {}
        }
    }

    fn find_calls_in_expr(
        &self,
        expr: &Expr,
        path: &[usize],
        calls: &mut Vec<CallNode>,
        function_name: &str,
    ) {
        match expr {
            Expr::Call(call) => {
                // Check direct function calls
                if let Expr::Name(name) = &*call.func {
                    if name.id.as_str() == function_name {
                        calls.push(CallNode {
                            function_name: function_name.to_string(),
                            args: vec![], // Simplified - would extract actual args
                            node_ref: AstNodeRef {
                                path: path.to_vec(),
                                node_type: "call".to_string(),
                                location: None,
                            },
                        });
                    }
                }
                // Also check attribute calls like module.function()
                if let Expr::Attribute(attr) = &*call.func {
                    if attr.attr.as_str() == function_name {
                        calls.push(CallNode {
                            function_name: function_name.to_string(),
                            args: vec![],
                            node_ref: AstNodeRef {
                                path: path.to_vec(),
                                node_type: "call".to_string(),
                                location: None,
                            },
                        });
                    }
                }

                // Recursively search in arguments
                for arg in &call.arguments.args {
                    self.find_calls_in_expr(arg, path, calls, function_name);
                }
            }
            Expr::Attribute(attr) => {
                // Recursively search in the value of attribute access
                // This handles cases like get_distribution(__name__).version
                self.find_calls_in_expr(&attr.value, path, calls, function_name);
            }
            Expr::BinOp(binop) => {
                // Search in binary operations
                self.find_calls_in_expr(&binop.left, path, calls, function_name);
                self.find_calls_in_expr(&binop.right, path, calls, function_name);
            }
            Expr::UnaryOp(unaryop) => {
                // Search in unary operations
                self.find_calls_in_expr(&unaryop.operand, path, calls, function_name);
            }
            Expr::Compare(compare) => {
                // Search in comparisons
                self.find_calls_in_expr(&compare.left, path, calls, function_name);
                for comparator in &compare.comparators {
                    self.find_calls_in_expr(comparator, path, calls, function_name);
                }
            }
            Expr::BoolOp(boolop) => {
                // Search in boolean operations
                for value in &boolop.values {
                    self.find_calls_in_expr(value, path, calls, function_name);
                }
            }
            Expr::Subscript(subscript) => {
                // Search in subscript operations
                self.find_calls_in_expr(&subscript.value, path, calls, function_name);
                self.find_calls_in_expr(&subscript.slice, path, calls, function_name);
            }
            _ => {}
        }
    }

    fn find_try_except_recursive(
        &self,
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        blocks: &mut Vec<TryExceptNode>,
        exception_type: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            if let Stmt::Try(try_stmt) = stmt {
                let mut exception_types = Vec::new();
                for handler in &try_stmt.handlers {
                    match handler {
                        ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                            if let Some(exc_type) = &eh.type_ {
                                if let Expr::Name(name) = &**exc_type {
                                    exception_types.push(name.id.to_string());
                                }
                            }
                        }
                    }
                }

                let matches = if let Some(target_type) = exception_type {
                    exception_types.iter().any(|t| t == target_type)
                } else {
                    true
                };

                if matches {
                    blocks.push(TryExceptNode {
                        exception_types,
                        node_ref: AstNodeRef {
                            path: path.clone(),
                            node_type: "try_except".to_string(),
                            location: None,
                        },
                    });
                }

                // Recursively search nested statements
                self.find_try_except_recursive(&try_stmt.body, path, blocks, exception_type);
                for handler in &try_stmt.handlers {
                    match handler {
                        ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                            self.find_try_except_recursive(&eh.body, path, blocks, exception_type);
                        }
                    }
                }
            }

            // Search in other nested statements
            match stmt {
                Stmt::FunctionDef(func) => {
                    self.find_try_except_recursive(&func.body, path, blocks, exception_type);
                }
                Stmt::ClassDef(class) => {
                    self.find_try_except_recursive(&class.body, path, blocks, exception_type);
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_assignments_recursive(
        &self,
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        assignments: &mut Vec<AssignmentNode>,
        target_pattern: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            if let Stmt::Assign(assign) = stmt {
                for target in &assign.targets {
                    if let Expr::Name(name) = target {
                        let target_name = name.id.to_string();
                        let matches = if let Some(pattern) = target_pattern {
                            target_name.contains(pattern)
                        } else {
                            true
                        };

                        if matches {
                            assignments.push(AssignmentNode {
                                target: target_name,
                                value: "...".to_string(), // Simplified - would extract actual value
                                node_ref: AstNodeRef {
                                    path: path.clone(),
                                    node_type: "assign".to_string(),
                                    location: None,
                                },
                            });
                        }
                    }
                }
            }

            // Recursively search nested statements
            match stmt {
                Stmt::FunctionDef(func) => {
                    self.find_assignments_recursive(&func.body, path, assignments, target_pattern);
                }
                Stmt::ClassDef(class) => {
                    self.find_assignments_recursive(&class.body, path, assignments, target_pattern);
                }
                Stmt::Try(try_stmt) => {
                    self.find_assignments_recursive(&try_stmt.body, path, assignments, target_pattern);
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                self.find_assignments_recursive(&eh.body, path, assignments, target_pattern);
                            }
                        }
                    }
                }
                _ => {}
            }

            path.pop();
        }
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

    #[test]
    fn test_empty_ast() -> Result<()> {
        let parser = Parser::new();
        let ast = parser.parse_string("")?;

        assert!(ast.is_empty());
        assert_eq!(ast.statement_count(), 0);
        assert_eq!(ast.function_names().len(), 0);
        assert_eq!(ast.class_names().len(), 0);
        assert_eq!(ast.imports().len(), 0);
        Ok(())
    }

    #[test]
    fn test_ast_to_string() -> Result<()> {
        let parser = Parser::new();
        let code = "def hello():\n    return 'world'";
        let ast = parser.parse_string(code)?;

        let result = ast.to_string()?;
        assert!(result.contains("hello"));
        assert!(result.contains("world"));
        Ok(())
    }

    #[test]
    fn test_complex_ast_structure() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
import os
from typing import List

class DataProcessor:
    def __init__(self, name: str):
        self.name = name

    def process(self, data: List[str]) -> List[str]:
        return [item.upper() for item in data]

def main():
    processor = DataProcessor("test")
    result = processor.process(["hello", "world"])
    print(result)

if __name__ == "__main__":
    main()
"#;
        let ast = parser.parse_string(code)?;

        assert!(!ast.is_empty());
        assert!(ast.statement_count() > 0);

        // Check functions
        let function_names = ast.function_names();
        assert!(function_names.contains(&"main".to_string()));

        // Check classes
        let class_names = ast.class_names();
        assert!(class_names.contains(&"DataProcessor".to_string()));

        // Check imports
        let imports = ast.imports();
        assert!(!imports.is_empty());

        Ok(())
    }

    #[test]
    fn test_nested_functions_and_classes() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
class OuterClass:
    def outer_method(self):
        def inner_function():
            return "inner"
        return inner_function()

    class InnerClass:
        pass

def outer_function():
    def nested_function():
        def deeply_nested():
            return "deep"
        return deeply_nested()
    return nested_function()
"#;
        let ast = parser.parse_string(code)?;

        // Only top-level functions and classes should be counted
        let function_names = ast.function_names();
        assert_eq!(function_names.len(), 1);
        assert!(function_names.contains(&"outer_function".to_string()));

        let class_names = ast.class_names();
        assert_eq!(class_names.len(), 1);
        assert!(class_names.contains(&"OuterClass".to_string()));

        Ok(())
    }

    #[test]
    fn test_unicode_identifiers() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
def greet_世界():
    return "Hello 世界!"

class UnicodeClass_测试:
    def method_测试(self):
        return "测试"
"#;
        let ast = parser.parse_string(code)?;

        let function_names = ast.function_names();
        assert!(function_names.contains(&"greet_世界".to_string()));

        let class_names = ast.class_names();
        assert!(class_names.contains(&"UnicodeClass_测试".to_string()));

        Ok(())
    }

    #[test]
    fn test_various_import_styles() -> Result<()> {
        let parser = Parser::new();
        let code = r#"
import os
import sys as system
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict as dd, OrderedDict
import json, csv, xml.etree.ElementTree as ET
"#;
        let ast = parser.parse_string(code)?;

        let imports = ast.imports();
        assert!(!imports.is_empty());

        // Should have multiple import statements
        assert!(imports.len() >= 5);

        Ok(())
    }

    #[test]
    fn test_ast_modification_tracking() -> Result<()> {
        let parser = Parser::new();
        let mut ast = parser.parse_string("def original(): pass")?;

        // Get original source
        let original_source = ast.source();
        assert!(original_source.contains("original"));

        // Modify the AST (this would be done by refactor operations)
        // For now, just test that we can access the mutable AST
        let _module = ast.module_mut();

        Ok(())
    }

    #[test]
    fn test_large_ast() -> Result<()> {
        let parser = Parser::new();

        // Generate a large Python file
        let mut large_code = String::new();
        for i in 0..100 {
            large_code.push_str(&format!("def function_{}(): return {}\n", i, i));
            large_code.push_str(&format!("class Class_{}: pass\n", i));
        }

        let ast = parser.parse_string(&large_code)?;

        assert!(!ast.is_empty());
        assert_eq!(ast.statement_count(), 200); // 100 functions + 100 classes

        let function_names = ast.function_names();
        assert_eq!(function_names.len(), 100);

        let class_names = ast.class_names();
        assert_eq!(class_names.len(), 100);

        Ok(())
    }

    #[test]
    fn test_ast_source_preservation() -> Result<()> {
        let parser = Parser::new();
        let original_code = r#"def hello():
    """A simple function."""
    return "Hello, World!"

class Greeter:
    """A simple class."""

    def greet(self):
        return hello()
"#;
        let ast = parser.parse_string(original_code)?;

        // The source should be preserved
        let source = ast.source();
        assert_eq!(source, original_code);

        Ok(())
    }

    #[test]
    fn test_ast_error_handling() -> Result<()> {
        let parser = Parser::new();

        // Test that we can create an AST and handle edge cases
        let ast = parser.parse_string("pass")?;

        // These operations should not panic
        let _ = ast.function_names();
        let _ = ast.class_names();
        let _ = ast.imports();
        let _ = ast.to_string();

        Ok(())
    }
}
