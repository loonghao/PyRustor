//! AST functionality tests

use pyrustor_core::Parser;

#[test]
fn test_ast_creation() {
    let parser = Parser::new();
    let code = r#"
def hello():
    print("Hello, world!")

class MyClass:
    def method(self):
        return 42
"#;

    let ast = parser.parse_string(code).unwrap();
    assert!(!ast.is_empty());
    assert_eq!(ast.statement_count(), 2);
}

#[test]
fn test_function_names() {
    let parser = Parser::new();
    let code = r#"
def top_level_function():
    pass

class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
"#;

    let ast = parser.parse_string(code).unwrap();
    let function_names = ast.function_names();

    assert_eq!(function_names.len(), 3);
    assert!(function_names.contains(&"top_level_function".to_string()));
    assert!(function_names.contains(&"method1".to_string()));
    assert!(function_names.contains(&"method2".to_string()));
}

#[test]
fn test_class_names() {
    let parser = Parser::new();
    let code = r#"
class FirstClass:
    pass

class SecondClass:
    pass
"#;

    let ast = parser.parse_string(code).unwrap();
    let class_names = ast.class_names();

    assert_eq!(class_names.len(), 2);
    assert!(class_names.contains(&"FirstClass".to_string()));
    assert!(class_names.contains(&"SecondClass".to_string()));
}

#[test]
fn test_empty_ast() {
    let parser = Parser::new();
    let ast = parser.parse_string("").unwrap();
    assert!(ast.is_empty());
    assert_eq!(ast.statement_count(), 0);
}

#[test]
fn test_comments_only() {
    let parser = Parser::new();
    let code = r#"
"""
This is just a docstring
"""
"#;

    let ast = parser.parse_string(code).unwrap();
    assert!(!ast.is_empty()); // Has a statement (docstring)
    assert!(ast.is_comments_only()); // But it's only comments/docstrings
}

#[test]
fn test_find_imports() {
    let parser = Parser::new();
    let code = r#"
import os
import sys
from collections import defaultdict
from typing import List, Dict
"#;

    let ast = parser.parse_string(code).unwrap();
    let imports = ast.find_imports(None);

    assert_eq!(imports.len(), 4);

    // Test specific module search
    let os_imports = ast.find_imports(Some("os"));
    assert_eq!(os_imports.len(), 1);
    assert_eq!(os_imports[0].module, "os");
}

#[test]
fn test_find_function_calls() {
    let parser = Parser::new();
    let code = r#"
def test():
    print("hello")
    len([1, 2, 3])
    print("world")
"#;

    let ast = parser.parse_string(code).unwrap();
    let calls = ast.find_function_calls(None);

    assert!(calls.len() >= 3); // At least print, len, print

    // Test specific function search
    let print_calls = ast.find_function_calls(Some("print"));
    assert_eq!(print_calls.len(), 2);
}

#[test]
fn test_find_assignments() {
    let parser = Parser::new();
    let code = r#"
x = 1
y = 2
result = x + y
"#;

    let ast = parser.parse_string(code).unwrap();
    let assignments = ast.find_assignments(None);

    assert_eq!(assignments.len(), 3);

    // Test specific target search
    let x_assignments = ast.find_assignments(Some("x"));
    assert_eq!(x_assignments.len(), 1);
    assert_eq!(x_assignments[0].target, "x");
}

#[test]
fn test_code_generation() {
    let parser = Parser::new();
    let code = r#"def hello():
    return "world"
"#;

    let ast = parser.parse_string(code).unwrap();
    let generated = ast.to_code().unwrap();

    // Should contain the function definition
    assert!(generated.contains("def hello():"));
    assert!(generated.contains("return \"world\""));
}
