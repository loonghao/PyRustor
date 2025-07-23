# PyRustor API扩展提案

## 当前API分析

PyRustor当前提供的API：

```python
# Parser
parser.parse_string(source)
parser.parse_file(path)
parser.parse_directory(path, recursive)

# PythonAst
ast.is_empty()
ast.statement_count()
ast.function_names()
ast.class_names()
ast.imports()
ast.to_string()

# Refactor
refactor.rename_function(old, new)
refactor.rename_class(old, new)
refactor.replace_import(old, new)
refactor.modernize_syntax()
refactor.get_code()
refactor.change_summary()
refactor.save_to_file(path)
```

## 建议的底层API扩展

### 1. AST节点访问和查询

```rust
// Rust核心实现
impl PythonAst {
    pub fn find_nodes(&self, node_type: Option<&str>, filter: Option<Box<dyn Fn(&AstNode) -> bool>>) -> Vec<AstNodeRef>
    pub fn find_imports(&self, module_pattern: Option<&str>) -> Vec<ImportNode>
    pub fn find_function_calls(&self, function_name: &str) -> Vec<CallNode>
    pub fn find_try_except_blocks(&self, exception_type: Option<&str>) -> Vec<TryExceptNode>
    pub fn find_assignments(&self, target_pattern: Option<&str>) -> Vec<AssignmentNode>
}
```

```python
# Python绑定
class PythonAst:
    def find_nodes(self, node_type: str = None, filter_func: callable = None) -> List[AstNode]:
        """查找匹配条件的AST节点"""
        pass
    
    def find_imports(self, module_pattern: str = None) -> List[ImportNode]:
        """查找导入语句"""
        pass
    
    def find_function_calls(self, function_name: str) -> List[CallNode]:
        """查找函数调用"""
        pass
    
    def find_try_except_blocks(self, exception_type: str = None) -> List[TryExceptNode]:
        """查找try-except块"""
        pass
    
    def find_assignments(self, target_pattern: str = None) -> List[AssignmentNode]:
        """查找赋值语句"""
        pass
```

### 2. 节点操作API

```rust
// Rust核心实现
impl Refactor {
    pub fn replace_node(&mut self, node_ref: AstNodeRef, new_code: &str) -> Result<()>
    pub fn remove_node(&mut self, node_ref: AstNodeRef) -> Result<()>
    pub fn insert_before(&mut self, node_ref: AstNodeRef, new_code: &str) -> Result<()>
    pub fn insert_after(&mut self, node_ref: AstNodeRef, new_code: &str) -> Result<()>
    pub fn replace_code_range(&mut self, start: usize, end: usize, new_code: &str) -> Result<()>
}
```

```python
# Python绑定
class Refactor:
    def replace_node(self, node: AstNode, new_code: str) -> None:
        """替换单个AST节点"""
        pass
    
    def remove_node(self, node: AstNode) -> None:
        """删除AST节点"""
        pass
    
    def insert_before(self, node: AstNode, new_code: str) -> None:
        """在节点前插入代码"""
        pass
    
    def insert_after(self, node: AstNode, new_code: str) -> None:
        """在节点后插入代码"""
        pass
    
    def replace_code_range(self, start_line: int, end_line: int, new_code: str) -> None:
        """替换指定行范围的代码"""
        pass
```

### 3. 模式匹配API

```python
class PatternMatcher:
    def __init__(self, ast: PythonAst):
        self.ast = ast
        self.conditions = []
    
    def has_imports(self, imports: List[str]) -> 'PatternMatcher':
        """匹配包含特定导入"""
        self.conditions.append(('imports', imports))
        return self
    
    def contains_try_except(self, exception_type: str = None) -> 'PatternMatcher':
        """匹配包含try-except块"""
        self.conditions.append(('try_except', exception_type))
        return self
    
    def contains_function_call(self, function_name: str) -> 'PatternMatcher':
        """匹配包含特定函数调用"""
        self.conditions.append(('function_call', function_name))
        return self
    
    def find_matches(self) -> List[PatternMatch]:
        """查找所有匹配的模式"""
        pass

# 使用方式
matcher = PatternMatcher(ast)
matches = (matcher
          .has_imports(["pkg_resources.get_distribution"])
          .contains_try_except("DistributionNotFound")
          .contains_function_call("get_distribution")
          .find_matches())
```

### 4. 代码生成器API

```python
class CodeGenerator:
    @staticmethod
    def create_import(module: str, items: List[str] = None, alias: str = None) -> str:
        """生成导入语句"""
        if items:
            items_str = ", ".join(items)
            return f"from {module} import {items_str}"
        else:
            if alias:
                return f"import {module} as {alias}"
            return f"import {module}"
    
    @staticmethod
    def create_assignment(target: str, value: str) -> str:
        """生成赋值语句"""
        return f"{target} = {value}"
    
    @staticmethod
    def create_function_call(function: str, args: List[str]) -> str:
        """生成函数调用"""
        args_str = ", ".join(args)
        return f"{function}({args_str})"
    
    @staticmethod
    def create_try_except(try_body: str, except_type: str, except_body: str) -> str:
        """生成try-except块"""
        return f"""try:
    {try_body}
except {except_type}:
    {except_body}"""
```

## 实际使用示例

### 用户基于底层API构建pkg_resources现代化

```python
def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony", target_function="get_package_version"):
    """用户基于底层API构建的pkg_resources现代化功能"""
    
    ast = refactor.ast
    
    # 1. 查找pkg_resources版本检测模式
    matcher = PatternMatcher(ast)
    matches = (matcher
              .has_imports(["pkg_resources.get_distribution", "pkg_resources.DistributionNotFound"])
              .contains_try_except("DistributionNotFound")
              .contains_function_call("get_distribution")
              .find_matches())
    
    if not matches:
        return False
    
    # 2. 分析匹配的模式
    for match in matches:
        # 提取信息
        try_except_node = match.get_try_except_node()
        assignment_node = match.get_assignment_in_try()
        
        # 获取变量名和包名
        var_name = assignment_node.target  # "__version__"
        pkg_call = assignment_node.value   # "get_distribution(__name__).version"
        pkg_arg = extract_package_arg(pkg_call)  # "__name__"
        
        # 3. 生成替换代码
        new_code = CodeGenerator.create_assignment(
            var_name, 
            CodeGenerator.create_function_call(target_function, [pkg_arg])
        )
        
        # 4. 替换节点
        refactor.replace_node(try_except_node, new_code)
    
    # 5. 更新导入
    refactor.replace_import("pkg_resources", target_module)
    
    return True

# 使用
parser = pyrustor.Parser()
ast = parser.parse_string(source_code)
refactor = pyrustor.Refactor(ast)

success = modernize_pkg_resources_version(refactor)
if success:
    result = refactor.get_code()
```

### 用户构建字符串格式化现代化

```python
def modernize_string_formatting(refactor):
    """现代化字符串格式化"""
    
    ast = refactor.ast
    
    # 查找%格式化
    format_nodes = ast.find_nodes(
        filter_func=lambda node: (
            node.node_type == "binary_op" and 
            node.operator == "%" and
            node.left.node_type == "string"
        )
    )
    
    for node in format_nodes:
        if can_convert_to_fstring(node):
            fstring_code = convert_to_fstring(node)
            refactor.replace_node(node, fstring_code)
    
    return len(format_nodes) > 0
```

### 用户构建导入现代化

```python
def modernize_imports(refactor, import_mapping):
    """现代化导入"""
    
    for old_module, new_module in import_mapping.items():
        # 查找旧导入
        import_nodes = refactor.ast.find_imports(old_module)
        
        if import_nodes:
            # 替换导入
            refactor.replace_import(old_module, new_module)
            
            # 查找并更新相关的函数调用
            old_calls = refactor.ast.find_function_calls(f"{old_module}.")
            for call_node in old_calls:
                new_call = call_node.code.replace(old_module, new_module)
                refactor.replace_node(call_node, new_call)
```

## 实现优先级

### 第一阶段（高优先级）
1. **节点查询API**：`find_nodes`, `find_imports`, `find_function_calls`
2. **基础节点操作**：`replace_node`, `remove_node`
3. **代码生成器**：基础的代码生成功能

### 第二阶段（中优先级）
1. **模式匹配器**：`PatternMatcher`类
2. **高级节点操作**：`insert_before`, `insert_after`
3. **上下文信息提取**：从匹配中提取变量、参数等信息

### 第三阶段（低优先级）
1. **性能优化**：批量操作、缓存
2. **高级模式**：复杂的AST模式匹配
3. **用户扩展接口**：插件系统

## 优势

1. **通用性**：底层API支持各种代码转换需求
2. **组合性**：用户可以组合基础API构建复杂功能
3. **可扩展性**：不需要修改核心就能支持新的转换
4. **向后兼容**：不影响现有的高级API
5. **性能**：Rust实现保证高性能

这种设计让PyRustor成为一个强大的底层工具平台，用户可以基于它快速构建各种专门的代码转换工具。
