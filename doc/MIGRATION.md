# Migration Guide

## 概述

本文档指导如何将现有项目从当前架构迁移到新的模块化架构。

## 迁移目标

1. **统一数据库管理**: 使用 DatabaseConnectionManager 统一管理所有数据库连接
2. **模块化分离**: 将 A 股和 H 股模块完全分离
3. **分层架构**: 严格分离数据层和视图层
4. **提高性能**: 减少数据库重连，优化查询性能

## 迁移前准备

### 1. 备份现有代码

```bash
# 创建备份目录
mkdir -p backup/$(date +%Y%m%d)

# 备份源代码
cp -r src backup/$(date +%Y%m%d)/

# 备份数据库
cp finance.db backup/$(date +%Y%m%d)/
```

### 2. 检查当前依赖

```bash
# 查看当前安装的包
uv pip list

# 确认所有依赖都记录在 pyproject.toml 中
cat pyproject.toml
```

### 3. 运行现有测试

```bash
# 运行所有测试
python -m pytest tests/

# 确保所有测试通过
```

## 迁移步骤

### 第一阶段：创建新的目录结构

#### 1.1 创建目录结构

```bash
# 创建数据库管理目录
mkdir -p src/database

# 创建 A 股模块目录
mkdir -p src/a_stock/entities
mkdir -p src/a_stock/repositories
mkdir -p src/a_stock/services
mkdir -p src/a_stock/view

# 创建 H 股模块目录
mkdir -p src/h_stock/entities
mkdir -p src/h_stock/repositories
mkdir -p src/h_stock/services
mkdir -p src/h_stock/view

# 创建 UI 模块目录
mkdir -p src/ui/components

# 创建工具模块目录
mkdir -p src/utils

# 创建测试目录
mkdir -p tests/test_database
mkdir -p tests/test_a_stock/test_entities
mkdir -p tests/test_a_stock/test_repositories
mkdir -p tests/test_a_stock/test_services
mkdir -p tests/test_h_stock/test_entities
mkdir -p tests/test_h_stock/test_repositories
mkdir -p tests/test_h_stock/test_services
```

#### 1.2 创建 __init__.py 文件

```bash
# 为所有目录创建 __init__.py
find src -type d -exec touch {}/__init__.py \;
find tests -type d -exec touch {}/__init__.py \;
```

### 第二阶段：重构数据库连接管理

#### 2.1 创建数据库连接管理器

创建文件 `src/database/connection.py`:

```python
import sqlite3
import threading
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    数据库连接管理器
    - 延迟创建连接
    - 连接复用，减少重连
    - 自动释放连接
    - 线程安全
    """
    
    _instance: Optional['DatabaseConnectionManager'] = None
    _connections: Dict[str, sqlite3.Connection] = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    logger.info("DatabaseConnectionManager instance created")
        return cls._instance
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """
        获取数据库连接，如果不存在则创建
        :param db_name: 数据库名称
        :return: 数据库连接对象
        """
        if db_name not in self._connections:
            with self._lock:
                if db_name not in self._connections:
                    try:
                        conn = sqlite3.connect(db_name, check_same_thread=False)
                        conn.row_factory = sqlite3.Row
                        self._connections[db_name] = conn
                        logger.info(f"Created new connection for database: {db_name}")
                    except Exception as e:
                        logger.error(f"Failed to create connection for {db_name}: {e}")
                        raise
        return self._connections[db_name]
    
    def close_connection(self, db_name: str):
        """
        关闭指定数据库连接
        :param db_name: 数据库名称
        """
        if db_name in self._connections:
            with self._lock:
                if db_name in self._connections:
                    try:
                        self._connections[db_name].close()
                        del self._connections[db_name]
                        logger.info(f"Closed connection for database: {db_name}")
                    except Exception as e:
                        logger.error(f"Failed to close connection for {db_name}: {e}")
    
    def close_all(self):
        """
        关闭所有数据库连接
        """
        with self._lock:
            for db_name, conn in list(self._connections.items()):
                try:
                    conn.close()
                    logger.info(f"Closed connection for database: {db_name}")
                except Exception as e:
                    logger.error(f"Failed to close connection for {db_name}: {e}")
            self._connections.clear()
            logger.info("All database connections closed")
    
    def get_cursor(self, db_name: str = "finance.db") -> sqlite3.Cursor:
        """
        获取数据库游标
        :param db_name: 数据库名称
        :return: 数据库游标对象
        """
        conn = self.get_connection(db_name)
        return conn.cursor()
```

#### 2.2 创建基础仓储类

创建文件 `src/database/base_repository.py`:

```python
from typing import Optional, List, Union
from .connection import DatabaseConnectionManager
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """
    基础仓储类
    提供通用的数据库操作方法
    """
    
    def __init__(self, db_name: str = "finance.db"):
        """
        初始化仓储
        :param db_name: 数据库名称
        """
        self.db_name = db_name
        self.db_manager = DatabaseConnectionManager()
    
    def create_table(self, sql: str) -> bool:
        """
        创建表
        :param sql: CREATE TABLE SQL 语句
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            logger.info("Table created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """
        删除表
        :param table_name: 表名
        :return: 是否成功
        """
        try:
            sql = f"DROP TABLE IF EXISTS {table_name}"
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            logger.info(f"Table {table_name} dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop table {table_name}: {e}")
            return False
    
    def insert(self, sql: str, data: Union[tuple, list]) -> bool:
        """
        插入数据
        :param sql: INSERT SQL 语句
        :param data: 插入的数据
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if isinstance(data, list):
                cursor.executemany(sql, data)
            else:
                cursor.execute(sql, data)
            conn.commit()
            logger.info("Data inserted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            conn.rollback()
            return False
    
    def update(self, sql: str, data: Union[tuple, list]) -> bool:
        """
        更新数据
        :param sql: UPDATE SQL 语句
        :param data: 更新的数据
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if isinstance(data, list):
                cursor.executemany(sql, data)
            else:
                cursor.execute(sql, data)
            conn.commit()
            logger.info("Data updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update data: {e}")
            conn.rollback()
            return False
    
    def delete(self, sql: str) -> bool:
        """
        删除数据
        :param sql: DELETE SQL 语句
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            logger.info("Data deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            conn.rollback()
            return False
    
    def query_one(self, sql: str, params: tuple = None) -> Optional[tuple]:
        """
        查询单条数据
        :param sql: SELECT SQL 语句
        :param params: 查询参数
        :return: 查询结果
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error(f"Failed to query one: {e}")
            return None
    
    def query_many(self, sql: str, params: tuple = None) -> List[tuple]:
        """
        查询多条数据
        :param sql: SELECT SQL 语句
        :param params: 查询参数
        :return: 查询结果列表
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as e:
            logger.error(f"Failed to query many: {e}")
            return []
    
    def execute(self, sql: str, params: tuple = None) -> bool:
        """
        执行 SQL 语句
        :param sql: SQL 语句
        :param params: 参数
        :return: 是否成功
        """
        try:
            conn = self.db_manager.get_connection(self.db_name)
            cursor = conn.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            conn.rollback()
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        :param table_name: 表名
        :return: 是否存在
        """
        sql = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?"
        result = self.query_one(sql, (table_name,))
        return result[0] == 1 if result else False
```

### 第三阶段：重构 A 股模块

#### 3.1 创建 A 股实体层

创建 A 股的实体类，使用 dataclass 替代 namedtuple：

```python
# src/a_stock/entities/stock.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """A 股实体"""
    code: str
    name: str
    market: str
    code_number: str
    industry: Optional[str] = None
    list_date: Optional[str] = None
    status: int = 1
    
    def validate(self) -> bool:
        """验证实体数据"""
        if not self.code or not self.name:
            return False
        return True
```

#### 3.2 重构 A 股仓储层

将 `src/hs/` 下的数据层文件迁移到 `src/a_stock/repositories/`，并重构为纯数据访问：

```bash
# 迁移仓储层文件
cp src/hs/HsStock.py src/a_stock/repositories/stock_repository.py
cp src/hs/HsDetail.py src/a_stock/repositories/detail_repository.py
cp src/hs/HsFinancial.py src/a_stock/repositories/financial_repository.py
cp src/hs/HsIndicator.py src/a_stock/repositories/indicator_repository.py
```

重构仓储类，移除业务逻辑，只保留数据访问：

```python
# src/a_stock/repositories/stock_repository.py
from src.database.base_repository import BaseRepository
from src.a_stock.entities.stock import Stock

class StockRepository(BaseRepository):
    """A 股数据仓储 - 纯数据访问"""
    
    def init_table(self):
        """初始化数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS a_stock (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            market TEXT,
            code_number TEXT,
            industry TEXT,
            list_date TEXT,
            status INTEGER DEFAULT 1
        )
        """
        return self.create_table(sql)
    
    def save(self, stock: Stock) -> bool:
        """保存股票实体"""
        sql = """
        INSERT INTO a_stock (code, name, market, code_number, industry, list_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            name=excluded.name,
            market=excluded.market,
            code_number=excluded.code_number,
            industry=excluded.industry,
            list_date=excluded.list_date,
            status=excluded.status
        """
        return self.insert(sql, (
            stock.code, stock.name, stock.market, stock.code_number,
            stock.industry, stock.list_date, stock.status
        ))
    
    def find_by_code(self, code: str) -> Optional[Stock]:
        """根据代码查询股票"""
        sql = "SELECT * FROM a_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return Stock(*result)
        return None
    
    def find_all(self) -> List[Stock]:
        """查询所有股票"""
        sql = "SELECT * FROM a_stock WHERE status = 1"
        results = self.query_many(sql)
        return [Stock(*row) for row in results]
```

#### 3.3 创建 A 股服务层

创建 A 股的服务类，将业务逻辑从仓储层分离：

```python
# src/a_stock/services/stock_service.py
from typing import List, Optional
from src.a_stock.repositories.stock_repository import StockRepository
from src.a_stock.entities.stock import Stock
import akshare as ak

class StockService:
    """A 股服务 - 业务逻辑层"""
    
    def __init__(self, repository: StockRepository):
        self.repository = repository
    
    def get_all_stocks(self) -> List[Stock]:
        """获取所有股票"""
        return self.repository.find_all()
    
    def get_stock_by_code(self, code: str) -> Optional[Stock]:
        """根据代码获取股票"""
        return self.repository.find_by_code(code)
    
    def fetch_and_save_stocks(self) -> int:
        """从 API 获取并保存股票数据"""
        stocks = self._fetch_from_api()
        count = 0
        for stock in stocks:
            if stock.validate():
                self.repository.save(stock)
                count += 1
        return count
    
    def _fetch_from_api(self) -> List[Stock]:
        """从外部 API 获取数据（内部方法）"""
        df = ak.stock_zh_a_spot()
        stocks = []
        for _, row in df.iterrows():
            stock = Stock(
                code=str(row['code']),
                name=str(row['name']),
                market='SH' if str(row['code']).startswith('6') else 'SZ',
                code_number=str(row['code']),
                industry=None,
                list_date=None,
                status=1
            )
            stocks.append(stock)
        return stocks
```

#### 3.4 重构 A 股视图层

将 `src/hs/` 下的视图层文件迁移到 `src/a_stock/view/`，并更新为调用服务层：

```bash
# 迁移视图层文件
cp src/hs/HsFacade.py src/a_stock/view/stock_list_view.py
```

重构视图类，改为调用服务层而不是仓储层：

```python
# src/a_stock/view/stock_list_view.py
import toga
from toga.style import Pack
from src.a_stock.services.stock_service import StockService
from src.a_stock.entities.stock import Stock

class StockListView(toga.Box):
    """A 股列表视图"""
    
    def __init__(self, service: StockService):
        self.service = service
        super().__init__(children=[self._create_ui()])
    
    def _create_ui(self) -> toga.Box:
        """创建 UI"""
        self.table = toga.Table(
            headings=["代码", "名称", "市场", "行业"],
            on_select=self._on_select,
            style=Pack(flex=1)
        )
        
        refresh_button = toga.Button(
            "刷新数据",
            on_press=self._refresh_data,
            style=Pack(padding=10)
        )
        
        return toga.Box(
            children=[self.table, refresh_button],
            style=Pack(direction=Column, flex=1)
        )
    
    def _refresh_data(self, widget):
        """刷新数据"""
        count = self.service.fetch_and_save_stocks()
        self._update_table()
    
    def _update_table(self):
        """更新表格数据"""
        stocks = self.service.get_all_stocks()
        data = [
            (stock.code, stock.name, stock.market, stock.industry or '-')
            for stock in stocks
        ]
        self.table.data = data
    
    def _on_select(self, widget, row):
        """选择行时的回调"""
        if row:
            code = row[0]
            stock = self.service.get_stock_by_code(code)
            print(f"Selected stock: {stock.code} - {stock.name}")
```

### 第四阶段：重构 H 股模块

#### 4.1 创建 H 股实体层

创建 H 股的实体类，使用 dataclass 替代 namedtuple：

```python
# src/h_stock/entities/stock.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """H 股实体"""
    code: str
    name: str
    price: Optional[float] = None
    market_cap: Optional[float] = None
    circulating_cap: Optional[float] = None
    update_at: Optional[str] = None
    
    def validate(self) -> bool:
        """验证实体数据"""
        if not self.code or not self.name:
            return False
        return True
```

#### 4.2 重构 H 股仓储层

将 `src/stocks/hkstock.py` 和 `src/stocks/hkfinancial.py` 迁移到 `src/h_stock/repositories/`，并重构为纯数据访问：

```bash
# 迁移仓储层文件
cp src/stocks/hkstock.py src/h_stock/repositories/stock_repository.py
cp src/stocks/hkfinancial.py src/h_stock/repositories/financial_repository.py
cp src/hk/hkreport.py src/h_stock/repositories/report_repository.py
```

重构仓储类，移除业务逻辑，只保留数据访问：

```python
# src/h_stock/repositories/stock_repository.py
from src.database.base_repository import BaseRepository
from src.h_stock.entities.stock import Stock

class StockRepository(BaseRepository):
    """H 股数据仓储 - 纯数据访问"""
    
    def init_table(self):
        """初始化数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS h_stock (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            market_cap REAL,
            circulating_cap REAL,
            update_at TEXT
        )
        """
        return self.create_table(sql)
    
    def save(self, stock: Stock) -> bool:
        """保存股票实体"""
        sql = """
        INSERT INTO h_stock (code, name, price, market_cap, circulating_cap, update_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            name=excluded.name,
            price=excluded.price,
            market_cap=excluded.market_cap,
            circulating_cap=excluded.circulating_cap,
            update_at=excluded.update_at
        """
        return self.insert(sql, (
            stock.code, stock.name, stock.price, stock.market_cap,
            stock.circulating_cap, stock.update_at
        ))
    
    def find_by_code(self, code: str) -> Optional[Stock]:
        """根据代码查询股票"""
        sql = "SELECT * FROM h_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return Stock(*result)
        return None
    
    def find_all(self) -> List[Stock]:
        """查询所有股票"""
        sql = "SELECT * FROM h_stock"
        results = self.query_many(sql)
        return [Stock(*row) for row in results]
```

#### 4.3 创建 H 股服务层

创建 H 股的服务类，将业务逻辑从仓储层分离：

```python
# src/h_stock/services/stock_service.py
from typing import List, Optional
from src.h_stock.repositories.stock_repository import StockRepository
from src.h_stock.entities.stock import Stock
import akshare as ak

class StockService:
    """H 股服务 - 业务逻辑层"""
    
    def __init__(self, repository: StockRepository):
        self.repository = repository
    
    def get_all_stocks(self) -> List[Stock]:
        """获取所有股票"""
        return self.repository.find_all()
    
    def get_stock_by_code(self, code: str) -> Optional[Stock]:
        """根据代码获取股票"""
        return self.repository.find_by_code(code)
    
    def fetch_and_save_stocks(self) -> int:
        """从 API 获取并保存股票数据"""
        stocks = self._fetch_from_api()
        count = 0
        for stock in stocks:
            if stock.validate():
                self.repository.save(stock)
                count += 1
        return count
    
    def _fetch_from_api(self) -> List[Stock]:
        """从外部 API 获取数据（内部方法）"""
        df = ak.stock_hk_spot()
        stocks = []
        for _, row in df.iterrows():
            stock = Stock(
                code=str(row['code']),
                name=str(row['name']),
                price=float(row['price']) if 'price' in row else None,
                market_cap=float(row['market_cap']) if 'market_cap' in row else None,
                circulating_cap=float(row['circulating_cap']) if 'circulating_cap' in row else None,
                update_at=None
            )
            stocks.append(stock)
        return stocks
```

#### 4.4 重构 H 股视图层

将 `src/stocks/stocklist.py` 迁移到 `src/h_stock/view/`，并更新为调用服务层：

```bash
# 迁移视图层文件
cp src/stocks/stocklist.py src/h_stock/view/stock_list_view.py
```

重构视图类，改为调用服务层而不是仓储层：

```python
# src/h_stock/view/stock_list_view.py
import toga
from toga.style import Pack
from src.h_stock.services.stock_service import StockService
from src.h_stock.entities.stock import Stock

class StockListView(toga.Box):
    """H 股列表视图"""
    
    def __init__(self, service: StockService):
        self.service = service
        super().__init__(children=[self._create_ui()])
    
    def _create_ui(self) -> toga.Box:
        """创建 UI"""
        self.table = toga.Table(
            headings=["代码", "名称", "价格", "市值"],
            on_select=self._on_select,
            style=Pack(flex=1)
        )
        
        refresh_button = toga.Button(
            "刷新数据",
            on_press=self._refresh_data,
            style=Pack(padding=10)
        )
        
        return toga.Box(
            children=[self.table, refresh_button],
            style=Pack(direction=Column, flex=1)
        )
    
    def _refresh_data(self, widget):
        """刷新数据"""
        count = self.service.fetch_and_save_stocks()
        self._update_table()
    
    def _update_table(self):
        """更新表格数据"""
        stocks = self.service.get_all_stocks()
        data = [
            (stock.code, stock.name, stock.price or '-', stock.market_cap or '-')
            for stock in stocks
        ]
        self.table.data = data
    
    def _on_select(self, widget, row):
        """选择行时的回调"""
        if row:
            code = row[0]
            stock = self.service.get_stock_by_code(code)
            print(f"Selected stock: {stock.code} - {stock.name}")
```

### 第五阶段：更新主应用代码

#### 5.1 更新 app.py

更新主应用文件以使用新的模块结构和 DDD 分层：

```python
# 更新导入
from src.a_stock.services.stock_service import StockService
from src.h_stock.services.stock_service import HkStockService
from src.a_stock.repositories.stock_repository import StockRepository
from src.h_stock.repositories.stock_repository import HkStockRepository
from src.database.connection import DatabaseConnectionManager

# 在应用退出时关闭所有数据库连接
def on_exit(self):
    db_manager = DatabaseConnectionManager()
    db_manager.close_all()
```

#### 5.2 更新依赖注入

使用依赖注入的方式创建服务实例：

```python
# 创建仓储实例
a_stock_repo = StockRepository("finance.db")
h_stock_repo = HkStockRepository("finance.db")

# 创建服务实例
a_stock_service = StockService(a_stock_repo)
h_stock_service = HkStockService(h_stock_repo)

# 创建视图实例
a_stock_view = StockListView(a_stock_service)
h_stock_view = HkStockListView(h_stock_service)
```

### 第六阶段：测试驱动开发（TDD）实施

#### 6.1 TDD 开发流程

按照测试驱动开发的方法论进行开发：

1. **红（Red）**: 编写一个失败的测试用例
2. **绿（Green）: 编写最少量的代码使测试通过
3. **重构（Refactor）**: 重构代码，保持测试通过
4. **循环**: 重复上述步骤

#### 6.2 创建测试文件结构

```bash
# 创建测试目录结构
mkdir -p tests/test_database
mkdir -p tests/test_a_stock
mkdir -p tests/test_h_stock
mkdir -p tests/test_integration
mkdir -p tests/test_ui

# 创建测试文件
touch tests/test_database/test_connection.py
touch tests/test_database/test_base_repository.py
touch tests/test_a_stock/test_stock_repository.py
touch tests/test_a_stock/test_detail_repository.py
touch tests/test_h_stock/test_stock_repository.py
touch tests/test_h_stock/test_financial_repository.py
touch tests/test_integration/test_a_stock_workflow.py
touch tests/test_integration/test_h_stock_workflow.py
touch tests/test_ui/test_stock_list_view.py
```

#### 6.3 TDD 开发示例：数据库连接管理器

**步骤1：编写测试用例（红）**

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
    assert conn1 is conn2  # 应该是同一个连接

def test_close_connection():
    """测试关闭连接"""
    db_manager = DatabaseConnectionManager()
    conn = db_manager.get_connection(":memory:")
    db_manager.close_connection(":memory:")
    # 验证连接已关闭
```

**运行测试，预期失败：**

```bash
pytest tests/test_database/test_connection.py -v
# 结果: FAILED (DatabaseConnectionManager 未实现)
```

**步骤2：编写最少代码使测试通过（绿）**

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

**运行测试，预期通过：**

```bash
pytest tests/test_database/test_connection.py -v
# 结果: PASSED
```

**步骤3：重构代码（保持测试通过）**

```python
# 添加更多功能，如 close_all、get_cursor 等
# 确保所有测试仍然通过
```

#### 6.4 TDD 开发示例：A 股仓储类

**步骤1：编写测试用例**

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
```

**步骤2：实现功能**

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
```

**步骤3：运行测试并验证**

```bash
pytest tests/test_a_stock/test_stock_repository.py -v
# 结果: PASSED
```

#### 6.5 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_a_stock/ -v
pytest tests/test_h_stock/ -v

# 运行特定测试文件
pytest tests/test_database/test_connection.py -v

# 运行特定测试函数
pytest tests/test_database/test_connection.py::test_get_connection -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

#### 6.6 测试覆盖率要求

- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 60%
- **关键路径覆盖率**: 100%

#### 6.7 持续集成

- **每次提交前**: 运行所有测试，确保测试通过
- **合并请求前**: 运行完整测试套件，包括覆盖率检查
- **定期执行**: 运行性能测试和集成测试

#### 6.8 性能测试

测试数据库连接管理器的性能：

```python
# tests/test_performance/test_connection_performance.py
import time
from src.database.connection import DatabaseConnectionManager

def test_connection_reuse_performance():
    """测试连接复用性能"""
    db_manager = DatabaseConnectionManager()
    
    # 测试多次获取连接
    start = time.time()
    for i in range(1000):
        conn = db_manager.get_connection(":memory:")
    end = time.time()
    
    elapsed = end - start
    print(f"1000 次获取连接耗时: {elapsed:.2f} 秒")
    
    # 验证性能（应该在0.1秒内完成）
    assert elapsed < 0.1
```

## 迁移验证

### 1. 功能验证

- [ ] A 股列表显示正常
- [ ] A 股详情显示正常
- [ ] H 股列表显示正常
- [ ] H 股详情显示正常
- [ ] 数据更新功能正常
- [ ] 数据查询功能正常

### 2. 性能验证

- [ ] 数据库连接复用正常
- [ ] 查询速度提升
- [ ] 内存使用合理
- [ ] 无内存泄漏

### 3. 代码质量验证

- [ ] 所有测试通过
- [ ] 代码符合 PEP 8 规范
- [ ] 无明显代码异味
- [ ] 文档完整

## 回滚计划

如果迁移出现问题，可以按以下步骤回滚：

```bash
# 停止应用
# 恢复备份的代码
cp -r backup/$(date +%Y%m%d)/src/* src/

# 恢复数据库
cp backup/$(date +%Y%m%d)/finance.db .

# 重启应用
briefcase dev
```

## 后续优化

### 1. 添加缓存机制

在数据层添加缓存，减少数据库查询：

```python
from functools import lru_cache

class StockRepository(BaseRepository):
    @lru_cache(maxsize=1000)
    def get_stock(self, code: str):
        # 实现缓存
        pass
```

### 2. 添加异步支持

使用异步数据库驱动提高性能：

```python
import aiosqlite

class AsyncBaseRepository:
    async def query_many(self, sql: str):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute(sql) as cursor:
                return await cursor.fetchall()
```

### 3. 添加日志和监控

添加详细的日志记录和性能监控：

```python
import time
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def query_many(self, sql: str):
        start = time.time()
        result = super().query_many(sql)
        elapsed = time.time() - start
        logger.info(f"Query executed in {elapsed:.2f}s: {sql[:100]}")
        return result
```

## 总结

本迁移指南详细描述了从现有架构迁移到新模块化架构的完整过程。按照本指南进行迁移，可以确保项目的平滑过渡，同时提高代码的可维护性和可扩展性。