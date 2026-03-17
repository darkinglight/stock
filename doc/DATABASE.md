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
    - 延迟创建连接
    - 连接复用，减少重连
    - 自动释放连接
    - 线程安全
    """
    
    _instance = None
    _connections = {}
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_connection(self, db_name: str = "finance.db") -> sqlite3.Connection:
        """获取数据库连接，如果不存在则创建"""
        if db_name not in self._connections:
            with self._lock:
                if db_name not in self._connections:
                    conn = sqlite3.connect(db_name, check_same_thread=False)
                    conn.row_factory = sqlite3.Row
                    self._connections[db_name] = conn
        return self._connections[db_name]
    
    def close_connection(self, db_name: str):
        """关闭指定数据库连接"""
        if db_name in self._connections:
            with self._lock:
                if db_name in self._connections:
                    self._connections[db_name].close()
                    del self._connections[db_name]
    
    def close_all(self):
        """关闭所有数据库连接"""
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()
```

### 连接生命周期

1. **创建**: 首次请求时延迟创建
2. **使用**: 通过连接管理器获取，支持复用
3. **释放**: 应用退出时统一释放，或手动释放指定连接

## 数据表设计

### A 股模块表

#### 1. a_stock (A 股基础信息表)

存储 A 股股票的基础信息。

```sql
CREATE TABLE IF NOT EXISTS a_stock (
    code TEXT PRIMARY KEY,           -- 股票代码 (如: 600000)
    name TEXT NOT NULL,              -- 股票名称
    market TEXT,                     -- 市场 (SH: 上海, SZ: 深圳)
    code_number TEXT,                -- 不带市场后缀的代码
    industry TEXT,                   -- 所属行业
    list_date TEXT,                   -- 上市日期
    status INTEGER DEFAULT 1,        -- 状态 (1: 正常, 0: 停牌)
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_a_stock_market ON a_stock(market);
CREATE INDEX idx_a_stock_industry ON a_stock(industry);
CREATE INDEX idx_a_stock_status ON a_stock(status);
```

#### 2. a_detail (A 股详情信息表)

存储 A 股的详细指标信息。

```sql
CREATE TABLE IF NOT EXISTS a_detail (
    code TEXT PRIMARY KEY,           -- 股票代码
    name TEXT,                       -- 股票名称
    price REAL,                      -- 当前价格
    pe REAL,                         -- 市盈率
    pb REAL,                         -- 市净率
    bonus_rate REAL,                  -- 分红率
    roe_ttm REAL,                    -- 滚动净资产收益率
    earning_growth REAL,             -- 净利润增长率
    debt_ratio REAL,                 -- 资产负债率
    earning_growth_rush INTEGER,     -- 增速是否上扬 (1: 是, 0: 否)
    market_cap REAL,                 -- 市值
    circulating_cap REAL,             -- 流通市值
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code) REFERENCES a_stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_a_detail_pe ON a_detail(pe);
CREATE INDEX idx_a_detail_pb ON a_detail(pb);
CREATE INDEX idx_a_detail_roe ON a_detail(roe_ttm);
CREATE INDEX idx_a_detail_bonus ON a_detail(bonus_rate);
```

#### 3. a_financial (A 股财务数据表)

存储 A 股的财务报表数据。

```sql
CREATE TABLE IF NOT EXISTS a_financial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,               -- 股票代码
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
    UNIQUE(code, report_date),
    FOREIGN KEY (code) REFERENCES a_stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_a_financial_code ON a_financial(code);
CREATE INDEX idx_a_financial_date ON a_financial(report_date);
CREATE INDEX idx_a_financial_code_date ON a_financial(code, report_date);
```

#### 4. a_indicator (A 股指标数据表)

存储 A 股的技术指标数据。

```sql
CREATE TABLE IF NOT EXISTS a_indicator (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,               -- 股票代码
    trade_date TEXT NOT NULL,         -- 交易日期
    ma5 REAL,                         -- 5日均线
    ma10 REAL,                        -- 10日均线
    ma20 REAL,                        -- 20日均线
    ma60 REAL,                        -- 60日均线
    volume REAL,                      -- 成交量
    turnover_rate REAL,                -- 换手率
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code, trade_date),
    FOREIGN KEY (code) REFERENCES a_stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_a_indicator_code ON a_indicator(code);
CREATE INDEX idx_a_indicator_date ON a_indicator(trade_date);
CREATE INDEX idx_a_indicator_code_date ON a_indicator(code, trade_date);
```

### H 股模块表

#### 1. h_stock (H 股基础信息表)

存储 H 股股票的基础信息。

```sql
CREATE TABLE IF NOT EXISTS h_stock (
    code TEXT PRIMARY KEY,           -- 股票代码 (如: 00700)
    name TEXT NOT NULL,              -- 股票名称
    price REAL,                      -- 当前价格
    market_cap REAL,                 -- 市值
    circulating_cap REAL,            -- 流通市值
    update_at TEXT,                  -- 更新时间
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_h_stock_price ON h_stock(price);
CREATE INDEX idx_h_stock_update ON h_stock(update_at);
```

#### 2. h_financial (H 股财务数据表)

存储 H 股的财务指标数据。

```sql
CREATE TABLE IF NOT EXISTS h_financial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,               -- 股票代码
    report_date TEXT NOT NULL,        -- 报告期
    EPS_TTM REAL,                     -- 滚动每股收益
    BPS REAL,                         -- 每股净资产
    ROE_YEARLY REAL,                  -- 年化净资产收益率
    DEBT_ASSET_RATIO REAL,            -- 资产负债率
    TOTAL_ASSETS REAL,                -- 总资产
    TOTAL_LIABILITIES REAL,           -- 总负债
    NET_PROFIT REAL,                  -- 净利润
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(code, report_date),
    FOREIGN KEY (code) REFERENCES h_stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_h_financial_code ON h_financial(code);
CREATE INDEX idx_h_financial_date ON h_financial(report_date);
CREATE INDEX idx_h_financial_code_date ON h_financial(code, report_date);
```

#### 3. h_report (H 股报告数据表)

存储 H 股的详细报告数据。

```sql
CREATE TABLE IF NOT EXISTS h_report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    SECUCODE TEXT,                   -- 带后缀股票代码
    SECURITY_CODE TEXT,               -- 不带后缀股票代码
    SECURITY_NAME_ABBR TEXT,          -- 股票名称
    ORG_CODE TEXT,                   -- 组织代码
    REPORT_DATE TEXT,                -- 报告期
    DATE_TYPE_CODE TEXT,             -- 数据类型
    FISCAL_YEAR TEXT,                -- 财年
    STD_ITEM_CODE TEXT,              -- 指标代码
    STD_ITEM_NAME TEXT,              -- 指标名称
    AMOUNT REAL,                     -- 金额
    START_DATE TEXT,                 -- 开始日期
    STD_REPORT_DATE TEXT,            -- 标准报告日期
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (SECURITY_CODE) REFERENCES h_stock(code) ON DELETE CASCADE
);

CREATE INDEX idx_h_report_code ON h_report(SECURITY_CODE);
CREATE INDEX idx_h_report_date ON h_report(REPORT_DATE);
CREATE INDEX idx_h_report_code_date ON h_report(SECURITY_CODE, REPORT_DATE);
CREATE INDEX idx_h_report_item ON h_report(STD_ITEM_CODE);
```

## 数据库优化策略

### 1. 索引优化

- 为常用查询字段创建索引
- 为外键字段创建索引
- 为复合查询创建复合索引
- 定期分析索引使用情况

### 2. 查询优化

- 使用参数化查询，避免 SQL 注入
- 使用 EXPLAIN QUERY PLAN 分析查询性能
- 避免使用 SELECT *，只查询需要的字段
- 合理使用 LIMIT 和 OFFSET

### 3. 事务管理

- 批量操作使用事务
- 设置合理的隔离级别
- 及时提交或回滚事务
- 避免长时间持有事务

### 4. 数据维护

- 定期清理过期数据
- 定期执行 VACUUM 优化数据库
- 定期执行 ANALYZE 更新统计信息
- 定期备份数据库

## 数据迁移策略

### 版本管理

使用数据库版本号管理表结构变更：

```sql
CREATE TABLE IF NOT EXISTS db_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO db_version (version, description) VALUES (1, 'Initial database schema');
```

### 迁移脚本

每次数据库结构变更都创建对应的迁移脚本：

```python
class Migration:
    def up(self):
        """升级数据库"""
        pass
    
    def down(self):
        """回滚数据库"""
        pass
```

## 数据备份与恢复

### 备份策略

1. **定期备份**: 每天自动备份数据库文件
2. **增量备份**: 只备份变更的数据
3. **云端备份**: 将备份文件上传到云存储

### 恢复策略

1. **完整恢复**: 从完整备份文件恢复
2. **时间点恢复**: 恢复到指定时间点的状态
3. **选择性恢复**: 只恢复指定的表或数据

## 性能监控

### 监控指标

- 查询执行时间
- 连接数量
- 数据库文件大小
- 缓存命中率

### 优化建议

- 监控慢查询并优化
- 合理设置缓存大小
- 定期分析数据库性能
- 根据使用情况调整数据库参数

## 安全性考虑

### 数据加密

- 敏感数据加密存储
- 使用安全的连接方式
- 定期更新加密密钥

### 访问控制

- 限制数据库文件访问权限
- 使用只读模式进行查询
- 记录数据库操作日志

### 数据验证

- 输入数据验证
- 防止 SQL 注入
- 数据完整性检查

## 总结

本数据库设计遵循规范化原则，通过合理的表结构设计、索引优化和连接管理，为项目提供了高效、安全、可靠的数据存储解决方案。