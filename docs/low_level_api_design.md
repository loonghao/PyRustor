# 底层API设计方案

## 设计理念

提供底层的、通用的API，让用户能够基于这些基础能力快速构建高级功能。

## 核心底层API

### 1. 代码块匹配和替换

```python
# 底层API：通用代码块替换
refactor.replace_code_block(
    matcher=lambda node: node.is_try_except() and 
                         node.contains_call("get_distribution"),
    replacer=lambda node, context: generate_new_code(node, context)
)
```

### 2. AST节点查询和操作

```python
# 查找特定模式的节点
try_except_nodes = refactor.find_nodes(
    node_type="try_except",
    filter_func=lambda node: node.contains_import("pkg_resources")
)

# 替换找到的节点
for node in try_except_nodes:
    new_code = generate_replacement(node)
    refactor.replace_node(node, new_code)
```

### 3. 模式匹配构建器

```python
# 构建复杂的匹配模式
pattern = (refactor.pattern_builder()
          .has_imports(["pkg_resources.get_distribution", "pkg_resources.DistributionNotFound"])
          .contains_try_except()
          .try_body_contains_call("get_distribution")
          .except_handles("DistributionNotFound"))

# 应用替换
refactor.replace_matching_patterns(pattern, replacement_template)
```

### 4. 代码生成器

```python
# 底层代码生成
code_generator = refactor.code_generator()
new_import = code_generator.create_import("internal_pyharmony", ["get_package_version"])
new_assignment = code_generator.create_assignment("__version__", "get_package_version(__name__)")

refactor.replace_imports_and_code(
    remove_imports=["pkg_resources"],
    add_imports=[new_import],
    replace_code_blocks=[(old_pattern, [new_assignment])]
)
```

## 实现示例

### 用户如何基于底层API构建高级功能

```python
def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony", target_function="get_package_version"):
    """用户基于底层API构建的高级功能"""
    
    # 1. 查找pkg_resources版本检测模式
    pattern = (refactor.pattern_builder()
              .has_imports(["pkg_resources.get_distribution", "pkg_resources.DistributionNotFound"])
              .contains_try_except()
              .try_body_contains_call("get_distribution")
              .except_handles("DistributionNotFound"))
    
    # 2. 定义替换逻辑
    def replacement_generator(matched_node, context):
        # 提取变量名
        version_var = context.get_assignment_target()  # "__version__"
        package_name = context.get_function_arg("get_distribution", 0)  # "__name__"
        
        # 生成新代码
        return f"""
from {target_module} import {target_function}

{version_var} = {target_function}({package_name})
        """.strip()
    
    # 3. 应用替换
    refactor.replace_matching_patterns(pattern, replacement_generator)
```

## 底层API详细设计

### 1. 节点查询API

```python
class Refactor:
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
```

### 2. 模式构建器API

```python
class PatternBuilder:
    def has_imports(self, imports: List[str]) -> 'PatternBuilder':
        """匹配包含特定导入的代码"""
        pass
    
    def contains_try_except(self) -> 'PatternBuilder':
        """匹配包含try-except的代码"""
        pass
    
    def try_body_contains_call(self, function_name: str) -> 'PatternBuilder':
        """匹配try块中包含特定函数调用"""
        pass
    
    def except_handles(self, exception_type: str) -> 'PatternBuilder':
        """匹配处理特定异常类型"""
        pass
    
    def build(self) -> Pattern:
        """构建最终的匹配模式"""
        pass
```

### 3. 代码替换API

```python
class Refactor:
    def replace_node(self, node: AstNode, new_code: str) -> None:
        """替换单个AST节点"""
        pass
    
    def replace_code_block(self, matcher: callable, replacer: callable) -> None:
        """替换匹配的代码块"""
        pass
    
    def replace_matching_patterns(self, pattern: Pattern, replacer: callable) -> None:
        """替换匹配模式的代码"""
        pass
    
    def remove_nodes(self, nodes: List[AstNode]) -> None:
        """删除指定的AST节点"""
        pass
    
    def insert_code_before(self, target_node: AstNode, new_code: str) -> None:
        """在指定节点前插入代码"""
        pass
    
    def insert_code_after(self, target_node: AstNode, new_code: str) -> None:
        """在指定节点后插入代码"""
        pass
```

### 4. 代码生成API

```python
class CodeGenerator:
    def create_import(self, module: str, items: List[str] = None) -> str:
        """生成导入语句"""
        pass
    
    def create_assignment(self, target: str, value: str) -> str:
        """生成赋值语句"""
        pass
    
    def create_function_call(self, function: str, args: List[str]) -> str:
        """生成函数调用"""
        pass
    
    def create_try_except(self, try_body: str, except_type: str, except_body: str) -> str:
        """生成try-except块"""
        pass
```

### 5. 上下文信息API

```python
class MatchContext:
    def get_assignment_target(self) -> str:
        """获取赋值语句的目标变量"""
        pass
    
    def get_function_arg(self, function_name: str, arg_index: int) -> str:
        """获取函数调用的参数"""
        pass
    
    def get_exception_type(self) -> str:
        """获取异常类型"""
        pass
    
    def get_variable_names(self) -> List[str]:
        """获取作用域内的变量名"""
        pass
```

## 使用示例

### 示例1：pkg_resources现代化

```python
# 用户代码
def modernize_pkg_resources(refactor):
    # 查找模式
    pattern = (refactor.pattern_builder()
              .has_imports(["pkg_resources.get_distribution"])
              .contains_try_except()
              .try_body_contains_call("get_distribution"))
    
    # 替换逻辑
    def replace_version_detection(node, context):
        var_name = context.get_assignment_target()
        pkg_name = context.get_function_arg("get_distribution", 0)
        return f"{var_name} = get_package_version({pkg_name})"
    
    # 应用替换
    refactor.replace_imports({"pkg_resources": "internal_pyharmony"})
    refactor.replace_matching_patterns(pattern, replace_version_detection)
```

### 示例2：字符串格式化现代化

```python
def modernize_string_formatting(refactor):
    # 查找%格式化
    old_format_calls = refactor.find_nodes(
        filter_func=lambda node: node.is_binary_op() and node.operator == "%"
    )
    
    # 替换为f-string
    for node in old_format_calls:
        if node.can_convert_to_fstring():
            new_code = node.to_fstring()
            refactor.replace_node(node, new_code)
```

### 示例3：导入现代化

```python
def modernize_imports(refactor, import_mapping):
    for old_import, new_import in import_mapping.items():
        # 查找旧导入
        old_import_nodes = refactor.find_imports(old_import)
        
        # 替换导入和相关调用
        refactor.replace_imports({old_import: new_import})
        
        # 更新函数调用
        for old_func, new_func in get_function_mapping(old_import, new_import):
            refactor.replace_function_calls(old_func, new_func)
```

## 优势

1. **通用性**：底层API可以支持各种代码转换需求
2. **灵活性**：用户可以组合基础API构建复杂功能
3. **可扩展性**：新的转换需求不需要修改核心API
4. **可组合性**：不同的转换可以链式组合
5. **可测试性**：每个底层API都可以独立测试

## 实现优先级

1. **高优先级**：节点查询API、基础替换API
2. **中优先级**：模式构建器、代码生成器
3. **低优先级**：高级组合API、性能优化

这种设计让PyRustor成为一个强大的底层工具，用户可以基于它快速构建各种高级代码转换功能。
