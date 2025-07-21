# PyRustor

[![PyPI version](https://img.shields.io/pypi/v/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyrustor.svg)](https://pypi.org/project/pyrustor/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-1.87+-orange.svg)](https://www.rust-lang.org)
[![CI](https://github.com/loonghao/PyRustor/workflows/CI/badge.svg)](https://github.com/loonghao/PyRustor/actions)

[English](README.md) | 中文

一个用 Rust 编写的**极速** Python 代码解析和重构工具，提供 Python 绑定。

## 🚀 特性

### 🌟 **核心优势**

- **⚡ 卓越性能**: 高性能 Rust 实现
- **🔄 Python AST 解析**: 将 Python 代码解析为 AST 进行分析
- **🛠️ 代码重构**: 重命名函数、类，现代化语法
- **🧵 安全并发**: 基于 Rust 的无畏并发构建
- **🐍 Python 绑定**: 易于使用的 Python API

### 🎛️ **重构操作**

- **函数重命名**: 在整个代码库中重命名函数
- **类重命名**: 重命名类并更新引用
- **导入现代化**: 将废弃的导入更新为现代替代方案
- **语法现代化**: 将旧的 Python 语法转换为现代模式
- **自定义转换**: 应用自定义 AST 转换

## 🚀 快速开始

```bash
pip install pyrustor
```

```python
import pyrustor

# 解析 Python 代码
parser = pyrustor.Parser()
ast = parser.parse_string("def hello(): pass")

# 创建重构实例
refactor = pyrustor.Refactor(ast)
refactor.rename_function("hello", "greet")

# 获取修改后的代码
result = refactor.to_string()
print(result)  # def greet(): pass
```

## 📦 安装

### 从 PyPI 安装（推荐）

```bash
# 标准安装（特定 Python 版本的 wheel）
pip install pyrustor

# ABI3 安装（兼容 Python 3.8+）
pip install pyrustor --prefer-binary
```

### 前置要求（从源码构建）

- Rust 1.87+（用于从源码构建）
- Python 3.8+
- maturin（用于构建 Python 绑定）

### 从源码构建

```bash
# 克隆仓库
git clone https://github.com/loonghao/PyRustor.git
cd PyRustor

# 安装依赖
just install

# 构建扩展
just build
```

## 🔧 使用示例

### 基本操作

```python
import pyrustor

# 解析 Python 代码
parser = pyrustor.Parser()
ast = parser.parse_string("""
def old_function():
    return "Hello, World!"

class OldClass:
    pass
""")

# 创建重构实例
refactor = pyrustor.Refactor(ast)

# 重命名函数
refactor.rename_function("old_function", "new_function")

# 重命名类
refactor.rename_class("OldClass", "NewClass")

# 获取重构后的代码
print(refactor.to_string())
```

### 文件操作

```python
import pyrustor

# 从文件解析
parser = pyrustor.Parser()
ast = parser.parse_file("example.py")

# 应用重构
refactor = pyrustor.Refactor(ast)
refactor.modernize_syntax()

# 保存到文件
refactor.save_to_file("refactored_example.py")

# 获取变更摘要
print(refactor.change_summary())
```

### 高级重构

```python
import pyrustor

parser = pyrustor.Parser()
ast = parser.parse_string("""
import ConfigParser
from imp import reload

def format_string(name, age):
    return "Name: %s, Age: %d" % (name, age)
""")

refactor = pyrustor.Refactor(ast)

# 现代化导入
refactor.replace_import("ConfigParser", "configparser")
refactor.replace_import("imp", "importlib")

# 现代化语法
refactor.modernize_syntax()

print(refactor.to_string())
print("所做的更改:")
print(refactor.change_summary())
```

## 📚 API 参考

### Parser 类

```python
parser = pyrustor.Parser()

# 从字符串解析
ast = parser.parse_string(source_code)

# 从文件解析
ast = parser.parse_file("path/to/file.py")

# 解析目录
results = parser.parse_directory("path/to/dir", recursive=True)
```

### PythonAst 类

```python
# 检查 AST 是否为空
if ast.is_empty():
    print("未找到代码")

# 获取统计信息
print(f"语句数: {ast.statement_count()}")
print(f"函数: {ast.function_names()}")
print(f"类: {ast.class_names()}")
print(f"导入: {ast.imports()}")

# 转换回字符串
source_code = ast.to_string()
```

### Refactor 类

```python
refactor = pyrustor.Refactor(ast)

# 基本重构
refactor.rename_function("old_name", "new_name")
refactor.rename_class("OldClass", "NewClass")
refactor.replace_import("old_module", "new_module")

# 高级重构
refactor.modernize_syntax()
refactor.modernize_imports()

# 获取结果
refactored_code = refactor.to_string()
changes = refactor.change_summary()

# 保存到文件
refactor.save_to_file("output.py")
```

## 🧪 开发

### 设置开发环境

```bash
# 安装 just（命令运行器）
cargo install just

# 设置开发环境
just dev

# 运行测试
just test

# 格式化代码
just format

# 运行 lint
just lint

# 构建发布版本
just release
```

### 可用命令

```bash
just --list  # 显示所有可用命令
```

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 添加测试
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [ruff](https://github.com/astral-sh/ruff) 提供 Python AST 解析
- [PyO3](https://github.com/PyO3/pyo3) 提供优秀的 Python-Rust 绑定
- [maturin](https://github.com/PyO3/maturin) 提供无缝的 Python 包构建
