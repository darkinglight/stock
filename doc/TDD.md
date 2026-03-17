# Test-Driven Development (TDD) Guide

## 概述

本文档详细描述了如何在股票项目中实施测试驱动开发（TDD）方法论。

## TDD 核心理念

### 什么是 TDD？

测试驱动开发（Test-Driven Development，TDD）是一种软件开发方法论，要求在编写功能代码之前先编写测试代码。

### TDD 的好处

- **提高代码质量**: 测试用例作为需求文档，确保代码满足预期
- **减少缺陷**: 通过持续测试，及早发现和修复问题
- **改善设计**: 测试驱动设计，使代码更模块化、更易维护
- **提供文档**: 测试用例本身就是最好的文档
- **增强信心**: 重构时有测试保护，不用担心破坏现有功能

## TDD 开发循环

### 红-绿-重构循环

```
┌─────────┐
│   红    │  编写一个失败的测试
│  (Red)  │
└────┬────┘
     │
     ▼
┌─────────┐
│   绿    │  编写最少代码使测试通过
│(Green)  │
└────┬────┘
     │
     ▼
┌─────────┐
│  重构   │  优化代码，保持测试通过
│(Refactor)│
└────┬────┘
     │
     ▼
   循环...
```

### 详细步骤

#### 1. 红（Red）- 编写失败的测试

```python
# tests/test_a_stock/test_stock_repository.py
import pytest
from src.a_stock.data.stock_repository import StockRepository

def test_add_stock():
    """测试添加股票"""
    repository = StockRepository(":memory:")
    repository.init_table()
    
    result = repository.add_stock("600000", "浦发银行", 10.5)
    assert result is True
    
    stock = repository.get_stock("600000")
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5
```

运行测试，预期失败：

```bash
pytest tests/test_a_stock/test_stock_repository.py::test_add_stock -v
# 结果: FAILED (add_stock 方法未实现)
```

#### 2. 绿（Green）- 编写最少代码使测试通过

```python
# src/a_stock/data/stock_repository.py
from src.database.base_repository import BaseRepository
from collections import namedtuple

Stock = namedtuple("Stock", ["code", "name", "price"])

class StockRepository(BaseRepository):
    """A 股数据仓储"""
    
    def init_table(self):
        """初始化数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS a_stock (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL
        )
        """
        return self.create_table(sql)
    
    def add_stock(self, code: str, name: str, price: float) -> bool:
        """添加股票"""
        sql = "INSERT INTO a_stock (code, name, price) VALUES (?, ?, ?)"
        return self.insert(sql, (code, name, price))
    
    def get_stock(self, code: str):
        """获取单个股票"""
        sql = "SELECT code, name, price FROM a_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return Stock(*result)
        return None
```

运行测试，预期通过：

```bash
pytest tests/test_a_stock/test_stock_repository.py::test_add_stock -v
# 结果: PASSED
```

#### 3. 重构（Refactor）- 优化代码

```python
# 添加参数验证、错误处理等
def add_stock(self, code: str, name: str, price: float) -> bool:
    """添加股票"""
    if not code or not name or price <= 0:
        return False
    
    sql = "INSERT INTO a_stock (code, name, price) VALUES (?, ?, ?)"
    return self.insert(sql, (code, name, price))
```

确保测试仍然通过：

```bash
pytest tests/test_a_stock/test_stock_repository.py::test_add_stock -v
# 结果: PASSED
```

## TDD 实施原则

### 1. 先写测试，后写代码

在编写任何功能代码之前，先编写测试用例：

```python
# 好的做法 - 先写测试
def test_calculate_roe():
    """测试计算净资产收益率"""
    result = calculate_roe(net_profit=100, total_equity=1000)
    assert result == 0.1

# 然后实现功能
def calculate_roe(net_profit: float, total_equity: float) -> float:
    return net_profit / total_equity

# 不好的做法 - 先写代码
def calculate_roe(net_profit: float, total_equity: float) -> float:
    return net_profit / total_equity

# 然后写测试
def test_calculate_roe():
    result = calculate_roe(100, 1000)
    assert result == 0.1
```

### 2. 小步快跑

每次只实现一个小的功能，确保测试通过：

```python
# 好的做法 - 小步快跑
def test_add_stock():
    """测试添加股票"""
    repository.add_stock("600000", "浦发银行", 10.5)
    assert repository.get_stock("600000") is not None

def test_add_duplicate_stock():
    """测试添加重复股票"""
    repository.add_stock("600000", "浦发银行", 10.5)
    result = repository.add_stock("600000", "浦发银行", 11.0)
    assert result is False

# 不好的做法 - 一次实现多个功能
def test_add_and_delete_stock():
    """测试添加和删除股票"""
    repository.add_stock("600000", "浦发银行", 10.5)
    repository.delete_stock("600000")
    assert repository.get_stock("600000") is None
```

### 3. 持续重构

在保持测试通过的前提下，不断优化代码结构：

```python
# 重构前
def get_stock(self, code: str):
    sql = f"SELECT * FROM a_stock WHERE code = '{code}'"
    result = self.query_one(sql)
    if result:
        return Stock(*result)
    return None

# 重构后 - 使用参数化查询
def get_stock(self, code: str):
    sql = "SELECT * FROM a_stock WHERE code = ?"
    result = self.query_one(sql, (code,))
    if result:
        return Stock(*result)
    return None

# 确保测试仍然通过
```

### 4. 测试覆盖

确保所有核心功能都有对应的测试用例：

```python
# 测试正常情况
def test_add_stock():
    """测试添加股票"""
    pass

# 测试边界情况
def test_add_stock_with_invalid_price():
    """测试添加价格为负的股票"""
    pass

# 测试异常情况
def test_add_stock_with_empty_code():
    """测试添加代码为空的股票"""
    pass
```

## TDD 实践示例

### 示例 1：数据库连接管理器

#### 步骤1：编写测试用例

```python
# tests/test_database/test_connection.py
import pytest
from src.database.connection import DatabaseConnectionManager

def test_get_connection():
    """测试获取数据库连接"""
    db_manager = DatabaseConnectionManager()
    conn = db_manager.get_connection(":memory:")
    assert conn is not None
    assert conn.cursor() is not None

def test_connection_reuse():
    """测试连接复用"""
    db_manager = DatabaseConnectionManager()
    conn1 = db_manager.get_connection(":memory:")
    conn2 = db_manager.get_connection(":memory:")
    assert conn1 is conn2

def test_close_connection():
    """测试关闭连接"""
    db_manager = DatabaseConnectionManager()
    conn = db_manager.get_connection(":memory:")
    db_manager.close_connection(":memory:")
    assert len(db_manager._connections) == 0
```

#### 步骤2：实现功能

```python
# src/database/connection.py
import sqlite3
import threading
from typing import Dict, Optional

class DatabaseConnectionManager:
    """数据库连接管理器"""
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _connections: Dict[str, sqlite3.Connection] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """获取数据库连接"""
        if db_name not in self._connections:
            with self._lock:
                if db_name not in self._connections:
                    conn = sqlite3.connect(db_name, check_same_thread=False)
                    self._connections[db_name] = conn
        return self._connections[db_name]
    
    def close_connection(self, db_name: str):
        """关闭指定数据库连接"""
        if db_name in self._connections:
            with self._lock:
                if db_name in self._connections:
                    self._connections[db_name].close()
                    del self._connections[db_name]
```

#### 步骤3：运行测试并验证

```bash
pytest tests/test_database/test_connection.py -v
# 结果: PASSED
```

### 示例 2：股票仓储类

#### 步骤1：编写测试用例

```python
# tests/test_a_stock/test_stock_repository.py
import pytest
from src.a_stock.data.stock_repository import StockRepository

@pytest.fixture
def repository():
    """创建测试用的仓储实例"""
    return StockRepository(":memory:")

def test_init_table(repository):
    """测试初始化数据表"""
    result = repository.init_table()
    assert result is True
    assert repository.table_exists("a_stock") is True

def test_add_stock(repository):
    """测试添加股票"""
    repository.init_table()
    result = repository.add_stock("600000", "浦发银行", 10.5)
    assert result is True
    
    stock = repository.get_stock("600000")
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5

def test_get_stock_not_found(repository):
    """测试查询不存在的股票"""
    repository.init_table()
    stock = repository.get_stock("999999")
    assert stock is None

def test_get_all_stocks(repository):
    """测试获取所有股票"""
    repository.init_table()
    repository.add_stock("600000", "浦发银行", 10.5)
    repository.add_stock("000001", "平安银行", 12.3)
    
    stocks = repository.get_all_stocks()
    assert len(stocks) == 2
    assert stocks[0].code == "600000"
    assert stocks[1].code == "000001"

def test_delete_stock(repository):
    """测试删除股票"""
    repository.init_table()
    repository.add_stock("600000", "浦发银行", 10.5)
    
    result = repository.delete_stock("600000")
    assert result is True
    
    stock = repository.get_stock("600000")
    assert stock is None
```

#### 步骤2：实现功能

```python
# src/a_stock/data/stock_repository.py
from src.database.base_repository import BaseRepository
from collections import namedtuple

Stock = namedtuple("Stock", ["code", "name", "price"])

class StockRepository(BaseRepository):
    """A 股数据仓储"""
    
    def init_table(self):
        """初始化数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS a_stock (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL
        )
        """
        return self.create_table(sql)
    
    def add_stock(self, code: str, name: str, price: float) -> bool:
        """添加股票"""
        sql = "INSERT INTO a_stock (code, name, price) VALUES (?, ?, ?)"
        return self.insert(sql, (code, name, price))
    
    def get_stock(self, code: str):
        """获取单个股票"""
        sql = "SELECT code, name, price FROM a_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return Stock(*result)
        return None
    
    def get_all_stocks(self):
        """获取所有股票"""
        sql = "SELECT code, name, price FROM a_stock"
        results = self.query_many(sql)
        return [Stock(*row) for row in results]
    
    def delete_stock(self, code: str) -> bool:
        """删除股票"""
        sql = "DELETE FROM a_stock WHERE code = ?"
        return self.delete(sql)
```

#### 步骤3：运行测试并验证

```bash
pytest tests/test_a_stock/test_stock_repository.py -v
# 结果: PASSED
```

## 测试覆盖率要求

### 覆盖率标准

- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 60%
- **关键路径覆盖率**: 100%

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 覆盖率报告解读

```
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/database/connection.py               45      5    89%   23-27
src/database/base_repository.py          78     12    85%   45-50, 67-70
src/a_stock/data/stock_repository.py     92      8    91%   101-105
-----------------------------------------------------------------------
TOTAL                                215     25    88%
```

- **Stmts**: 语句总数
- **Miss**: 未覆盖的语句数
- **Cover**: 覆盖率
- **Missing**: 未覆盖的行号

## 运行测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 运行特定模块测试

```bash
pytest tests/test_a_stock/ -v
pytest tests/test_h_stock/ -v
```

### 运行特定测试文件

```bash
pytest tests/test_database/test_connection.py -v
```

### 运行特定测试函数

```bash
pytest tests/test_database/test_connection.py::test_get_connection -v
```

### 运行失败的测试

```bash
pytest tests/ -v --lf
# --lf: last-failed，只运行上次失败的测试
```

### 并行运行测试

```bash
pytest tests/ -v -n auto
# -n auto: 自动检测 CPU 核心数并并行运行
```

## 持续集成

### 提交前检查

```bash
# 运行所有测试
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 检查代码风格
flake8 src/
```

### 预提交钩子

创建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash

# 运行测试
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix them before committing."
    exit 1
fi

# 检查代码风格
flake8 src/
if [ $? -ne 0 ]; then
    echo "Code style check failed. Please fix the issues."
    exit 1
fi

exit 0
```

## 常见问题

### Q1: 如何处理外部依赖？

```python
# 使用 mock 模拟外部依赖
from unittest.mock import patch
import pytest

def test_fetch_from_api():
    """测试从 API 获取数据"""
    with patch('src.utils.data_fetcher.fetch_data') as mock_fetch:
        mock_fetch.return_value = {"code": "600000", "name": "浦发银行"}
        
        result = fetch_from_api("600000")
        assert result["code"] == "600000"
        assert result["name"] == "浦发银行"
```

### Q2: 如何测试异步代码？

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_function()
    assert result is not None
```

### Q3: 如何测试 UI 组件？

```python
import pytest
from src.a_stock.view.stock_list_view import StockListView

def test_view_initialization():
    """测试视图初始化"""
    repository = StockRepository(":memory:")
    repository.init_table()
    repository.add_stock("600000", "浦发银行", 10.5)
    
    view = StockListView(repository)
    assert view is not None
    assert view.table is not None
    assert len(view.table.data) == 1
```

## 总结

TDD 是一种强大的开发方法论，通过先写测试后写代码的方式，确保代码质量和可维护性。遵循红-绿-重构的循环，小步快跑，持续重构，可以显著提高开发效率和代码质量。

## 相关文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计文档
- [DATABASE.md](DATABASE.md) - 数据库设计文档
- [MIGRATION.md](MIGRATION.md) - 迁移指南
- [QUICK_START.md](QUICK_START.md) - 快速开始指南