# Stock Project Architecture

## 项目概述

这是一个基于 Python 的股票数据分析项目，使用 Toga 框架构建跨平台 GUI 应用，支持 A 股和 H 股的数据获取、分析和展示。

## 架构设计原则

### 1. 数据库连接管理
- **统一管理**: 所有数据库操作通过统一的数据库管理器进行
- **延迟创建**: 连接在首次使用时创建，避免不必要的资源占用
- **线程独立**: 每个线程使用独立的数据库连接，避免线程冲突
- **自动释放**: 连接在适当的时候自动释放，避免资源泄漏

### 2. 模块化设计
- **功能模块化**: 按功能划分模块，提高代码可读性和可维护性
- **配置化管理**: 使用配置或参数化区分不同股票市场
- **接口统一**: 各模块遵循统一的接口规范

### 3. 分层架构
- **简化分层**: 采用三层架构，减少复杂度
- **职责明确**: 各层职责清晰，便于理解和维护
- **适度分离**: 数据层和视图层通过接口通信，不直接依赖

## 目录结构

```
stock/
├── doc/                           # 文档目录
│   ├── ARCHITECTURE.md            # 架构文档
│   └── QUICK_START.md            # 快速开始指南
├── src/
│   ├── database/                  # 数据库管理
│   │   ├── __init__.py
│   │   └── connection.py          # 数据库连接管理器
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   └── stock.py               # 股票数据模型
│   ├── services/                  # 业务逻辑
│   │   ├── __init__.py
│   │   └── stock_service.py       # 股票业务逻辑
│   ├── ui/                        # UI模块
│   │   ├── __init__.py
│   │   ├── app.py                 # 主应用
│   │   └── views/                 # 视图
│   │       ├── __init__.py
│   │       └── stock_view.py      # 股票视图
│   └── utils/                     # 工具模块
│       ├── __init__.py
│       ├── data_fetcher.py        # 数据获取工具
│       └── calculator.py          # 计算工具
├── tests/                         # 测试目录
│   ├── __init__.py
│   └── test_stock.py              # 股票功能测试
├── pyproject.toml
└── README.MD
```

## 核心组件设计

### 1. 数据库连接管理器 (DatabaseConnectionManager)

**职责**:
- 统一管理所有数据库连接
- 为每个线程创建独立连接，避免线程冲突
- 提供延迟创建和自动释放功能
- 确保线程安全

**接口设计**:
```python
class DatabaseConnectionManager:
    def get_connection(self, db_name: str) -> sqlite3.Connection
    def close_connection(self, db_name: str)
    def close_all()
    def get_cursor(self, db_name: str) -> sqlite3.Cursor
```

### 2. 数据模型 (Model)

**职责**:
- 定义数据结构和字段
- 提供数据验证逻辑
- 封装业务规则
- 使用 dataclass 实现强类型

**设计原则**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Stock:
    """股票模型"""
    code: str
    name: str
    price: float
    market: str  # 'a' for A股, 'h' for H股
    pe: Optional[float] = None
    pb: Optional[float] = None
    bonus_rate: Optional[float] = None
    
    def validate(self) -> bool:
        """验证模型数据"""
        if not self.code or not self.name:
            return False
        if self.price <= 0:
            return False
        return True
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Stock':
        """从字典创建模型"""
        return cls(
            code=data.get('code', ''),
            name=data.get('name', ''),
            price=float(data.get('price', 0)),
            market=data.get('market', 'a'),
            pe=float(data.get('pe')) if data.get('pe') else None,
            pb=float(data.get('pb')) if data.get('pb') else None,
            bonus_rate=float(data.get('bonus_rate')) if data.get('bonus_rate') else None
        )
```

### 3. 服务层 (Service)

**职责**:
- 实现业务逻辑
- 数据访问和处理
- 调用外部 API（akshare、baostock）
- 数据转换和验证

**设计原则**:
```python
from typing import List, Optional

class StockService:
    """股票服务 - 业务逻辑层"""
    
    def __init__(self, db_name: str = "finance.db"):
        self.db_name = db_name
    
    def fetch_and_save_stocks(self, market: str = 'a') -> int:
        """从 API 获取并保存股票数据"""
        stocks = self._fetch_from_api(market)
        count = 0
        for stock in stocks:
            if stock.validate():
                self._save_stock(stock)
                count += 1
        return count
    
    def filter_by_pe(self, min_pe: float, max_pe: float, market: str = 'a') -> List[Stock]:
        """根据市盈率筛选股票"""
        all_stocks = self._get_all_stocks(market)
        return [s for s in all_stocks if s.pe and min_pe <= s.pe <= max_pe]
    
    def get_stock_detail(self, code: str, market: str = 'a') -> Optional[Stock]:
        """获取股票详情"""
        return self._get_stock_by_code(code, market)
    
    def _fetch_from_api(self, market: str) -> List[Stock]:
        """从外部 API 获取数据"""
        import akshare as ak
        if market == 'a':
            df = ak.stock_zh_a_spot()
            return [Stock.from_dict({**row, 'market': 'a'}) for _, row in df.iterrows()]
        elif market == 'h':
            # H股数据获取逻辑
            pass
        return []
    
    def _save_stock(self, stock: Stock):
        """保存股票数据"""
        # 直接操作数据库
        pass
    
    def _get_all_stocks(self, market: str) -> List[Stock]:
        """获取所有股票"""
        # 直接操作数据库
        pass
    
    def _get_stock_by_code(self, code: str, market: str) -> Optional[Stock]:
        """根据代码获取股票"""
        # 直接操作数据库
        pass
```

### 4. 视图层设计

**原则**:
- 视图层只负责 UI 展示和用户交互
- 通过接口调用 Service 层获取数据
- 不包含任何业务逻辑
- 使用 Toga 框架组件构建

**接口设计**:
```python
class BaseView(toga.Box):
    def __init__(self, service: StockService)
    def refresh_data()
    def get_selected_item()
```

### 5. 核心算法设计

**企业内在年化增长率算法**:
- **公式**: 企业内在年化增长率 = roe * (1 - 分红率) + roe * 分红率 / pb
- **含义**: 计算企业通过留存收益和分红再投资的综合增长能力
- **应用场景**: 评估企业长期增长潜力，为投资决策提供参考

**ROE计算方法**:
- **周期**: 取最近4个季度的ROE总和
- **季度ROE计算**: 
  - 非第一季度: 当季财报ROE - 上季财报ROE
  - 第一季度: 当季财报ROE（因为没有上一季度数据）
- **年化ROE计算**: 季度ROE + 前三季的季度ROE总和
- **数据来源**: 企业季度财务报告

**资产负债率要求**:
- **定义**: 资产负债率 = 总负债 / 总资产 × 100%
- **阈值**: 一般要求资产负债率不超过 70%
- **应用场景**: 评估企业财务风险，作为投资决策的重要参考指标
- **数据来源**: 企业季度财务报告


## 分层架构说明

### 架构层次

本项目采用简化的三层架构：

```
┌─────────────────────────────────────────┐
│         View Layer (视图层)          │  UI 展示和用户交互
├─────────────────────────────────────────┤
│      Service Layer (服务层)          │  业务逻辑和数据访问
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
- 直接操作数据库
- 调用外部 API（akshare、baostock）
- 数据转换和处理

**3. Database Layer (数据库层)**:
- 统一管理数据库连接
- 为每个线程创建独立连接
- 确保线程安全

### 依赖关系

```
View → Service → Database
  ↓
Model
```

- View 依赖 Service
- Service 依赖 Database 和 Model
- 所有层都依赖 Database

## 数据流设计

### 1. 数据获取流程

```
用户操作 → 视图层 → 服务层 → 数据库
                ↓
            数据处理
                ↓
            视图更新
```

### 2. 数据更新流程

```
定时任务/用户触发 → 服务层 → 外部 API
                        ↓
                    数据处理和转换
                        ↓
                    创建 Model 对象
                        ↓
                    服务层 → 数据库
                        ↓
                    视图刷新
```

## 数据库设计

### 表结构

**股票表**:
- `stock`: 股票基础信息（包含 market 字段区分 A 股和 H 股）

### 数据库优化

- 使用索引提高查询性能
- 合理设计表结构，避免冗余
- 使用事务确保数据一致性

## 性能优化策略

### 1. 数据库层面
- 每个线程独立连接，避免线程冲突
- 合理使用索引
- 避免全表扫描

### 2. 应用层面
- 数据缓存机制
- 分页查询
- 增量更新

### 3. UI 层面
- 简单的数据加载和显示

## 安全性考虑

### 1. 数据安全
- SQL 注入防护（使用参数化查询）
- 定期备份

### 2. API 安全
- 错误处理和重试机制
- 数据验证

## 测试策略

### 简化测试策略

本项目采用简化的测试策略，确保核心功能正常运行。

### 测试类型

- **核心功能测试**: 测试主要业务逻辑
- **数据库操作测试**: 测试数据库连接和基本操作
- **API 集成测试**: 测试外部 API 调用

### 测试运行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_stock.py -v
```

## 部署和发布

### 1. 开发环境
- 使用 `briefcase dev` 进行本地开发
- 使用虚拟环境隔离依赖

### 2. 构建发布
- 使用 `briefcase package` 构建安装包
- 支持多平台（Windows、macOS、Linux）

## 技术栈

- **语言**: Python 3.12+
- **GUI 框架**: Toga
- **数据库**: SQLite
- **数据源**: AkShare、BaoStock
- **构建工具**: Briefcase
- **包管理**: uv

## 总结

本架构设计遵循简化、实用的原则，通过合理的分层、模块化设计和线程独立的数据库连接管理，为小型项目提供了清晰、易于维护的架构方案。同时，保留了必要的扩展性，为未来的功能扩展留下了空间。