# Database Design Document

## 数据库概述

本项目使用 SQLite 作为数据库管理系统，存储 A 股和 H 股的相关数据。数据库文件默认名为 `finance.db`。

## 数据库连接管理

### 连接管理器设计

**DatabaseConnectionManager** 负责统一管理所有数据库连接：

```python
class DatabaseConnectionManager:
    """
    数据库连接管理器
    - 每个线程独立连接
    - 延迟创建连接
    - 自动释放连接
    - 线程安全
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    # 使用threading.local()存储线程本地连接
                    cls._instance._local = threading.local()
        return cls._instance
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """获取数据库连接，如果不存在则创建"""
        connections = self._get_thread_connections()
        if db_name not in connections:
            conn = sqlite3.connect(db_name)
            conn.row_factory = sqlite3.Row
            connections[db_name] = conn
        return connections[db_name]
    
    def close_connection(self, db_name: str):
        """关闭指定数据库连接"""
        connections = self._get_thread_connections()
        if db_name in connections:
            connections[db_name].close()
            del connections[db_name]
    
    def close_all(self):
        """关闭所有数据库连接"""
        connections = self._get_thread_connections()
        for conn in connections.values():
            conn.close()
        connections.clear()
    
    def _get_thread_connections(self) -> dict:
        """获取当前线程的连接字典"""
        if not hasattr(self._local, 'connections'):
            self._local.connections = {}
        return self._local.connections
```

### 连接生命周期

1. **创建**: 首次请求时延迟创建，每个线程独立
2. **使用**: 通过连接管理器获取，线程内复用
3. **释放**: 线程结束时自动释放，或手动释放指定连接

## 数据表设计

### 股票表

存储所有股票的基础信息，使用 `market` 字段区分 A 股和 H 股。

```sql
CREATE TABLE IF NOT EXISTS stock (
    code TEXT PRIMARY KEY,           -- 股票代码
    name TEXT NOT NULL,              -- 股票名称
    market TEXT NOT NULL,            -- 市场类型 ('a' for A股, 'h' for H股)
    price REAL,                      -- 当前价格
    pe REAL,                         -- 市盈率
    pb REAL,                         -- 市净率
    bonus_rate REAL,                 -- 分红率
    market_cap REAL,                 -- 市值
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 财务数据表

存储股票的财务指标数据。

```sql
CREATE TABLE IF NOT EXISTS financial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,               -- 股票代码
    market TEXT NOT NULL,             -- 市场类型
    report_date TEXT NOT NULL,        -- 报告期
    revenue REAL,                     -- 营业收入
    net_profit REAL,                  -- 净利润
    total_assets REAL,                -- 总资产
    total_liabilities REAL,            -- 总负债
    roe REAL,                        -- 净资产收益率
    eps REAL,                        -- 每股收益
    bps REAL,                        -- 每股净资产
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code, market, report_date),
    FOREIGN KEY (code) REFERENCES stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_financial_code ON financial(code);
CREATE INDEX idx_financial_market ON financial(market);
CREATE INDEX idx_financial_date ON financial(report_date);
```

## 数据库优化策略

### 1. 索引优化

- 为常用查询字段创建索引
- 为外键字段创建索引
- 为复合查询创建复合索引

### 2. 查询优化

- 使用参数化查询，避免 SQL 注入
- 避免使用 SELECT *，只查询需要的字段
- 合理使用 LIMIT 和 OFFSET

### 3. 事务管理

- 批量操作使用事务
- 及时提交或回滚事务
- 避免长时间持有事务

### 4. 数据维护

- 定期清理过期数据
- 定期执行 VACUUM 优化数据库
- 定期备份数据库

## 数据备份与恢复

### 备份策略

1. **定期备份**: 每天自动备份数据库文件
2. **增量备份**: 只备份变更的数据
3. **云端备份**: 将备份文件上传到云存储

### 恢复策略

1. **完整恢复**: 从完整备份文件恢复
2. **时间点恢复**: 恢复到指定时间点的状态

## 安全性考虑

### 数据安全

- SQL 注入防护（使用参数化查询）
- 限制数据库文件访问权限
- 定期备份

### 数据验证

- 输入数据验证
- 数据完整性检查

## 总结

本数据库设计遵循简化、实用的原则，通过统一的表结构、合理的索引设计和线程独立的连接管理，为小型项目提供了高效、安全、可靠的数据存储解决方案。