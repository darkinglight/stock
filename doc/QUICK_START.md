# Quick Start Guide

## 快速开始

本指南帮助您快速理解和使用重构后的股票项目架构。

## 核心概念

### 1. 数据库连接管理

项目使用单例模式的 `DatabaseConnectionManager` 来管理所有数据库连接：

```python
from src.core.database.connection import DatabaseConnectionManager

# 获取连接管理器实例（单例）
db_manager = DatabaseConnectionManager()

# 获取数据库连接（延迟创建，自动复用）
conn = db_manager.get_connection("finance.db")

# 使用连接
cursor = conn.cursor()
cursor.execute("SELECT * FROM a_stock LIMIT 10")
results = cursor.fetchall()

# 应用退出时关闭所有连接
db_manager.close_all()
```

**优势**：
- ✅ 延迟创建连接，节省资源
- ✅ 连接复用，减少重连开销
- ✅ 线程安全，支持多线程
- ✅ 统一管理，避免连接泄漏

### 2. 基础仓储类

所有数据层类都继承自 `BaseRepository`，提供通用的数据库操作方法：

```python
from src.core.database.base_repository import BaseRepository

class MyRepository(BaseRepository):
    def __init__(self, db_name: str = "finance.db"):
        super().__init__(db_name)
    
    def create_my_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            value REAL
        )
        """
        return self.create_table(sql)
    
    def insert_data(self, name: str, value: float):
        sql = "INSERT INTO my_table (name, value) VALUES (?, ?)"
        return self.insert(sql, (name, value))
    
    def get_all_data(self):
        sql = "SELECT * FROM my_table"
        return self.query_many(sql)
```

**优势**：
- ✅ 统一的数据库操作接口
- ✅ 自动事务管理
- ✅ 异常处理和日志记录
- ✅ 代码复用，减少重复

### 3. 模块化设计

项目按股票市场模块化，每个模块独立且可平行扩展：

```
src/
├── database/         # 数据库管理
├── a_stock/          # A 股模块
│   ├── entities/         # 实体层
│   ├── repositories/     # 仓储层
│   ├── services/         # 服务层
│   └── view/            # 视图层
├── h_stock/          # H 股模块
│   ├── entities/
│   ├── repositories/
│   ├── services/
│   └── view/
└── us_stock/         # 美股模块（可扩展）
   ├── entities/
   ├── repositories/
   ├── services/
   └── view/
```

**优势**：
- ✅ 模块独立，互不影响
- ✅ 易于扩展新市场
- ✅ 便于维护和测试
- ✅ 代码组织清晰

### 4. 分层架构

采用 DDD（领域驱动设计）的分层架构，严格分离各层职责：

```
┌─────────────────────────────────────────┐
│         View Layer (视图层)          │  UI 展示和用户交互
├─────────────────────────────────────────┤
│      Service Layer (服务层)          │  业务逻辑和 API 调用
├─────────────────────────────────────────┤
│    Repository Layer (仓储层)        │  纯数据访问
├─────────────────────────────────────────┤
│      Entity Layer (实体层)           │  数据模型和验证
├─────────────────────────────────────────┤
│   Database Layer (数据库层)          │  数据持久化
└─────────────────────────────────────────┘
```

**各层职责**：

**1. Entity Layer (实体层)**:
- 定义领域模型和数据结构
- 提供数据验证逻辑
- 使用 dataclass 实现强类型

**2. Repository Layer (仓储层)**:
- 纯数据访问，不包含业务逻辑
- 封装数据库操作
- 继承自 BaseRepository

**3. Service Layer (服务层)**:
- 实现业务逻辑
- 协调多个 Repository 和 Entity
- 调用外部 API（akshare、baostock）

**4. View Layer (视图层)**:
- 负责 UI 展示和用户交互
- 调用 Service 层获取数据
- 不包含业务逻辑

**5. Database Layer (数据库层)**:
- 统一管理数据库连接
- 提供连接池机制

## 快速示例

### 示例 1：创建 Entity、Repository、Service、View

#### 步骤 1：创建实体层（Entity）

```python
# src/a_stock/entities/stock.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """A 股实体"""
    code: str
    name: str
    price: float
    pe: Optional[float] = None
    pb: Optional[float] = None
    
    def validate(self) -> bool:
        """验证实体数据"""
        if not self.code or not self.name:
            return False
        if self.price <= 0:
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Stock':
        """从字典创建实体"""
        return cls(
            code=data.get('code', ''),
            name=data.get('name', ''),
            price=float(data.get('price', 0)),
            pe=float(data.get('pe')) if data.get('pe') else None,
            pb=float(data.get('pb')) if data.get('pb') else None
        )
```

#### 步骤 2：创建仓储层（Repository）

```python
# src/a_stock/repositories/stock_repository.py
from src.database.base_repository import BaseRepository
from src.a_stock.entities.stock import Stock

class StockRepository(BaseRepository):
    """
    A 股数据仓储 - 纯数据访问
    """
    
    def init_table(self):
        """初始化数据表"""
        sql = """
        CREATE TABLE IF NOT EXISTS a_stock (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL,
            pe REAL,
            pb REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        return self.create_table(sql)
    
    def save(self, stock: Stock) -> bool:
        """保存股票实体"""
        sql = """
        INSERT INTO a_stock (code, name, price, pe, pb)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            name=excluded.name,
            price=excluded.price,
            pe=excluded.pe,
            pb=excluded.pb
        """
        return self.insert(sql, (
            stock.code, stock.name, stock.price, stock.pe, stock.pb
        ))
    
    def find_by_code(self, code: str) -> Optional[Stock]:
        """根据代码查询股票"""
        sql = "SELECT * FROM a_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return Stock(*result)
        return None
    
    def find_all(self) -> list[Stock]:
        """查询所有股票"""
        sql = "SELECT * FROM a_stock"
        results = self.query_many(sql)
        return [Stock(*row) for row in results]
```

#### 步骤 3：创建服务层（Service）

```python
# src/a_stock/services/stock_service.py
from typing import List, Optional
from src.a_stock.repositories.stock_repository import StockRepository
from src.a_stock.entities.stock import Stock
import akshare as ak

class StockService:
    """
    A 股服务 - 业务逻辑层
    """
    
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
    
    def filter_by_pe(self, min_pe: float, max_pe: float) -> List[Stock]:
        """根据市盈率筛选股票"""
        all_stocks = self.repository.find_all()
        return [s for s in all_stocks if s.pe and min_pe <= s.pe <= max_pe]
    
    def _fetch_from_api(self) -> List[Stock]:
        """从外部 API 获取数据（内部方法）"""
        df = ak.stock_zh_a_spot()
        stocks = []
        for _, row in df.iterrows():
            stock = Stock.from_dict({
                'code': str(row['code']),
                'name': str(row['name']),
                'price': float(row.get('price', 0)),
                'pe': None,
                'pb': None
            })
            stocks.append(stock)
        return stocks
```

#### 步骤 4：创建视图层（View）

```python
# src/a_stock/view/stock_list_view.py
import toga
from toga.style import Pack
from src.a_stock.services.stock_service import StockService
from src.a_stock.entities.stock import Stock

class StockListView(toga.Box):
    """
    A 股列表视图
    """
    
    def __init__(self, service: StockService):
        self.service = service
        super().__init__(children=[self._create_ui()])
    
    def _create_ui(self) -> toga.Box:
        """创建 UI"""
        self.table = toga.Table(
            headings=["代码", "名称", "价格", "市盈率", "市净率"],
            on_select=self._on_select,
            style=Pack(flex=1)
        )
        
        refresh_button = toga.Button(
            "刷新数据",
            on_press=self._refresh_data,
            style=Pack(padding=10)
        )
        
        filter_button = toga.Button(
            "筛选 PE < 10",
            on_press=self._filter_stocks,
            style=Pack(padding=10)
        )
        
        return toga.Box(
            children=[self.table, refresh_button, filter_button],
            style=Pack(direction=Column, flex=1)
        )
    
    def _refresh_data(self, widget):
        """刷新数据"""
        count = self.service.fetch_and_save_stocks()
        print(f"成功获取并保存了 {count} 只股票")
        self._update_table()
    
    def _filter_stocks(self, widget):
        """筛选股票"""
        filtered_stocks = self.service.filter_by_pe(0, 10)
        self._update_table(filtered_stocks)
    
    def _update_table(self, stocks: List[Stock] = None):
        """更新表格数据"""
        if stocks is None:
            stocks = self.service.get_all_stocks()
        
        data = [
            (stock.code, stock.name, stock.price, stock.pe or '-', stock.pb or '-')
            for stock in stocks
        ]
        self.table.data = data
    
    def _on_select(self, widget, row):
        """选择行时的回调"""
        if row:
            code = row[0]
            stock = self.service.get_stock_by_code(code)
            if stock:
                print(f"Selected stock: {stock.code} - {stock.name}")
```

#### 步骤 5：在主应用中使用

```python
# src/ui/app.py
import toga
from src.a_stock.repositories.stock_repository import StockRepository
from src.a_stock.services.stock_service import StockService
from src.a_stock.view.stock_list_view import StockListView
from src.database.connection import DatabaseConnectionManager

class StockApp(toga.App):
    """
    股票应用主类
    """
    
    def __init__(self):
        super().__init__(
            formal_name="Stock Analysis",
            app_id="com.example.stocks"
        )
        
        # 获取数据库路径
        self.db_path = str(self.paths.data / "finance.db")
        
        # 创建仓储实例
        stock_repo = StockRepository(self.db_path)
        stock_repo.init_table()
        
        # 创建服务实例
        stock_service = StockService(stock_repo)
        
        # 创建视图实例
        self.stock_view = StockListView(stock_service)
        
        # 创建主窗口
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.stock_view
    
    def on_exit(self):
        """应用退出时的清理"""
        # 关闭所有数据库连接
        db_manager = DatabaseConnectionManager()
        db_manager.close_all()
        return True

def main():
    return StockApp()
```
        sql = "SELECT code, name, price, pe FROM custom_stock WHERE code = ?"
        result = self.query_one(sql, (code,))
        if result:
            return CustomStock(*result)
        return None
    
    def get_all_stocks(self) -> List[CustomStock]:
        """获取所有股票"""
        sql = "SELECT code, name, price, pe FROM custom_stock"
        results = self.query_many(sql)
        return [CustomStock(*row) for row in results]
    
    def delete_stock(self, code: str) -> bool:
        """删除股票"""
        sql = "DELETE FROM custom_stock WHERE code = ?"
        return self.delete(sql)
```

### 示例 2：创建新的视图

```python
# src/a_stock/view/custom_view.py
import toga
from toga.style import Pack
from typing import Callable
from ..data.custom_repository import CustomStockRepository, CustomStock

class CustomStockView(toga.Box):
    """
    自定义股票视图
    """
    
    def __init__(self, db_path: str, on_select: Callable = None):
        self.repository = CustomStockRepository(db_path)
        self.on_select = on_select
        super().__init__(children=[self._create_ui()])
    
    def _create_ui(self) -> toga.Box:
        """创建 UI"""
        # 创建表格
        self.table = toga.Table(
            headings=["代码", "名称", "价格", "市盈率"],
            on_select=self._on_select,
            style=Pack(flex=1)
        )
        
        # 创建按钮
        refresh_button = toga.Button(
            "刷新数据",
            on_press=self._refresh_data,
            style=Pack(padding=10)
        )
        
        # 创建容器
        return toga.Box(
            children=[self.table, refresh_button],
            style=Pack(direction=Column, flex=1)
        )
    
    def _refresh_data(self, widget):
        """刷新数据"""
        stocks = self.repository.get_all_stocks()
        data = [
            (stock.code, stock.name, stock.price, stock.pe)
            for stock in stocks
        ]
        self.table.data = data
    
    def _on_select(self, widget, row):
        """选择行时的回调"""
        if self.on_select and row:
            code = row[0]
            stock = self.repository.get_stock(code)
            self.on_select(stock)
    
    def refresh(self):
        """刷新视图"""
        self._refresh_data(None)
```

### 示例 3：在主应用中使用

```python
# src/ui/app.py
import toga
from toga.style import Pack
from src.database.connection import DatabaseConnectionManager
from src.a_stock.view.custom_view import CustomStockView

class StockApp(toga.App):
    """
    股票应用主类
    """
    
    def __init__(self):
        super().__init__(
            formal_name="Stock Analysis",
            app_id="com.example.stocks"
        )
        
        # 获取数据库路径
        self.db_path = self.paths.data / "finance.db"
        
        # 创建主窗口
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # 创建自定义视图
        self.custom_view = CustomStockView(
            str(self.db_path),
            on_select=self._on_stock_selected
        )
        
        # 设置主窗口内容
        self.main_window.content = self.custom_view
        
        # 初始化数据
        self._init_data()
    
    def _init_data(self):
        """初始化数据"""
        repository = CustomStockRepository(str(self.db_path))
        repository.init_table()
        
        # 添加示例数据
        repository.add_stock("600000", "浦发银行", 10.5, 5.2)
        repository.add_stock("000001", "平安银行", 12.3, 6.1)
        repository.add_stock("600036", "招商银行", 35.6, 8.3)
        
        # 刷新视图
        self.custom_view.refresh()
    
    def _on_stock_selected(self, stock):
        """股票选择回调"""
        print(f"Selected stock: {stock.code} - {stock.name}")
    
    def on_exit(self):
        """应用退出时的清理"""
        # 关闭所有数据库连接
        db_manager = DatabaseConnectionManager()
        db_manager.close_all()
        return True

def main():
    return StockApp()
```

## 常见任务

### 任务 1：添加新的股票市场模块

1. 创建模块目录结构
2. 实现数据层仓储类
3. 实现视图层类
4. 在主应用中注册

```bash
# 1. 创建目录
mkdir -p src/us_stock/{data,view,models}

# 2. 创建文件
touch src/us_stock/data/stock_repository.py
touch src/us_stock/view/stock_list_view.py

# 3. 实现功能（参考现有模块）

# 4. 在主应用中导入和使用
from src.us_stock.view.stock_list_view import UsStockListView
```

### 任务 2：优化数据库查询

```python
class StockRepository(BaseRepository):
    def get_stocks_by_criteria(self, min_pe: float, max_pe: float):
        """根据条件查询股票"""
        sql = """
        SELECT code, name, price, pe 
        FROM a_stock 
        WHERE pe BETWEEN ? AND ?
        ORDER BY pe ASC
        LIMIT 100
        """
        return self.query_many(sql, (min_pe, max_pe))
```

### 任务 3：添加数据缓存

```python
from functools import lru_cache
import time

class StockRepository(BaseRepository):
    @lru_cache(maxsize=1000)
    def get_stock(self, code: str):
        """带缓存的股票查询"""
        sql = "SELECT * FROM a_stock WHERE code = ?"
        return self.query_one(sql, (code,))
    
    def clear_cache(self):
        """清除缓存"""
        self.get_stock.cache_clear()
```

## 性能优化建议

### 1. 批量操作

```python
# 不好的做法 - 单条插入
for stock in stocks:
    repository.insert_stock(stock.code, stock.name, stock.price)

# 好的做法 - 批量插入
data = [(stock.code, stock.name, stock.price) for stock in stocks]
repository.insert_many(data)
```

### 2. 使用索引

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_a_stock_pe ON a_stock(pe);
CREATE INDEX idx_a_stock_code_name ON a_stock(code, name);
```

### 3. 连接复用

```python
# 好的做法 - 复用连接管理器
db_manager = DatabaseConnectionManager()
conn = db_manager.get_connection()

# 多次使用同一个连接
cursor1 = conn.cursor()
cursor1.execute("SELECT * FROM a_stock")

cursor2 = conn.cursor()
cursor2.execute("SELECT * FROM h_stock")

# 不需要手动关闭连接，应用退出时统一关闭
```

## 测试建议

### 1. 单元测试

```python
# tests/test_a_stock/test_stock_repository.py
import pytest
from src.modules.a_stock.data.stock_repository import StockRepository

def test_get_stock():
    repository = StockRepository(":memory:")
    repository.init_table()
    
    repository.add_stock("600000", "浦发银行", 10.5)
    stock = repository.get_stock("600000")
    
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5
```

### 2. 集成测试

```python
# tests/test_integration.py
def test_full_workflow():
    db_manager = DatabaseConnectionManager()
    
    # 测试完整的数据流程
    repository = StockRepository(":memory:")
    repository.init_table()
    
    # 添加数据
    repository.add_stock("600000", "浦发银行", 10.5)
    
    # 查询数据
    stock = repository.get_stock("600000")
    assert stock is not None
    
    # 清理
    db_manager.close_all()
```

## 调试技巧

### 1. 启用详细日志

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. 查看数据库连接状态

```python
db_manager = DatabaseConnectionManager()
print(f"Active connections: {len(db_manager._connections)}")
print(f"Connection details: {db_manager._connections}")
```

### 3. 分析 SQL 查询性能

```python
import time

start = time.time()
results = repository.query_many("SELECT * FROM a_stock")
elapsed = time.time() - start

print(f"Query executed in {elapsed:.2f}s")
print(f"Returned {len(results)} rows")
```

## 下一步

1. 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解完整的架构设计
2. 阅读 [DATABASE.md](DATABASE.md) 了解数据库设计
3. 阅读 [MIGRATION.md](MIGRATION.md) 了解如何迁移现有代码
4. 查看 `tests/` 目录中的测试用例
5. **采用 TDD 方法论开发新功能**
6. 开始实现您的功能！

## 测试驱动开发（TDD）实践

### TDD 开发流程

本项目采用测试驱动开发（TDD）方法论，确保代码质量和可维护性。

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

class StockRepository(BaseRepository):
    def add_stock(self, code: str, name: str, price: float) -> bool:
        """添加股票"""
        sql = "INSERT INTO a_stock (code, name, price) VALUES (?, ?, ?)"
        return self.insert(sql, (code, name, price))
```

运行测试，预期通过：
```bash
pytest tests/test_a_stock/test_stock_repository.py::test_add_stock -v
# 结果: PASSED
```

#### 3. 重构（Refactor）- 优化代码

```python
# 添加更多功能，如参数验证、错误处理等
# 确保所有测试仍然通过
```

### TDD 最佳实践

#### 1. 小步快跑

每次只实现一个小的功能，确保测试通过：

```python
# 好的做法 - 小步快跑
def test_add_stock():
    """测试添加股票"""
    # 测试基本功能
    repository.add_stock("600000", "浦发银行", 10.5)
    assert repository.get_stock("600000") is not None

def test_add_duplicate_stock():
    """测试添加重复股票"""
    # 测试边界情况
    repository.add_stock("600000", "浦发银行", 10.5)
    result = repository.add_stock("600000", "浦发银行", 11.0)
    assert result is False  # 应该失败
```

#### 2. 测试驱动设计

通过测试用例驱动 API 设计：

```python
# 先写测试，定义期望的 API
def test_get_stocks_by_criteria():
    """测试根据条件查询股票"""
    stocks = repository.get_stocks_by_criteria(
        min_pe=5.0, 
        max_pe=10.0,
        min_roe=10.0
    )
    assert len(stocks) > 0
    for stock in stocks:
        assert 5.0 <= stock.pe <= 10.0
        assert stock.roe >= 10.0

# 然后实现 API
def get_stocks_by_criteria(self, min_pe, max_pe, min_roe):
    # 实现逻辑
    pass
```

#### 3. 持续重构

在保持测试通过的前提下，不断优化代码：

```python
# 重构前
def get_stock(self, code: str):
    sql = f"SELECT * FROM a_stock WHERE code = '{code}'"
    result = self.query_one(sql)
    return Stock(*result) if result else None

# 重构后 - 使用参数化查询
def get_stock(self, code: str):
    sql = "SELECT * FROM a_stock WHERE code = ?"
    result = self.query_one(sql, (code,))
    return Stock(*result) if result else None

# 确保测试仍然通过
```

### TDD 开发示例：完整的仓储类

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
# 运行所有测试
pytest tests/test_a_stock/test_stock_repository.py -v

# 预期结果：所有测试通过
# test_init_table PASSED
# test_add_stock PASSED
# test_get_stock_not_found PASSED
# test_get_all_stocks PASSED
# test_delete_stock PASSED
```

### 测试覆盖率要求

- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 60%
- **关键路径覆盖率**: 100%

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_a_stock/ -v
pytest tests/test_h_stock/ -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 持续集成

- **每次提交前**: 运行所有测试，确保测试通过
- **合并请求前**: 运行完整测试套件，包括覆盖率检查
- **定期执行**: 运行性能测试和集成测试

## 获取帮助

- 查看项目文档：`doc/` 目录
- 查看测试用例：`tests/` 目录
- 查看示例代码：`src/` 目录
- 提交 Issue：项目 GitHub 仓库

## 总结

本快速开始指南提供了新架构的核心概念和实用示例。通过遵循这些模式和最佳实践，您可以高效地开发和维护股票项目。