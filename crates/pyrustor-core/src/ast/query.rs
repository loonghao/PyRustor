//! AST query functionality

use super::{core::PythonAst, nodes::*};
use ruff_python_ast::{Expr, Stmt};

impl PythonAst {
    /// Find nodes matching specific criteria (bottom-level API)
    pub fn find_nodes(&self, node_type: Option<&str>) -> Vec<AstNodeRef> {
        let mut nodes = Vec::new();
        Self::find_nodes_recursive(&self.module.body, &mut Vec::new(), &mut nodes, node_type);
        nodes
    }

    /// Find import statements
    pub fn find_imports(&self, module_pattern: Option<&str>) -> Vec<ImportNode> {
        let mut imports = Vec::new();

        for (i, stmt) in self.module.body.iter().enumerate() {
            match stmt {
                Stmt::Import(import) => {
                    for alias in &import.names {
                        let module_name = alias.name.to_string();
                        if let Some(pattern) = module_pattern {
                            if !module_name.contains(pattern) {
                                continue;
                            }
                        }

                        imports.push(ImportNode {
                            module: module_name,
                            items: vec![],
                            node_ref: AstNodeRef {
                                path: vec![i],
                                node_type: "Import".to_string(),
                                location: None,
                            },
                        });
                    }
                }
                Stmt::ImportFrom(import_from) => {
                    if let Some(module) = &import_from.module {
                        let module_name = module.to_string();
                        if let Some(pattern) = module_pattern {
                            if !module_name.contains(pattern) {
                                continue;
                            }
                        }

                        let items: Vec<String> = import_from
                            .names
                            .iter()
                            .map(|alias| alias.name.to_string())
                            .collect();

                        imports.push(ImportNode {
                            module: module_name,
                            items,
                            node_ref: AstNodeRef {
                                path: vec![i],
                                node_type: "ImportFrom".to_string(),
                                location: None,
                            },
                        });
                    }
                }
                _ => {}
            }
        }

        imports
    }

    /// Find function calls
    pub fn find_function_calls(&self, function_name: Option<&str>) -> Vec<CallNode> {
        let mut calls = Vec::new();
        Self::find_calls_recursive(
            &self.module.body,
            &mut Vec::new(),
            &mut calls,
            function_name,
        );
        calls
    }

    /// Find try-except blocks
    pub fn find_try_except_blocks(&self, exception_type: Option<&str>) -> Vec<TryExceptNode> {
        let mut blocks = Vec::new();
        Self::find_try_except_recursive(
            &self.module.body,
            &mut Vec::new(),
            &mut blocks,
            exception_type,
        );
        blocks
    }

    /// Find assignment statements
    pub fn find_assignments(&self, target_pattern: Option<&str>) -> Vec<AssignmentNode> {
        let mut assignments = Vec::new();
        Self::find_assignments_recursive(
            &self.module.body,
            &mut Vec::new(),
            &mut assignments,
            target_pattern,
        );
        assignments
    }

    // Private helper methods for recursive AST traversal

    fn find_nodes_recursive(
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        nodes: &mut Vec<AstNodeRef>,
        node_type: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            // Check if this node matches the criteria
            let stmt_type = match stmt {
                Stmt::FunctionDef(_) => "FunctionDef",
                Stmt::ClassDef(_) => "ClassDef",
                Stmt::Import(_) => "Import",
                Stmt::ImportFrom(_) => "ImportFrom",
                Stmt::Assign(_) => "Assign",
                Stmt::Try(_) => "Try",
                _ => "Other",
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
                    Self::find_nodes_recursive(&func.body, path, nodes, node_type);
                }
                Stmt::ClassDef(class) => {
                    Self::find_nodes_recursive(&class.body, path, nodes, node_type);
                }
                Stmt::Try(try_stmt) => {
                    Self::find_nodes_recursive(&try_stmt.body, path, nodes, node_type);
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                Self::find_nodes_recursive(&eh.body, path, nodes, node_type);
                            }
                        }
                    }
                    Self::find_nodes_recursive(&try_stmt.orelse, path, nodes, node_type);
                    Self::find_nodes_recursive(&try_stmt.finalbody, path, nodes, node_type);
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_calls_recursive(
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        calls: &mut Vec<CallNode>,
        function_name: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            // Search for function calls in expressions
            match stmt {
                Stmt::Expr(expr) => {
                    Self::find_calls_in_expr(&expr.value, path, calls, function_name);
                }
                Stmt::Assign(assign) => {
                    Self::find_calls_in_expr(&assign.value, path, calls, function_name);
                }
                Stmt::Return(ret) => {
                    if let Some(value) = &ret.value {
                        Self::find_calls_in_expr(value, path, calls, function_name);
                    }
                }
                Stmt::FunctionDef(func) => {
                    Self::find_calls_recursive(&func.body, path, calls, function_name);
                }
                Stmt::ClassDef(class) => {
                    Self::find_calls_recursive(&class.body, path, calls, function_name);
                }
                Stmt::Try(try_stmt) => {
                    Self::find_calls_recursive(&try_stmt.body, path, calls, function_name);
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                Self::find_calls_recursive(&eh.body, path, calls, function_name);
                            }
                        }
                    }
                    Self::find_calls_recursive(&try_stmt.orelse, path, calls, function_name);
                    Self::find_calls_recursive(&try_stmt.finalbody, path, calls, function_name);
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_calls_in_expr(
        expr: &Expr,
        path: &[usize],
        calls: &mut Vec<CallNode>,
        function_name: Option<&str>,
    ) {
        match expr {
            Expr::Call(call) => {
                // Extract function name from the call
                let func_name = match &*call.func {
                    Expr::Name(name) => name.id.to_string(),
                    Expr::Attribute(attr) => {
                        // Handle method calls like obj.method()
                        format!("{}.{}", Self::expr_to_string(&attr.value), attr.attr)
                    }
                    _ => "unknown".to_string(),
                };

                // Check if this matches the search criteria
                if function_name.is_none() || function_name == Some(&func_name) {
                    let args: Vec<String> = call
                        .arguments
                        .args
                        .iter()
                        .map(Self::expr_to_string)
                        .collect();

                    calls.push(CallNode {
                        function_name: func_name,
                        args,
                        node_ref: AstNodeRef {
                            path: path.to_vec(),
                            node_type: "Call".to_string(),
                            location: None,
                        },
                    });
                }

                // Recursively search in arguments
                for arg in &call.arguments.args {
                    Self::find_calls_in_expr(arg, path, calls, function_name);
                }
            }
            Expr::Attribute(attr) => {
                Self::find_calls_in_expr(&attr.value, path, calls, function_name);
            }
            Expr::BinOp(binop) => {
                Self::find_calls_in_expr(&binop.left, path, calls, function_name);
                Self::find_calls_in_expr(&binop.right, path, calls, function_name);
            }
            Expr::UnaryOp(unaryop) => {
                Self::find_calls_in_expr(&unaryop.operand, path, calls, function_name);
            }
            Expr::Compare(compare) => {
                Self::find_calls_in_expr(&compare.left, path, calls, function_name);
                for comparator in &compare.comparators {
                    Self::find_calls_in_expr(comparator, path, calls, function_name);
                }
            }
            Expr::List(list) => {
                for value in &list.elts {
                    Self::find_calls_in_expr(value, path, calls, function_name);
                }
            }
            Expr::Subscript(subscript) => {
                Self::find_calls_in_expr(&subscript.value, path, calls, function_name);
                Self::find_calls_in_expr(&subscript.slice, path, calls, function_name);
            }
            _ => {}
        }
    }

    fn find_try_except_recursive(
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        blocks: &mut Vec<TryExceptNode>,
        exception_type: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            match stmt {
                Stmt::Try(try_stmt) => {
                    let mut exception_types = Vec::new();

                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                if let Some(exc_type) = &eh.type_ {
                                    let type_name = Self::expr_to_string(exc_type);
                                    exception_types.push(type_name.clone());

                                    // Check if this matches the search criteria
                                    if exception_type.is_none()
                                        || exception_type == Some(&type_name)
                                    {
                                        blocks.push(TryExceptNode {
                                            exception_types: vec![type_name],
                                            node_ref: AstNodeRef {
                                                path: path.clone(),
                                                node_type: "Try".to_string(),
                                                location: None,
                                            },
                                        });
                                    }
                                }
                                Self::find_try_except_recursive(
                                    &eh.body,
                                    path,
                                    blocks,
                                    exception_type,
                                );
                            }
                        }
                    }

                    Self::find_try_except_recursive(&try_stmt.body, path, blocks, exception_type);
                }
                Stmt::FunctionDef(func) => {
                    Self::find_try_except_recursive(&func.body, path, blocks, exception_type);
                }
                Stmt::ClassDef(class) => {
                    Self::find_try_except_recursive(&class.body, path, blocks, exception_type);
                }
                _ => {}
            }

            path.pop();
        }
    }

    fn find_assignments_recursive(
        stmts: &[Stmt],
        path: &mut Vec<usize>,
        assignments: &mut Vec<AssignmentNode>,
        target_pattern: Option<&str>,
    ) {
        for (i, stmt) in stmts.iter().enumerate() {
            path.push(i);

            match stmt {
                Stmt::Assign(assign) => {
                    for target in &assign.targets {
                        let target_name = Self::expr_to_string(target);

                        // Check if this matches the search criteria
                        if target_pattern.is_none() || target_name.contains(target_pattern.unwrap())
                        {
                            assignments.push(AssignmentNode {
                                target: target_name,
                                value: Self::expr_to_string(&assign.value),
                                node_ref: AstNodeRef {
                                    path: path.clone(),
                                    node_type: "Assign".to_string(),
                                    location: None,
                                },
                            });
                        }
                    }
                }
                Stmt::FunctionDef(func) => {
                    Self::find_assignments_recursive(&func.body, path, assignments, target_pattern);
                }
                Stmt::ClassDef(class) => {
                    Self::find_assignments_recursive(
                        &class.body,
                        path,
                        assignments,
                        target_pattern,
                    );
                }
                Stmt::Try(try_stmt) => {
                    Self::find_assignments_recursive(
                        &try_stmt.body,
                        path,
                        assignments,
                        target_pattern,
                    );
                    for handler in &try_stmt.handlers {
                        match handler {
                            ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                                Self::find_assignments_recursive(
                                    &eh.body,
                                    path,
                                    assignments,
                                    target_pattern,
                                );
                            }
                        }
                    }
                }
                _ => {}
            }

            path.pop();
        }
    }

    /// Helper method to convert expressions to strings (simplified)
    fn expr_to_string(expr: &Expr) -> String {
        match expr {
            Expr::Name(name) => name.id.to_string(),
            Expr::StringLiteral(s) => format!("\"{}\"", s.value),
            Expr::NumberLiteral(n) => format!("{:?}", n.value),
            Expr::Attribute(attr) => {
                format!("{}.{}", Self::expr_to_string(&attr.value), attr.attr)
            }
            Expr::Call(call) => {
                let func_name = Self::expr_to_string(&call.func);
                let args: Vec<String> = call
                    .arguments
                    .args
                    .iter()
                    .map(Self::expr_to_string)
                    .collect();
                format!("{}({})", func_name, args.join(", "))
            }
            _ => "unknown".to_string(),
        }
    }
}
