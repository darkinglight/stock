# Stock Project Architecture

## 项目概述

这是一个基于 Python 的股票数据分析项目，使用 Toga 框架构建跨平台 GUI 应用，支持 A 股和 H 股的数据获取、分析和展示。

## 架构设计原则

### 1. 数据库连接管理
- **统一管理**: 所有数据库操作通过统一的数据库管理器进行
- **延迟创建**: 连接在首次使用时创建，避免不必要的资源占用
- **生命周期管理**: 连接在对象生命周期结束时自动断开
- **连接复用**: 尽量减少重连，提高查询性能
- **线程安全**: 支持多线程环境下的安全访问

### 2. 模块化设计
- **模块独立**: A 股、H 股等模块完全独立，互不影响
- **平行扩展**: 新增股票市场模块时，不影响现有模块
- **接口统一**: 各模块遵循统一的接口规范

### 3. 分层架构
- **数据层**: 负责数据访问、存储和业务逻辑
- **视图层**: 负责 UI 展示和用户交互
- **完全分离**: 数据层和视图层通过接口通信，不直接依赖

## 目录结构

```
stock/
├── doc/                           # 文档目录
│   ├── ARCHITECTURE.md            # 架构文档
│   ├── DATABASE.md                # 数据库设计文档
│   ├── MIGRATION.md              # 迁移指南
│   ├── QUICK_START.md            # 快速开始指南
│   ├── TDD.md                   # 测试驱动开发指南
│   └── INDEX.md                 # 文档索引
├── src/
│   ├── database/                  # 数据库管理
│   │   ├── __init__.py
│   │   ├── connection.py          # 数据库连接管理器
│   │   └── base_repository.py    # 基础仓储类
│   ├── a_stock/                  # A 股模块
│   │   ├── __init__.py
│   │   ├── entities/             # 实体层
│   │   │   ├── __init__.py
│   │   │   ├── stock.py      # 股票实体
│   │   │   ├── detail.py     # 详情实体
│   │   │   └── financial.py  # 财务实体
│   │   ├── repositories/         # 仓储层
│   │   │   ├── __init__.py
│   │   │   ├── stock_repository.py      # 股票数据仓储
│   │   │   ├── detail_repository.py     # 详情数据仓储
│   │   │   ├── financial_repository.py  # 财务数据仓储
│   │   │   └── indicator_repository.py  # 指标数据仓储
│   │   ├── services/            # 服务层
│   │   │   ├── __init__.py
│   │   │   ├── stock_service.py      # 股票业务逻辑
│   │   │   ├── detail_service.py     # 详情业务逻辑
│   │   │   └── financial_service.py  # 财务业务逻辑
│   │   └── view/               # 视图层
│   │       ├── __init__.py
│   │       ├── stock_list_view.py      # 股票列表视图
│   │       ├── detail_view.py          # 详情视图
│   │       └── financial_view.py       # 财务视图
│   ├── h_stock/                  # H 股模块
│   │   ├── __init__.py
│   │   ├── entities/             # 实体层
│   │   │   ├── __init__.py
│   │   │   ├── stock.py
│   │   │   └── financial.py
│   │   ├── repositories/         # 仓储层
│   │   │   ├── __init__.py
│   │   │   ├── stock_repository.py
│   │   │   ├── financial_repository.py
│   │   │   └── report_repository.py
│   │   ├── services/            # 服务层
│   │   │   ├── __init__.py
│   │   │   ├── stock_service.py
│   │   │   └── financial_service.py
│   │   └── view/               # 视图层
│   │       ├── __init__.py
│   │       ├── stock_list_view.py
│   │       └── financial_view.py
│   ├── us_stock/                 # 美股模块（示例扩展）
│   │   └── ...
│   ├── ui/                       # 主 UI 模块
│   │   ├── __init__.py
│   │   ├── app.py               # 主应用
│   │   └── components/          # 通用 UI 组件
│   │       ├── __init__.py
│   │       └── table.py
│   └── utils/                   # 工具模块
│       ├── __init__.py
│       ├── data_fetcher.py      # 数据获取工具
│       └── calculator.py        # 计算工具
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_database/
│   ├── test_a_stock/
│   │   ├── test_entities/
│   │   ├── test_repositories/
│   │   └── test_services/
│   └── test_h_stock/
│       ├── test_entities/
│       ├── test_repositories/
│       └── test_services/
├── pyproject.toml
└── README.MD
```

## 核心组件设计

### 1. 数据库连接管理器 (DatabaseConnectionManager)

**职责**:
- 统一管理所有数据库连接
- 实现连接池机制，减少重连开销
- 提供延迟创建和自动释放功能
- 确保线程安全

**接口设计**:
```python
class DatabaseConnectionManager:
    def get_connection(self, db_name: str) -> sqlite3.Connection
    def release_connection(self, db_name: str)
    def close_all(self)
```

### 2. 基础仓储类 (BaseRepository)

**职责**:
- 提供通用的数据库操作方法
- 封装 CRUD 操作
- 处理事务和异常
- 纯数据访问，不包含业务逻辑

**接口设计**:
```python
class BaseRepository:
    def __init__(self, db_name: str)
    def create_table(self, sql: str) -> bool
    def drop_table(self, table_name: str) -> bool
    def insert(self, sql: str, data: Union[tuple, list]) -> bool
    def update(self, sql: str, data: Union[tuple, list]) -> bool
    def delete(self, sql: str, params: tuple = None) -> bool
    def query_one(self, sql: str, params: tuple = None) -> Optional[tuple]
    def query_many(self, sql: str, params: tuple = None) -> List[tuple]
    def execute(self, sql: str, params: tuple = None) -> bool
    def table_exists(self, table_name: str) -> bool
```

### 3. 实体层 (Entity)

**职责**:
- 定义领域模型和数据结构
- 提供数据验证逻辑
- 封装业务规则
- 使用 dataclass 实现强类型

**设计原则**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """股票实体"""
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

### 3.1 Entity 操作方法

**BaseRepository 新增的 Entity 操作方法**：

```python
from src.database.entity import BaseEntity

# 保存单个 Entity
repository.save(stock_entity)

# 批量保存 Entity
repository.save_all([stock1, stock2, stock3])

# 更新 Entity
repository.update_entity(stock_entity)

# 批量更新 Entity
repository.update_all([stock1, stock2])

# 删除 Entity
repository.delete_entity(stock_entity)

# 根据主键查找 Entity
stock = repository.find_by_id(Stock, "600000")

# 查找所有 Entity
stocks = repository.find_all(Stock)

# 条件查找 Entity
stocks = repository.find_all(Stock, status=1)

# 检查 Entity 是否存在
exists = repository.exists(stock_entity)
```

**优势**：
- ✅ **类型安全**：直接操作 Entity 对象，编译时类型检查
- ✅ **代码简洁**：不需要手动处理 SQL 字段映射
- ✅ **易于维护**：字段变更只需修改 Entity 定义
- ✅ **自动验证**：Entity 可以包含验证逻辑
- ✅ **类似 ORM**：提供类似 ORM 的开发体验

### 4. 服务层 (Service)

**职责**:
- 实现业务逻辑
- 协调多个 Repository 和 Entity
- 调用外部 API（akshare、baostock）
- 数据转换和处理

**设计原则**:
```python
from typing import List, Optional

class StockService:
    """股票服务 - 业务逻辑层"""
    
    def __init__(self, repository: StockRepository):
        self.repository = repository
    
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
    
    def get_stock_detail(self, code: str) -> Optional[Stock]:
        """获取股票详情"""
        return self.repository.find_by_code(code)
    
    def _fetch_from_api(self) -> List[Stock]:
        """从外部 API 获取数据（内部方法）"""
        # 调用 akshare 或 baostock
        import akshare as ak
        df = ak.stock_zh_a_spot()
        return [Stock.from_dict(row) for _, row in df.iterrows()]
```

### 5. 模块仓储接口

**A 股模块仓储层**:
- `StockRepository`: A 股基础信息管理
- `DetailRepository`: A 股详情数据管理
- `FinancialRepository`: A 股财务数据管理
- `IndicatorRepository`: A 股指标数据管理

**A 股模块服务层**:
- `StockService`: A 股业务逻辑
- `DetailService`: A 股详情业务逻辑
- `FinancialService`: A 股财务业务逻辑

**H 股模块仓储层**:
- `StockRepository`: H 股基础信息管理
- `FinancialRepository`: H 股财务数据管理
- `ReportRepository`: H 股报告数据管理

**H 股模块服务层**:
- `StockService`: H 股业务逻辑
- `FinancialService`: H 股财务业务逻辑

### 4. 视图层设计

**原则**:
- 视图层只负责 UI 展示和用户交互
- 通过接口调用 Service 层获取数据
- 不包含任何业务逻辑
- 使用 Toga 框架组件构建

**接口设计**:
```python
class BaseView(toga.Box):
    def __init__(self, service: BaseService)
    def refresh_data(self)
    def get_selected_item(self)
```

## 分层架构说明

### 架构层次

本项目采用 DDD（领域驱动设计）的分层架构，从上到下分为：

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

### 各层职责

**1. View Layer (视图层)**:
- 负责 UI 展示和用户交互
- 调用 Service 层获取数据
- 不包含业务逻辑
- 使用 Toga 框架组件

**2. Service Layer (服务层)**:
- 实现业务逻辑
- 协调多个 Repository 和 Entity
- 调用外部 API（akshare、baostock）
- 数据转换和处理
- 不直接操作数据库

**3. Repository Layer (仓储层)**:
- 纯数据访问，不包含业务逻辑
- 封装数据库操作
- 继承自 BaseRepository
- 只负责 CRUD 操作

**4. Entity Layer (实体层)**:
- 定义领域模型和数据结构
- 提供数据验证逻辑
- 封装业务规则
- 使用 dataclass 实现强类型

**5. Database Layer (数据库层)**:
- 统一管理数据库连接
- 提供连接池机制
- 确保线程安全

### 依赖关系

```
View → Service → Repository → Database
  ↓         ↓           ↓
Entity    Entity    Entity
```

- View 依赖 Service
- Service 依赖 Repository 和 Entity
- Repository 依赖 Entity
- 所有层都依赖 Database

### 调用规则

**1. 向下调用**:
- View 调用 Service
- Service 调用 Repository
- Repository 调用 Database

**2. 不跨层调用**:
- View 不直接调用 Repository
- Service 不直接调用 Database
- Repository 不调用外部 API

**3. 数据流向**:
- 数据从下往上流：Database → Repository → Service → View
- 命令从上往下流：View → Service → Repository → Database

## 数据流设计

### 1. 数据获取流程

```
用户操作 → 视图层 → 服务层 → 仓储层 → 数据库
                ↓         ↓         ↓
            数据处理  Entity  Entity
                ↓
            视图更新
```

### 2. 数据更新流程

```
定时任务/用户触发 → 服务层 → 外部 API
                        ↓
                    数据处理和转换
                        ↓
                    创建 Entity 对象
                        ↓
                    仓储层 → 数据库
                        ↓
                    视图刷新
```

### 3. 典型业务流程示例

**查询股票列表**:
```
View → StockService.get_all_stocks()
       ↓
StockService → StockRepository.find_all()
       ↓
StockRepository → Database
       ↓
返回 List[Stock] → StockService → View
```

**更新股票数据**:
```
View → StockService.refresh_stocks()
       ↓
StockService → akshare API
       ↓
返回 DataFrame → 转换为 List[Stock]
       ↓
StockService → StockRepository.save_all(stocks)
       ↓
StockRepository → Database
       ↓
通知 View 刷新
```

## 数据库设计

### 表结构

**A 股相关表**:
- `a_stock`: A 股基础信息
- `a_detail`: A 股详情信息
- `a_financial`: A 股财务数据
- `a_indicator`: A 股指标数据

**H 股相关表**:
- `h_stock`: H 股基础信息
- `h_financial`: H 股财务数据
- `h_report`: H 股报告数据

### 数据库优化

- 使用索引提高查询性能
- 合理设计表结构，避免冗余
- 使用事务确保数据一致性
- 定期清理过期数据

## 扩展性设计

### 1. 新增市场模块

按照以下步骤新增市场模块：

1. 在 `src/` 下创建新模块目录
2. 创建 `data/`、`view/`、`models/` 子目录
3. 实现数据层仓储类
4. 实现视图层类
5. 在主应用中注册新模块

### 2. 新增数据源

1. 在 `src/utils/data_fetcher.py` 中添加新的数据获取方法
2. 在相应模块的仓储类中调用新方法
3. 确保数据格式统一

## 性能优化策略

### 1. 数据库层面
- 使用连接池减少连接创建开销
- 批量操作代替单条操作
- 合理使用索引
- 避免全表扫描

### 2. 应用层面
- 数据缓存机制
- 异步数据加载
- 分页查询
- 增量更新

### 3. UI 层面
- 虚拟滚动
- 懒加载
- 异步渲染

## 安全性考虑

### 1. 数据安全
- SQL 注入防护（使用参数化查询）
- 数据加密存储敏感信息
- 定期备份

### 2. API 安全
- 请求频率限制
- 错误处理和重试机制
- 数据验证

## 测试策略

### 测试驱动开发（TDD）

本项目采用测试驱动开发（TDD）方法论，确保代码质量和可维护性。

#### TDD 开发流程

1. **红（Red）**: 编写一个失败的测试用例
2. **绿（Green）: 编写最少量的代码使测试通过
3. **重构（Refactor）**: 重构代码，保持测试通过
4. **循环**: 重复上述步骤

#### TDD 实施原则

- **先写测试，后写代码**: 在编写任何功能代码之前，先编写测试用例
- **小步快跑**: 每次只实现一个小的功能，确保测试通过
- **持续重构**: 在保持测试通过的前提下，不断优化代码结构
- **测试覆盖**: 确保所有核心功能都有对应的测试用例

#### TDD 开发示例

```python
# 步骤1: 编写测试用例（红）
# tests/test_database.py
import pytest
from src.database.connection import DatabaseConnectionManager

def test_get_connection():
    """测试获取数据库连接"""
    db_manager = DatabaseConnectionManager()
    conn = db_manager.get_connection(":memory:")
    assert conn is not None
    assert conn.cursor() is not None

# 运行测试，预期失败
# pytest tests/test_database.py -v
# 结果: FAILED (函数未实现)

# 步骤2: 编写最少代码使测试通过（绿）
# src/database/connection.py
class DatabaseConnectionManager:
    def get_connection(self, db_name: str = "finance.db"):
        import sqlite3
        return sqlite3.connect(db_name)

# 运行测试，预期通过
# pytest tests/test_database.py -v
# 结果: PASSED

# 步骤3: 重构代码（保持测试通过）
# 添加单例模式、连接复用等功能
```

### 1. 单元测试

#### 测试数据层仓储类

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
```

#### 测试业务逻辑

```python
# tests/test_a_stock/test_stock_service.py
import pytest
from src.a_stock.data.stock_repository import StockRepository
from src.a_stock.service.stock_service import StockService

@pytest.fixture
def service():
    """创建测试用的服务实例"""
    return StockService(":memory:")

def test_calculate_pe(service):
    """测试计算市盈率"""
    result = service.calculate_pe(price=10.5, eps=2.0)
    assert result == 5.25

def test_filter_stocks_by_pe(service):
    """测试根据市盈率筛选股票"""
    service.init_data()
    stocks = service.filter_stocks_by_pe(min_pe=5.0, max_pe=10.0)
    assert len(stocks) > 0
    for stock in stocks:
        assert 5.0 <= stock.pe <= 10.0
```

#### 测试工具函数

```python
# tests/test_utils/test_calculator.py
import pytest
from src.utils.calculator import calculate_roe, calculate_debt_ratio

def test_calculate_roe():
    """测试计算净资产收益率"""
    result = calculate_roe(net_profit=100, total_equity=1000)
    assert result == 0.1  # 10%

def test_calculate_debt_ratio():
    """测试计算资产负债率"""
    result = calculate_debt_ratio(total_liabilities=600, total_assets=1000)
    assert result == 0.6  # 60%
```

### 2. 集成测试

#### 测试模块间交互

```python
# tests/test_integration/test_a_stock_workflow.py
import pytest
from src.a_stock.data.stock_repository import StockRepository
from src.a_stock.data.detail_repository import DetailRepository
from src.a_stock.service.stock_service import StockService

def test_stock_detail_workflow():
    """测试股票和详情的完整工作流"""
    # 创建仓储
    stock_repo = StockRepository(":memory:")
    detail_repo = DetailRepository(":memory:")
    
    # 初始化表
    stock_repo.init_table()
    detail_repo.init_table()
    
    # 添加股票
    stock_repo.add_stock("600000", "浦发银行", 10.5)
    
    # 添加详情
    detail_repo.add_detail("600000", pe=5.2, pb=0.8)
    
    # 验证数据
    stock = stock_repo.get_stock("600000")
    detail = detail_repo.get_detail("600000")
    
    assert stock.code == "600000"
    assert detail.pe == 5.2
```

#### 测试数据库操作

```python
# tests/test_integration/test_database_operations.py
import pytest
from src.database.connection import DatabaseConnectionManager

def test_database_connection_pool():
    """测试数据库连接池"""
    db_manager = DatabaseConnectionManager()
    
    # 获取多个连接
    conn1 = db_manager.get_connection(":memory:")
    conn2 = db_manager.get_connection(":memory:")
    
    # 验证连接复用
    assert conn1 is conn2
    
    # 清理
    db_manager.close_all()
```

#### 测试 API 集成

```python
# tests/test_integration/test_akshare_api.py
import pytest
import akshare as ak

def test_fetch_stock_list():
    """测试获取股票列表"""
    df = ak.stock_info_a_code_name()
    assert df is not None
    assert len(df) > 0
    assert 'code' in df.columns
    assert 'name' in df.columns
```

### 3. UI 测试

#### 测试用户交互

```python
# tests/test_ui/test_stock_list_view.py
import pytest
from src.a_stock.view.stock_list_view import StockListView
from src.a_stock.data.stock_repository import StockRepository

def test_view_initialization():
    """测试视图初始化"""
    repository = StockRepository(":memory:")
    repository.init_table()
    repository.add_stock("600000", "浦发银行", 10.5)
    
    view = StockListView(repository)
    assert view is not None
    assert view.table is not None
    assert len(view.table.data) == 1

def test_view_refresh():
    """测试视图刷新"""
    repository = StockRepository(":memory:")
    repository.init_table()
    
    view = StockListView(repository)
    view.refresh()
    
    assert len(view.table.data) == 1
```

#### 测试数据显示

```python
# tests/test_ui/test_data_display.py
import pytest
from src.a_stock.view.stock_list_view import StockListView
from src.a_stock.data.stock_repository import StockRepository

def test_data_display_format():
    """测试数据显示格式"""
    repository = StockRepository(":memory:")
    repository.init_table()
    repository.add_stock("600000", "浦发银行", 10.5)
    
    view = StockListView(repository)
    view.refresh()
    
    # 验证表头
    assert view.table.headings == ["代码", "名称", "价格", "市盈率"]
    
    # 验证数据格式
    row = view.table.data[0]
    assert row[0] == "600000"
    assert row[1] == "浦发银行"
    assert isinstance(row[2], float)
```

#### 测试响应性能

```python
# tests/test_ui/test_performance.py
import pytest
import time
from src.a_stock.view.stock_list_view import StockListView
from src.a_stock.data.stock_repository import StockRepository

def test_view_refresh_performance():
    """测试视图刷新性能"""
    repository = StockRepository(":memory:")
    repository.init_table()
    
    # 添加大量数据
    for i in range(1000):
        repository.add_stock(f"{i:06d}", f"股票{i}", 10.0 + i * 0.1)
    
    view = StockListView(repository)
    
    # 测量刷新时间
    start = time.time()
    view.refresh()
    elapsed = time.time() - start
    
    # 验证性能（应该在1秒内完成）
    assert elapsed < 1.0
    assert len(view.table.data) == 1000
```

### 4. 测试覆盖率要求

- **单元测试覆盖率**: ≥ 80%
- **集成测试覆盖率**: ≥ 60%
- **关键路径覆盖率**: 100%

### 5. 测试运行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_a_stock/ -v
pytest tests/test_h_stock/ -v

# 运行特定测试文件
pytest tests/test_database.py -v

# 运行特定测试函数
pytest tests/test_database.py::test_get_connection -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 6. 持续集成

- **每次提交前**: 运行所有测试，确保测试通过
- **合并请求前**: 运行完整测试套件，包括覆盖率检查
- **定期执行**: 运行性能测试和集成测试

## 部署和发布

### 1. 开发环境
- 使用 `briefcase dev` 进行本地开发
- 使用虚拟环境隔离依赖

### 2. 构建发布
- 使用 `briefcase package` 构建安装包
- 支持多平台（Windows、macOS、Linux）

## 迁移计划

### 从现有架构迁移到新架构

1. **第一阶段**: 创建新的目录结构
2. **第二阶段**: 重构数据库连接管理
3. **第三阶段**: 分离 A 股模块的数据层和视图层
4. **第四阶段**: 分离 H 股模块的数据层和视图层
5. **第五阶段**: 更新主应用代码
6. **第六阶段**: 测试和优化

## 技术栈

- **语言**: Python 3.12+
- **GUI 框架**: Toga
- **数据库**: SQLite
- **数据源**: AkShare、BaoStock
- **构建工具**: Briefcase
- **包管理**: uv

## 总结

本架构设计遵循模块化、分层、可扩展的原则，通过统一的数据库管理、清晰的模块划分和严格的分层设计，为项目的长期维护和扩展提供了坚实的基础。