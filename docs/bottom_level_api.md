# PyRustor Bottom-Level API

The PyRustor Bottom-Level API provides fine-grained access to the Abstract Syntax Tree (AST) and code generation capabilities, enabling users to build custom refactoring and modernization tools on top of PyRustor's core functionality.

## Overview

The bottom-level API consists of several key components:

1. **AST Query Methods** - Find specific nodes, imports, function calls, etc.
2. **Node Manipulation Methods** - Replace, insert, and remove AST nodes
3. **Code Generation Utilities** - Generate Python code snippets programmatically
4. **Node Reference System** - Navigate and reference specific AST nodes

## API Components

### AST Query Methods

#### PythonAst Methods

```python
import pyrustor

parser = pyrustor.Parser()
ast = parser.parse_string(source_code)

# Find all nodes or nodes of specific type
all_nodes = ast.find_nodes()
import_nodes = ast.find_nodes("import_from")

# Find import statements
all_imports = ast.find_imports()
pkg_imports = ast.find_imports("pkg_resources")

# Find function calls
get_dist_calls = ast.find_function_calls("get_distribution")

# Find try-except blocks
all_try_except = ast.find_try_except_blocks()
specific_exceptions = ast.find_try_except_blocks("DistributionNotFound")

# Find assignment statements
all_assignments = ast.find_assignments()
version_assignments = ast.find_assignments("__version__")
```

#### Refactor Methods

The `Refactor` class provides the same query methods plus manipulation capabilities:

```python
refactor = pyrustor.Refactor(ast)

# All the same query methods as PythonAst
imports = refactor.find_imports("pkg_resources")
calls = refactor.find_function_calls("get_distribution")

# Plus access to underlying AST
underlying_ast = refactor.ast()
```

### Node Manipulation Methods

```python
# Replace a specific AST node with new code
refactor.replace_node(node_ref, "new_code_here")

# Remove a specific AST node
refactor.remove_node(node_ref)

# Insert code before/after a specific node
refactor.insert_before(node_ref, "# Comment before")
refactor.insert_after(node_ref, "# Comment after")

# Replace code in a specific line range
refactor.replace_code_range(start_line, end_line, "new_code")
```

### Code Generation

#### Standalone Code Generator

```python
generator = pyrustor.CodeGenerator()

# Import statements
simple_import = generator.create_import("os")
# Result: "import os"

import_with_alias = generator.create_import("json", None, "js")
# Result: "import json as js"

from_import = generator.create_import("pathlib", ["Path"])
# Result: "from pathlib import Path"

multiple_import = generator.create_import("typing", ["List", "Dict"])
# Result: "from typing import List, Dict"

# Assignment statements
assignment = generator.create_assignment("x", "42")
# Result: "x = 42"

# Function calls
func_call = generator.create_function_call("print", ["'hello'"])
# Result: "print('hello')"

# Try-except blocks
try_except = generator.create_try_except(
    "result = risky_operation()",
    "ValueError", 
    "result = 'error'"
)
# Result: "try:\n    result = risky_operation()\nexcept ValueError:\n    result = 'error'"
```

#### Through Refactor Instance

```python
refactor = pyrustor.Refactor(ast)
generator = refactor.code_generator()
# Use same methods as standalone generator
```

### Node Reference System

The API uses `AstNodeRef` objects to reference specific nodes in the AST:

```python
# Node references contain path and type information
node_ref = AstNodeRef(
    node_type="import_from",
    path=[0, 1],  # Path to node in AST
    location=SourceLocation(line=1, column=0)
)

# Access node properties
print(node_ref.node_type)  # "import_from"
print(node_ref.path)       # [0, 1]
```

### Specialized Node Types

#### ImportNode
```python
import_node = ImportNode(
    module="pkg_resources",
    items=["get_distribution"],
    node_ref=node_ref
)

print(import_node.module)    # "pkg_resources"
print(import_node.items)     # ["get_distribution"]
```

#### CallNode
```python
call_node = CallNode(
    function_name="get_distribution",
    args=["__name__"],
    node_ref=node_ref
)

print(call_node.function_name)  # "get_distribution"
print(call_node.args)           # ["__name__"]
```

#### TryExceptNode
```python
try_except_node = TryExceptNode(
    exception_types=["DistributionNotFound"],
    node_ref=node_ref
)

print(try_except_node.exception_types)  # ["DistributionNotFound"]
```

#### AssignmentNode
```python
assignment_node = AssignmentNode(
    target="__version__",
    value="get_distribution(__name__).version",
    node_ref=node_ref
)

print(assignment_node.target)  # "__version__"
print(assignment_node.value)   # "get_distribution(__name__).version"
```

## Example: Building pkg_resources Modernization

Here's a complete example of how to build a custom pkg_resources modernization function:

```python
def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony"):
    """Modernize pkg_resources version detection pattern."""
    
    # 1. Check if we have the pattern
    pkg_imports = refactor.find_imports("pkg_resources")
    if not pkg_imports:
        return False
    
    try_except_blocks = refactor.find_try_except_blocks("DistributionNotFound")
    if not try_except_blocks:
        return False
    
    get_dist_calls = refactor.find_function_calls("get_distribution")
    if not get_dist_calls:
        return False
    
    version_assignments = refactor.find_assignments("__version__")
    if not version_assignments:
        return False
    
    # 2. Apply transformations
    refactor.replace_import("pkg_resources", target_module)
    
    # 3. Generate new code
    generator = refactor.code_generator()
    new_import = generator.create_import(target_module, ["get_package_version"])
    new_assignment = generator.create_assignment(
        "__version__", 
        "get_package_version(__name__)"
    )
    
    # In a full implementation, you would use replace_node to apply these changes
    
    return True

# Usage
source_code = '''
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
'''

parser = pyrustor.Parser()
ast = parser.parse_string(source_code)
refactor = pyrustor.Refactor(ast)

success = modernize_pkg_resources_version(refactor)
if success:
    print("Modernization applied!")
    print(refactor.get_code())
```

## Benefits of the Bottom-Level API

1. **Flexibility** - Build custom transformations for specific needs
2. **Composability** - Combine multiple transformations
3. **Precision** - Target specific code patterns accurately
4. **Extensibility** - Add new functionality without modifying core library
5. **Code Generation** - Create new code programmatically
6. **Pattern Matching** - Find complex code patterns reliably

## Use Cases

- **Custom Modernization Rules** - Build organization-specific modernization patterns
- **Code Analysis Tools** - Analyze codebases for specific patterns
- **Migration Utilities** - Migrate from deprecated APIs to new ones
- **Code Quality Tools** - Detect and fix code quality issues
- **Template Generation** - Generate boilerplate code
- **Refactoring Automation** - Automate complex refactoring tasks

## Best Practices

1. **Start with Queries** - Always query first to understand the code structure
2. **Use Code Generator** - Generate new code instead of string concatenation
3. **Test Patterns** - Verify your patterns work on representative code samples
4. **Handle Edge Cases** - Consider various code styles and edge cases
5. **Preserve Formatting** - Use PyRustor's formatting preservation features
6. **Batch Operations** - Apply multiple changes in a single refactor session

The bottom-level API provides the foundation for building sophisticated code transformation tools while maintaining PyRustor's performance and reliability.
