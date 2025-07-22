"""Type stubs for PyRustor Python bindings"""

from typing import List, Optional, Dict, Any
from pathlib import Path

class Parser:
    """Python wrapper for the Parser"""
    
    def __init__(self) -> None:
        """Create a new parser"""
        ...
    
    def parse_string(self, source: str) -> PythonAst:
        """Parse Python code from a string"""
        ...
    
    def parse_file(self, path: str) -> PythonAst:
        """Parse Python code from a file"""
        ...
    
    def parse_directory(self, dir_path: str, recursive: bool) -> List[tuple[str, PythonAst]]:
        """Parse multiple Python files from a directory"""
        ...

class PythonAst:
    """Python wrapper for the PythonAst"""
    
    def is_empty(self) -> bool:
        """Check if the AST is empty"""
        ...
    
    def statement_count(self) -> int:
        """Get the number of statements"""
        ...
    
    def function_names(self) -> List[str]:
        """Get function names"""
        ...
    
    def class_names(self) -> List[str]:
        """Get class names"""
        ...
    
    def imports(self) -> List[str]:
        """Get import information"""
        ...
    
    def get_code(self) -> str:
        """Convert AST back to string"""
        ...

class Refactor:
    """Python wrapper for the Refactor"""
    
    def __init__(self, ast: PythonAst) -> None:
        """Create a new refactor instance"""
        ...
    
    def rename_function(self, old_name: str, new_name: str) -> None:
        """Rename a function"""
        ...
    
    def rename_class(self, old_name: str, new_name: str) -> None:
        """Rename a class"""
        ...
    
    def replace_import(self, old_module: str, new_module: str) -> None:
        """Replace import statements"""
        ...
    
    def modernize_syntax(self) -> None:
        """Modernize syntax"""
        ...
    
    def get_code(self) -> str:
        """Get the refactored code as string"""
        ...
    
    def save_to_file(self, path: str) -> None:
        """Save to file"""
        ...
    
    def change_summary(self) -> str:
        """Get change summary"""
        ...

__version__: str
