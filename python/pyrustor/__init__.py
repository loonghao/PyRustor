"""
PyRustor - A high-performance Python code parsing and refactoring tool written in Rust

This package provides Python bindings for the PyRustor core library,
enabling Python developers to use the high-performance Rust-based
Python code parsing and refactoring tools.

Example:
    >>> import pyrustor
    >>> parser = pyrustor.Parser()
    >>> ast = parser.parse_string("def hello(): pass")
    >>> refactor = pyrustor.Refactor(ast)
    >>> refactor.rename_function("hello", "greet")
    >>> print(refactor.get_code())
"""

from ._pyrustor import (
    Parser,
    PythonAst,
    Refactor,
    AstNodeRef,
    ImportNode,
    CallNode,
    TryExceptNode,
    AssignmentNode,
    CodeGenerator,
)

__version__ = "0.1.15"

__all__ = [
    "Parser",
    "PythonAst",
    "Refactor",
    "AstNodeRef",
    "ImportNode",
    "CallNode",
    "TryExceptNode",
    "AssignmentNode",
    "CodeGenerator",
    "__version__",
]
