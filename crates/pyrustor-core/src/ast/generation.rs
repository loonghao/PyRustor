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

            Stmt::Assign(assign) => {
                let mut result = String::new();
                result.push_str(&indent_str);

                // Generate targets (left side of assignment)
                for (i, target) in assign.targets.iter().enumerate() {
                    if i > 0 {
                        result.push_str(" = ");
                    }
                    result.push_str(&Self::generate_expression(target)?);
                }

                result.push_str(" = ");

                // Generate value (right side of assignment)
                result.push_str(&Self::generate_expression(&assign.value)?);

                Ok(result)
            }

            Stmt::AugAssign(aug_assign) => {
                // Augmented assignment (+=, -=, *=, etc.)
                let mut result = String::new();
                result.push_str(&indent_str);

                // Generate target (left side)
                result.push_str(&Self::generate_expression(&aug_assign.target)?);

                // Generate operator
                let op_str = match aug_assign.op {
                    ruff_python_ast::Operator::Add => " += ",
                    ruff_python_ast::Operator::Sub => " -= ",
                    ruff_python_ast::Operator::Mult => " *= ",
                    ruff_python_ast::Operator::Div => " /= ",
                    ruff_python_ast::Operator::Mod => " %= ",
                    ruff_python_ast::Operator::Pow => " **= ",
                    ruff_python_ast::Operator::LShift => " <<= ",
                    ruff_python_ast::Operator::RShift => " >>= ",
                    ruff_python_ast::Operator::BitOr => " |= ",
                    ruff_python_ast::Operator::BitXor => " ^= ",
                    ruff_python_ast::Operator::BitAnd => " &= ",
                    ruff_python_ast::Operator::FloorDiv => " //= ",
                    _ => " ?= ",
                };
                result.push_str(op_str);

                // Generate value (right side)
                result.push_str(&Self::generate_expression(&aug_assign.value)?);

                Ok(result)
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

            Stmt::For(for_stmt) => {
                // For loop statement
                let target = Self::generate_expression(&for_stmt.target)?;
                let iter = Self::generate_expression(&for_stmt.iter)?;
                let mut result = format!("{}for {} in {}:\n", indent_str, target, iter);

                // Generate body statements
                for body_stmt in &for_stmt.body {
                    let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                    result.push_str(&body_code);
                    result.push('\n');
                }

                // Handle else clause if present
                if !for_stmt.orelse.is_empty() {
                    result.push_str(&format!("{}else:\n", indent_str));
                    for else_stmt in &for_stmt.orelse {
                        let else_code = Self::generate_statement_impl(else_stmt, indent_level + 1)?;
                        result.push_str(&else_code);
                        result.push('\n');
                    }
                }

                Ok(result.trim_end().to_string())
            }

            Stmt::Try(try_stmt) => {
                // Try-except statement
                let mut result = format!("{}try:\n", indent_str);

                // Generate try body
                for body_stmt in &try_stmt.body {
                    let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                    result.push_str(&body_code);
                    result.push('\n');
                }

                // Generate except handlers
                for handler in &try_stmt.handlers {
                    match handler {
                        ruff_python_ast::ExceptHandler::ExceptHandler(eh) => {
                            result.push_str(&format!("{}except", indent_str));

                            if let Some(exc_type) = &eh.type_ {
                                result.push(' ');
                                result.push_str(&Self::generate_expression(exc_type)?);
                            }

                            if let Some(name) = &eh.name {
                                result.push_str(" as ");
                                result.push_str(name);
                            }

                            result.push_str(":\n");

                            // Generate except body
                            for except_stmt in &eh.body {
                                let except_code =
                                    Self::generate_statement_impl(except_stmt, indent_level + 1)?;
                                result.push_str(&except_code);
                                result.push('\n');
                            }
                        }
                    }
                }

                // Generate else clause if present
                if !try_stmt.orelse.is_empty() {
                    result.push_str(&format!("{}else:\n", indent_str));
                    for else_stmt in &try_stmt.orelse {
                        let else_code = Self::generate_statement_impl(else_stmt, indent_level + 1)?;
                        result.push_str(&else_code);
                        result.push('\n');
                    }
                }

                // Generate finally clause if present
                if !try_stmt.finalbody.is_empty() {
                    result.push_str(&format!("{}finally:\n", indent_str));
                    for finally_stmt in &try_stmt.finalbody {
                        let finally_code =
                            Self::generate_statement_impl(finally_stmt, indent_level + 1)?;
                        result.push_str(&finally_code);
                        result.push('\n');
                    }
                }

                Ok(result.trim_end().to_string())
            }

            Stmt::If(if_stmt) => {
                // If statement
                let test = Self::generate_expression(&if_stmt.test)?;
                let mut result = format!("{}if {}:\n", indent_str, test);

                // Generate if body
                for body_stmt in &if_stmt.body {
                    let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                    result.push_str(&body_code);
                    result.push('\n');
                }

                // Generate elif/else clauses
                for elif_clause in &if_stmt.elif_else_clauses {
                    if let Some(test) = &elif_clause.test {
                        // elif clause
                        let elif_test = Self::generate_expression(test)?;
                        result.push_str(&format!("{}elif {}:\n", indent_str, elif_test));
                    } else {
                        // else clause
                        result.push_str(&format!("{}else:\n", indent_str));
                    }

                    for clause_stmt in &elif_clause.body {
                        let clause_code =
                            Self::generate_statement_impl(clause_stmt, indent_level + 1)?;
                        result.push_str(&clause_code);
                        result.push('\n');
                    }
                }

                Ok(result.trim_end().to_string())
            }

            Stmt::While(while_stmt) => {
                // While loop statement
                let test = Self::generate_expression(&while_stmt.test)?;
                let mut result = format!("{}while {}:\n", indent_str, test);

                // Generate while body
                for body_stmt in &while_stmt.body {
                    let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                    result.push_str(&body_code);
                    result.push('\n');
                }

                // Generate else clause if present
                if !while_stmt.orelse.is_empty() {
                    result.push_str(&format!("{}else:\n", indent_str));
                    for else_stmt in &while_stmt.orelse {
                        let else_code = Self::generate_statement_impl(else_stmt, indent_level + 1)?;
                        result.push_str(&else_code);
                        result.push('\n');
                    }
                }

                Ok(result.trim_end().to_string())
            }

            Stmt::With(with_stmt) => {
                // With statement (context manager)
                let mut result = format!("{}with ", indent_str);

                for (i, item) in with_stmt.items.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(&item.context_expr)?);
                    if let Some(optional_vars) = &item.optional_vars {
                        result.push_str(" as ");
                        result.push_str(&Self::generate_expression(optional_vars)?);
                    }
                }

                result.push_str(":\n");

                // Generate with body
                for body_stmt in &with_stmt.body {
                    let body_code = Self::generate_statement_impl(body_stmt, indent_level + 1)?;
                    result.push_str(&body_code);
                    result.push('\n');
                }

                Ok(result.trim_end().to_string())
            }

            Stmt::Break(_) => {
                // Break statement
                Ok(format!("{}break", indent_str))
            }

            Stmt::Continue(_) => {
                // Continue statement
                Ok(format!("{}continue", indent_str))
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
                Ok(format!("\"{}\"", s.value.to_str()))
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

            Expr::FString(_) => {
                // F-string support - simplified placeholder implementation
                // TODO: Implement proper f-string generation
                Ok("f\"<f-string>\"".to_string())
            }

            Expr::List(list) => {
                // List literal support
                let mut result = String::from("[");
                for (i, element) in list.elts.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(element)?);
                }
                result.push(']');
                Ok(result)
            }

            Expr::Tuple(tuple) => {
                // Tuple literal support
                let mut result = String::from("(");
                for (i, element) in tuple.elts.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(element)?);
                }
                // Add trailing comma for single-element tuples
                if tuple.elts.len() == 1 {
                    result.push(',');
                }
                result.push(')');
                Ok(result)
            }

            Expr::Dict(dict) => {
                // Dictionary literal support
                let mut result = String::from("{");
                for (i, item) in dict.items.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    if let Some(key) = &item.key {
                        result.push_str(&Self::generate_expression(key)?);
                        result.push_str(": ");
                        result.push_str(&Self::generate_expression(&item.value)?);
                    } else {
                        // Handle dictionary unpacking like **other_dict
                        result.push_str("**");
                        result.push_str(&Self::generate_expression(&item.value)?);
                    }
                }
                result.push('}');
                Ok(result)
            }

            Expr::Set(set) => {
                // Set literal support
                let mut result = String::from("{");
                for (i, element) in set.elts.iter().enumerate() {
                    if i > 0 {
                        result.push_str(", ");
                    }
                    result.push_str(&Self::generate_expression(element)?);
                }
                result.push('}');
                Ok(result)
            }

            Expr::Compare(compare) => {
                // Comparison operations like ==, !=, <, >, etc.
                let mut result = Self::generate_expression(&compare.left)?;

                for (op, comparator) in compare.ops.iter().zip(compare.comparators.iter()) {
                    let op_str = match op {
                        ruff_python_ast::CmpOp::Eq => " == ",
                        ruff_python_ast::CmpOp::NotEq => " != ",
                        ruff_python_ast::CmpOp::Lt => " < ",
                        ruff_python_ast::CmpOp::LtE => " <= ",
                        ruff_python_ast::CmpOp::Gt => " > ",
                        ruff_python_ast::CmpOp::GtE => " >= ",
                        ruff_python_ast::CmpOp::Is => " is ",
                        ruff_python_ast::CmpOp::IsNot => " is not ",
                        ruff_python_ast::CmpOp::In => " in ",
                        ruff_python_ast::CmpOp::NotIn => " not in ",
                    };
                    result.push_str(op_str);
                    result.push_str(&Self::generate_expression(comparator)?);
                }

                Ok(result)
            }

            Expr::BoolOp(bool_op) => {
                // Boolean operations like 'and', 'or'
                let op_str = match bool_op.op {
                    ruff_python_ast::BoolOp::And => " and ",
                    ruff_python_ast::BoolOp::Or => " or ",
                };

                let mut parts = Vec::new();
                for value in &bool_op.values {
                    parts.push(Self::generate_expression(value)?);
                }

                Ok(parts.join(op_str))
            }

            Expr::UnaryOp(unary_op) => {
                // Unary operations like 'not', '-', '+'
                let op_str = match unary_op.op {
                    ruff_python_ast::UnaryOp::Not => "not ",
                    ruff_python_ast::UnaryOp::UAdd => "+",
                    ruff_python_ast::UnaryOp::USub => "-",
                    ruff_python_ast::UnaryOp::Invert => "~",
                };

                let operand = Self::generate_expression(&unary_op.operand)?;
                Ok(format!("{}{}", op_str, operand))
            }

            Expr::If(if_exp) => {
                // Conditional expression (ternary operator)
                let body = Self::generate_expression(&if_exp.body)?;
                let test = Self::generate_expression(&if_exp.test)?;
                let orelse = Self::generate_expression(&if_exp.orelse)?;
                Ok(format!("{} if {} else {}", body, test, orelse))
            }

            Expr::Slice(slice) => {
                // Slice expression
                let mut result = String::new();

                if let Some(lower) = &slice.lower {
                    result.push_str(&Self::generate_expression(lower)?);
                }
                result.push(':');

                if let Some(upper) = &slice.upper {
                    result.push_str(&Self::generate_expression(upper)?);
                }

                if let Some(step) = &slice.step {
                    result.push(':');
                    result.push_str(&Self::generate_expression(step)?);
                }

                Ok(result)
            }

            Expr::Lambda(lambda) => {
                // Lambda function - simplified implementation
                let mut result = String::from("lambda");

                // For now, just generate a simple lambda without parameters
                result.push_str(": ");
                result.push_str(&Self::generate_expression(&lambda.body)?);

                Ok(result)
            }

            Expr::Generator(gen) => {
                // Generator expression
                let elt = Self::generate_expression(&gen.elt)?;
                let mut result = format!("({}", elt);

                for comprehension in &gen.generators {
                    result.push_str(" for ");
                    result.push_str(&Self::generate_expression(&comprehension.target)?);
                    result.push_str(" in ");
                    result.push_str(&Self::generate_expression(&comprehension.iter)?);

                    for if_clause in &comprehension.ifs {
                        result.push_str(" if ");
                        result.push_str(&Self::generate_expression(if_clause)?);
                    }
                }

                result.push(')');
                Ok(result)
            }

            Expr::ListComp(listcomp) => {
                // List comprehension
                let elt = Self::generate_expression(&listcomp.elt)?;
                let mut result = format!("[{}", elt);

                for comprehension in &listcomp.generators {
                    result.push_str(" for ");
                    result.push_str(&Self::generate_expression(&comprehension.target)?);
                    result.push_str(" in ");
                    result.push_str(&Self::generate_expression(&comprehension.iter)?);

                    for if_clause in &comprehension.ifs {
                        result.push_str(" if ");
                        result.push_str(&Self::generate_expression(if_clause)?);
                    }
                }

                result.push(']');
                Ok(result)
            }

            Expr::SetComp(setcomp) => {
                // Set comprehension
                let elt = Self::generate_expression(&setcomp.elt)?;
                let mut result = format!("{{{}", elt);

                for comprehension in &setcomp.generators {
                    result.push_str(" for ");
                    result.push_str(&Self::generate_expression(&comprehension.target)?);
                    result.push_str(" in ");
                    result.push_str(&Self::generate_expression(&comprehension.iter)?);

                    for if_clause in &comprehension.ifs {
                        result.push_str(" if ");
                        result.push_str(&Self::generate_expression(if_clause)?);
                    }
                }

                result.push('}');
                Ok(result)
            }

            Expr::DictComp(dictcomp) => {
                // Dictionary comprehension
                let key = Self::generate_expression(&dictcomp.key)?;
                let value = Self::generate_expression(&dictcomp.value)?;
                let mut result = format!("{{{}: {}", key, value);

                for comprehension in &dictcomp.generators {
                    result.push_str(" for ");
                    result.push_str(&Self::generate_expression(&comprehension.target)?);
                    result.push_str(" in ");
                    result.push_str(&Self::generate_expression(&comprehension.iter)?);

                    for if_clause in &comprehension.ifs {
                        result.push_str(" if ");
                        result.push_str(&Self::generate_expression(if_clause)?);
                    }
                }

                result.push('}');
                Ok(result)
            }

            Expr::Yield(yield_expr) => {
                // Yield expression
                let mut result = String::from("yield");
                if let Some(value) = &yield_expr.value {
                    result.push(' ');
                    result.push_str(&Self::generate_expression(value)?);
                }
                Ok(result)
            }

            Expr::YieldFrom(yield_from) => {
                // Yield from expression
                let value = Self::generate_expression(&yield_from.value)?;
                Ok(format!("yield from {}", value))
            }

            Expr::Await(await_expr) => {
                // Await expression
                let value = Self::generate_expression(&await_expr.value)?;
                Ok(format!("await {}", value))
            }

            // Add more expression types as needed
            _ => Err(PyRustorError::ast_error(format!(
                "Unsupported expression type: {:?}",
                std::mem::discriminant(expr)
            ))),
        }
    }
}
