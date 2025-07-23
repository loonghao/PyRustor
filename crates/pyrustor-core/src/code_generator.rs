//! Code generation utilities for building Python code programmatically

use crate::error::Result;

/// Utility for generating Python code snippets
#[derive(Debug, Clone)]
pub struct CodeGenerator;

impl CodeGenerator {
    /// Create a new code generator
    pub fn new() -> Self {
        Self
    }

    /// Generate an import statement
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// // Simple import: import os
    /// let import1 = gen.create_import("os", None, None).unwrap();
    /// assert_eq!(import1, "import os");
    ///
    /// // Import with alias: import json as js
    /// let import2 = gen.create_import("json", None, Some("js")).unwrap();
    /// assert_eq!(import2, "import json as js");
    ///
    /// // From import: from pathlib import Path
    /// let import3 = gen.create_import("pathlib", Some(vec!["Path".to_string()]), None).unwrap();
    /// assert_eq!(import3, "from pathlib import Path");
    ///
    /// // Multiple from import: from typing import List, Dict
    /// let import4 = gen.create_import("typing", Some(vec!["List".to_string(), "Dict".to_string()]), None).unwrap();
    /// assert_eq!(import4, "from typing import List, Dict");
    /// ```
    pub fn create_import(
        &self,
        module: &str,
        items: Option<Vec<String>>,
        alias: Option<&str>,
    ) -> Result<String> {
        if let Some(items) = items {
            if items.is_empty() {
                return Ok(format!("from {}", module));
            }
            let items_str = items.join(", ");
            Ok(format!("from {} import {}", module, items_str))
        } else if let Some(alias) = alias {
            Ok(format!("import {} as {}", module, alias))
        } else {
            Ok(format!("import {}", module))
        }
    }

    /// Generate an assignment statement
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let assignment = gen.create_assignment("x", "42").unwrap();
    /// assert_eq!(assignment, "x = 42");
    ///
    /// let complex_assignment = gen.create_assignment("result", "func(arg1, arg2)").unwrap();
    /// assert_eq!(complex_assignment, "result = func(arg1, arg2)");
    /// ```
    pub fn create_assignment(&self, target: &str, value: &str) -> Result<String> {
        Ok(format!("{} = {}", target, value))
    }

    /// Generate a function call
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let call1 = gen.create_function_call("print", vec!["'hello'".to_string()]).unwrap();
    /// assert_eq!(call1, "print('hello')");
    ///
    /// let call2 = gen.create_function_call("max", vec!["a".to_string(), "b".to_string()]).unwrap();
    /// assert_eq!(call2, "max(a, b)");
    ///
    /// let call3 = gen.create_function_call("func", vec![]).unwrap();
    /// assert_eq!(call3, "func()");
    /// ```
    pub fn create_function_call(&self, function: &str, args: Vec<String>) -> Result<String> {
        let args_str = args.join(", ");
        Ok(format!("{}({})", function, args_str))
    }

    /// Generate a try-except block
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let try_except = gen.create_try_except(
    ///     "result = risky_operation()",
    ///     "ValueError",
    ///     "result = default_value"
    /// ).unwrap();
    ///
    /// let expected = "try:\n    result = risky_operation()\nexcept ValueError:\n    result = default_value";
    /// assert_eq!(try_except, expected);
    /// ```
    pub fn create_try_except(
        &self,
        try_body: &str,
        except_type: &str,
        except_body: &str,
    ) -> Result<String> {
        Ok(format!(
            "try:\n    {}\nexcept {}:\n    {}",
            try_body, except_type, except_body
        ))
    }

    /// Generate a function definition
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let func = gen.create_function_def(
    ///     "greet",
    ///     vec!["name".to_string()],
    ///     "return f'Hello, {name}!'"
    /// ).unwrap();
    ///
    /// let expected = "def greet(name):\n    return f'Hello, {name}!'";
    /// assert_eq!(func, expected);
    /// ```
    pub fn create_function_def(&self, name: &str, args: Vec<String>, body: &str) -> Result<String> {
        let args_str = args.join(", ");
        Ok(format!("def {}({}):\n    {}", name, args_str, body))
    }

    /// Generate a class definition
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let class = gen.create_class_def(
    ///     "MyClass",
    ///     Some(vec!["BaseClass".to_string()]),
    ///     "pass"
    /// ).unwrap();
    ///
    /// let expected = "class MyClass(BaseClass):\n    pass";
    /// assert_eq!(class, expected);
    /// ```
    pub fn create_class_def(
        &self,
        name: &str,
        bases: Option<Vec<String>>,
        body: &str,
    ) -> Result<String> {
        if let Some(bases) = bases {
            if bases.is_empty() {
                Ok(format!("class {}:\n    {}", name, body))
            } else {
                let bases_str = bases.join(", ");
                Ok(format!("class {}({}):\n    {}", name, bases_str, body))
            }
        } else {
            Ok(format!("class {}:\n    {}", name, body))
        }
    }

    /// Generate an if statement
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let if_stmt = gen.create_if_statement(
    ///     "x > 0",
    ///     "print('positive')",
    ///     Some("print('not positive')")
    /// ).unwrap();
    ///
    /// let expected = "if x > 0:\n    print('positive')\nelse:\n    print('not positive')";
    /// assert_eq!(if_stmt, expected);
    /// ```
    pub fn create_if_statement(
        &self,
        condition: &str,
        if_body: &str,
        else_body: Option<&str>,
    ) -> Result<String> {
        if let Some(else_body) = else_body {
            Ok(format!(
                "if {}:\n    {}\nelse:\n    {}",
                condition, if_body, else_body
            ))
        } else {
            Ok(format!("if {}:\n    {}", condition, if_body))
        }
    }

    /// Generate a for loop
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let for_loop = gen.create_for_loop(
    ///     "item",
    ///     "items",
    ///     "print(item)"
    /// ).unwrap();
    ///
    /// let expected = "for item in items:\n    print(item)";
    /// assert_eq!(for_loop, expected);
    /// ```
    pub fn create_for_loop(&self, var: &str, iterable: &str, body: &str) -> Result<String> {
        Ok(format!("for {} in {}:\n    {}", var, iterable, body))
    }

    /// Generate a while loop
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let while_loop = gen.create_while_loop(
    ///     "x > 0",
    ///     "x -= 1"
    /// ).unwrap();
    ///
    /// let expected = "while x > 0:\n    x -= 1";
    /// assert_eq!(while_loop, expected);
    /// ```
    pub fn create_while_loop(&self, condition: &str, body: &str) -> Result<String> {
        Ok(format!("while {}:\n    {}", condition, body))
    }

    /// Generate a list comprehension
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let list_comp = gen.create_list_comprehension(
    ///     "x * 2",
    ///     "x",
    ///     "range(10)",
    ///     Some("x % 2 == 0")
    /// ).unwrap();
    ///
    /// let expected = "[x * 2 for x in range(10) if x % 2 == 0]";
    /// assert_eq!(list_comp, expected);
    /// ```
    pub fn create_list_comprehension(
        &self,
        expression: &str,
        var: &str,
        iterable: &str,
        condition: Option<&str>,
    ) -> Result<String> {
        if let Some(condition) = condition {
            Ok(format!(
                "[{} for {} in {} if {}]",
                expression, var, iterable, condition
            ))
        } else {
            Ok(format!("[{} for {} in {}]", expression, var, iterable))
        }
    }

    /// Generate a dictionary comprehension
    ///
    /// # Examples
    ///
    /// ```
    /// use pyrustor_core::code_generator::CodeGenerator;
    ///
    /// let gen = CodeGenerator::new();
    ///
    /// let dict_comp = gen.create_dict_comprehension(
    ///     "x",
    ///     "x * 2",
    ///     "x",
    ///     "range(5)",
    ///     None
    /// ).unwrap();
    ///
    /// let expected = "{x: x * 2 for x in range(5)}";
    /// assert_eq!(dict_comp, expected);
    /// ```
    pub fn create_dict_comprehension(
        &self,
        key_expr: &str,
        value_expr: &str,
        var: &str,
        iterable: &str,
        condition: Option<&str>,
    ) -> Result<String> {
        if let Some(condition) = condition {
            Ok(format!(
                "{{{}: {} for {} in {} if {}}}",
                key_expr, value_expr, var, iterable, condition
            ))
        } else {
            Ok(format!(
                "{{{}: {} for {} in {}}}",
                key_expr, value_expr, var, iterable
            ))
        }
    }
}

impl Default for CodeGenerator {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_import() {
        let gen = CodeGenerator::new();

        // Simple import
        assert_eq!(gen.create_import("os", None, None).unwrap(), "import os");

        // Import with alias
        assert_eq!(
            gen.create_import("json", None, Some("js")).unwrap(),
            "import json as js"
        );

        // From import
        assert_eq!(
            gen.create_import("pathlib", Some(vec!["Path".to_string()]), None)
                .unwrap(),
            "from pathlib import Path"
        );

        // Multiple from import
        assert_eq!(
            gen.create_import(
                "typing",
                Some(vec!["List".to_string(), "Dict".to_string()]),
                None
            )
            .unwrap(),
            "from typing import List, Dict"
        );
    }

    #[test]
    fn test_create_assignment() {
        let gen = CodeGenerator::new();

        assert_eq!(gen.create_assignment("x", "42").unwrap(), "x = 42");
        assert_eq!(
            gen.create_assignment("result", "func(arg1, arg2)").unwrap(),
            "result = func(arg1, arg2)"
        );
    }

    #[test]
    fn test_create_function_call() {
        let gen = CodeGenerator::new();

        assert_eq!(
            gen.create_function_call("print", vec!["'hello'".to_string()])
                .unwrap(),
            "print('hello')"
        );
        assert_eq!(
            gen.create_function_call("max", vec!["a".to_string(), "b".to_string()])
                .unwrap(),
            "max(a, b)"
        );
        assert_eq!(gen.create_function_call("func", vec![]).unwrap(), "func()");
    }

    #[test]
    fn test_create_try_except() {
        let gen = CodeGenerator::new();

        let result = gen
            .create_try_except(
                "result = risky_operation()",
                "ValueError",
                "result = default_value",
            )
            .unwrap();

        let expected =
            "try:\n    result = risky_operation()\nexcept ValueError:\n    result = default_value";
        assert_eq!(result, expected);
    }
}
