# 底层优先的API设计哲学

## 核心理念

**提供强大的底层构建块，让用户能够快速组合出高级功能，而不是提供特定的高级方法。**

## 为什么选择底层API？

### 1. 灵活性 > 便利性
```python
# ❌ 不推荐：特定的高级方法
refactor.modernize_pkg_resources_version()
refactor.modernize_urllib2()
refactor.modernize_configparser()
# 问题：每个特定需求都需要新的方法

# ✅ 推荐：通用的底层API
refactor.replace_pattern(matcher, replacer)
refactor.find_nodes(filter_func)
refactor.replace_node(node, new_code)
# 优势：用户可以组合出任何转换
```

### 2. 可扩展性 > 完整性
```python
# 用户可以基于底层API构建自己的高级功能
def modernize_pkg_resources(refactor):
    pattern = find_pkg_resources_pattern(refactor.ast)
    if pattern:
        new_code = generate_modern_version(pattern)
        refactor.replace_node(pattern.node, new_code)

def modernize_string_formatting(refactor):
    old_formats = refactor.ast.find_nodes(filter_func=is_percent_format)
    for node in old_formats:
        fstring = convert_to_fstring(node)
        refactor.replace_node(node, fstring)
```

### 3. 组合性 > 单一功能
```python
# 用户可以组合多个转换
def comprehensive_modernization(refactor):
    modernize_imports(refactor, IMPORT_MAPPING)
    modernize_string_formatting(refactor)
    modernize_pkg_resources(refactor)
    modernize_exception_handling(refactor)
```

## 建议的底层API层次

### 第1层：AST访问和查询
```python
# 最底层：直接访问AST节点
ast.find_nodes(node_type="try_except")
ast.find_imports(module="pkg_resources")
ast.find_function_calls("get_distribution")
```

### 第2层：节点操作
```python
# 节点级别的操作
refactor.replace_node(node, new_code)
refactor.remove_node(node)
refactor.insert_before(node, code)
```

### 第3层：模式匹配
```python
# 模式级别的操作
pattern = PatternMatcher(ast).has_imports(["pkg_resources"]).contains_try_except()
matches = pattern.find_matches()
```

### 第4层：代码生成
```python
# 代码生成辅助
CodeGenerator.create_import("internal_pyharmony", ["get_package_version"])
CodeGenerator.create_assignment("__version__", "get_package_version(__name__)")
```

### 第5层：用户组合（不在核心API中）
```python
# 用户基于底层API构建的高级功能
def modernize_pkg_resources(refactor):
    # 使用第1-4层API的组合
    pass
```

## 实际应用示例

### 用户需求：pkg_resources现代化

**输入：**
```python
from pkg_resources import DistributionNotFound
from pkg_resources import get_distribution

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0-dev.1"
```

**期望输出：**
```python
from internal_pyharmony import get_package_version

__version__ = get_package_version(__name__)
```

**用户基于底层API的实现：**
```python
def modernize_pkg_resources_version(refactor, target_module="internal_pyharmony"):
    ast = refactor.ast
    
    # 1. 查找模式（使用第1层API）
    try_except_nodes = ast.find_try_except_blocks("DistributionNotFound")
    pkg_imports = ast.find_imports("pkg_resources")
    
    # 2. 验证模式
    valid_patterns = []
    for node in try_except_nodes:
        if has_get_distribution_call(node):
            valid_patterns.append(node)
    
    if not valid_patterns or not pkg_imports:
        return False
    
    # 3. 替换节点（使用第2层API）
    for pattern_node in valid_patterns:
        # 提取信息
        var_name = extract_assignment_target(pattern_node)
        pkg_arg = extract_package_argument(pattern_node)
        
        # 生成新代码（使用第4层API）
        new_code = CodeGenerator.create_assignment(
            var_name, 
            f"get_package_version({pkg_arg})"
        )
        
        # 替换节点
        refactor.replace_node(pattern_node, new_code)
    
    # 4. 更新导入
    refactor.replace_import("pkg_resources", target_module)
    
    return True

# 使用
success = modernize_pkg_resources_version(refactor)
```

## 与现有API的关系

### 保持现有高级API
```python
# 现有的高级API继续保留
refactor.rename_function("old", "new")
refactor.rename_class("Old", "New")
refactor.replace_import("old", "new")
refactor.modernize_syntax()
```

### 添加底层API
```python
# 新增的底层API
refactor.find_nodes(filter_func)
refactor.replace_node(node, code)
refactor.pattern_matcher()
refactor.code_generator()
```

### 两者协同工作
```python
# 用户可以混合使用
def comprehensive_refactor(refactor):
    # 使用高级API处理简单情况
    refactor.replace_import("urllib2", "urllib.request")
    refactor.rename_function("old_func", "new_func")
    
    # 使用底层API处理复杂情况
    custom_modernize_pkg_resources(refactor)
    custom_modernize_string_formatting(refactor)
```

## 实现策略

### 阶段1：核心底层API
1. **AST节点查询**：`find_nodes`, `find_imports`, `find_function_calls`
2. **节点操作**：`replace_node`, `remove_node`
3. **基础代码生成**：`CodeGenerator`类

### 阶段2：模式匹配
1. **模式构建器**：`PatternMatcher`类
2. **复杂查询**：支持组合条件的查询
3. **上下文提取**：从匹配中提取信息

### 阶段3：生态系统
1. **示例库**：常见转换的示例代码
2. **工具函数**：常用的辅助函数
3. **文档和教程**：如何基于底层API构建高级功能

## 优势总结

1. **未来证明**：新的转换需求不需要修改核心API
2. **用户赋能**：用户可以构建任何他们需要的转换
3. **社区驱动**：社区可以分享转换模式和最佳实践
4. **性能优化**：底层API可以高度优化
5. **测试友好**：每个底层API都可以独立测试

## 设计原则

1. **组合优于继承**：提供可组合的小功能
2. **约定优于配置**：合理的默认值和行为
3. **显式优于隐式**：用户明确控制转换过程
4. **简单优于复杂**：每个API做一件事并做好
5. **可扩展优于完整**：提供扩展点而不是覆盖所有用例

这种设计哲学让PyRustor成为一个强大的平台，而不仅仅是一个工具。用户可以基于它构建任何他们需要的代码转换功能，而不受核心API的限制。
