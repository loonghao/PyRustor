//! AST code generation functionality

use super::core::PythonAst;
use crate::{error::Result, PyRustorError};
use ruff_python_ast::Stmt;

impl PythonAst {
    /// Generate code for the entire AST
    pub fn to_code(&self) -> Result<String> {
        let mut result = String::new();

        for stmt in &self.module.body {
            let stmt_code = self.generate_statement(stmt, 0)?;
            result.push_str(&stmt_code);
            result.push('\n');
        }

        Ok(result)
    }

    /// Generate code for a single statement
    pub fn generate_statement(&self, stmt: &Stmt, indent_level: usize) -> Result<String> {
        Self::generate_statement_impl(stmt, indent_level)
    }

    /// Internal implementation for statement generation
    fn generate_statement_impl(stmt: &Stmt, indent_level: usize) -> Result<String> {
        let indent_str = "    ".repeat(indent_level);

        match stmt {
            Stmt::FunctionDef(func) => {
                let mut result = format!("{}def {}(", indent_str, func.name);

                // Add parameters
                for (i, arg) in func.parameters.args.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&arg.parameter.name);
                }

                result.push_str("):\n");

                // Add function body
                if func.body.is_empty() {
                    result.push_str(&format!("{}    pass\n", indent_str));
                } else {
                    for body_stmt in &func.body {
                        let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                        result.push_str(&body_code);
                        result.push('\n');
                    }
                }

                Ok(result)
            }

            Stmt::ClassDef(class) => {
                let mut result = format!("{}class {}", indent_str, class.name);

                // Add base classes if any
                if !class.bases().is_empty() {
                    result.push('(');
                    for (i, base) in class.bases().iter().enumerate() {
                        if i > 0 {
                            result.push_str(", ");
                        }
                        result.push_str(&Self::generate_expression(base)?);
                    }
                    result.push(')');
                }

                result.push_str(":\n");

                // Add class body
                if class.body.is_empty() {
                    result.push_str(&format!("{}    pass\n", indent_str));
                } else {
                    for body_stmt in &class.body {
                        let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                        result.push_str(&body_code);
                        result.push('\n');
                    }
                }

                Ok(result)
            }

            Stmt::Return(ret) => {
                let mut result = format!("{}return", indent_str);
                if let Some(value) = &ret.value {
                    result.push(' ');
                    result.push_str(&Self::generate_expression(value)?);
                }
                Ok(result)
            }

            Stmt::Pass(_) => Ok(format!("{}pass", indent_str)),

            Stmt::Expr(expr) => {
                let expr_code = Self::generate_expression(&expr.value)?;
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
                let mut result = format!("{}from ", indent_str);
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
                let mut result = indent_str.to_string();

                // Handle targets (left side of assignment)
                for (i, target) in assign.targets.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(target)?);
                }

                result.push_str(" = ");
                result.push_str(&Self::generate_expression(&assign.value)?);
                Ok(result)
            }

            // Add more statement types as needed
            _ => Err(PyRustorError::ast_error(format!(
                "Unsupported statement type: {:?}",
                std::mem::discriminant(stmt)
            ))),
        }
    }

    /// Generate code for an expression
    fn generate_expression(expr: &ruff_python_ast::Expr) -> Result<String> {
        use ruff_python_ast::Expr;

        match expr {
            Expr::Name(name) => Ok(name.id.to_string()),

            Expr::StringLiteral(s) => {
                // Simple string literal generation
                Ok(format!("\"{}\"", s.value))
            }

            Expr::NumberLiteral(n) => Ok(format!("{:?}", n.value)),

            Expr::BooleanLiteral(b) => Ok(if b.value { "True" } else { "False" }.to_string()),

            Expr::NoneLiteral(_) => Ok("None".to_string()),

            Expr::Call(call) => {
                let mut result = Self::generate_expression(&call.func)?;
                result.push('(');

                for (i, arg) in call.arguments.args.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(arg)?);
                }

                result.push(')');
                Ok(result)
            }

            Expr::BinOp(binop) => {
                // Binary operations like +, -, *, etc.
                let left = Self::generate_expression(&binop.left)?;
                let right = Self::generate_expression(&binop.right)?;
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
                let value = Self::generate_expression(&attr.value)?;
                Ok(format!("{}.{}", value, attr.attr))
            }
            Expr::Subscript(subscript) => {
                // Subscript access like obj[key]
                let value = Self::generate_expression(&subscript.value)?;
                let slice = Self::generate_expression(&subscript.slice)?;
                Ok(format!("{}[{}]", value, slice))
            }

            // Add more expression types as needed
            _ => Err(PyRustorError::ast_error(format!(
                "Unsupported expression type: {:?}",
                std::mem::discriminant(expr)
            ))),
        }
    }
}
