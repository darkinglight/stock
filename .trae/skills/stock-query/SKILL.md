---
name: "stock-query"
description: "查询A股股票信息，包括股票列表、历史行情、实时行情、财务数据、年报季报、业绩快报、板块数据等。当用户需要查询股票信息、获取股票数据、分析股票时调用。"
---

# A股股票信息查询

这个skill提供A股股票信息查询功能，基于akshare库获取各种股票数据。

## 功能列表

### 1. 股票列表查询

#### 1.1 获取沪深京A股股票列表
获取所有A股股票的代码和名称信息。

**函数**: `stock_info_a_code_name()`

**使用示例**:
```python
import akshare as ak

# 获取所有A股股票代码和名称
stock_info_a_code_name_df = ak.stock_info_a_code_name()
print(stock_info_a_code_name_df)
```

**返回数据**:
- code: 股票代码
- name: 股票名称

### 2. 实时行情数据

#### 2.1 沪深京A股实时行情 ⚠️
获取所有A股的实时行情数据（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_zh_a_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取所有A股实时行情
real_time_data = ak.stock_zh_a_spot_em()
print(real_time_data)

# 筛选特定股票（如贵州茅台）
gm_data = real_time_data[real_time_data['代码'] == '600519']
print(gm_data)
```

**返回数据**:
- 代码: 股票代码
- 名称: 股票名称
- 最新价: 最新价格
- 涨跌幅: 涨跌幅
- 涨跌额: 涨跌额
- 成交量: 成交量
- 成交额: 成交额
- 振幅: 振幅
- 最高: 最高价
- 最低: 最低价
- 今开: 今开
- 昨收: 昨收
- 换手率: 换手率
- 市盈率-动态: 动态市盈率
- 市净率: 市净率

---

### 3. 历史行情数据

#### 3.1 获取股票历史数据 ⚠️
获取指定股票的历史行情数据，支持日线、周线、月线等不同周期（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_zh_a_hist(symbol, period="daily", start_date="19900101", end_date="20251231", adjust="")`

**参数说明**:
- symbol: 股票代码（如 "600519"）
- period: 数据周期，可选 "daily"(日线)、"weekly"(周线)、"monthly"(月线)
- start_date: 起始日期，格式 "YYYYMMDD"
- end_date: 结束日期，格式 "YYYYMMDD"
- adjust: 复权类型，可选 ""(不复权)、"qfq"(前复权)、"hfq"(后复权)

**使用示例**:
```python
import akshare as ak

# 获取贵州茅台日线数据（不复权）
df = ak.stock_zh_a_hist(
    symbol="600519",  # 股票代码
    period="daily",   # 日线
    start_date="20240101",
    end_date="20241231",
    adjust=""         # 不复权
)
print(df)

# 获取前复权数据
df_qfq = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"      # 前复权
)
print(df_qfq)

# 获取后复权数据
df_hfq = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="hfq"      # 后复权
)
print(df_hfq)
```

**返回数据**:
- 日期: 交易日期
- 股票代码: 股票代码
- 开盘: 开盘价
- 收盘: 收盘价
- 最高: 最高价
- 最低: 最低价
- 成交量: 成交量（手）
- 成交额: 成交额（元）
- 振幅: 振幅（%）
- 涨跌幅: 涨跌幅（%）
- 涨跌额: 涨跌额（元）
- 换手率: 换手率（%）

---

### 4. 年报季报数据

#### 4.1 获取业绩快报
获取指定日期的业绩快报数据。

**函数**: `stock_yjkb_em(date="20200331")`

**参数说明**:
- date: 日期，格式 "YYYYMMDD"，可选 "XXXX0331"(一季报)、"XXXX0630"(半年报)、"XXXX0930"(三季报)、"XXXX1231"(年报)；从 20100331 开始

**使用示例**:
```python
import akshare as ak

# 获取2024年年报业绩快报
yjkb_df = ak.stock_yjkb_em(date="20241231")
print(yjkb_df)

# 获取2024年一季报业绩快报
yjkb_q1_df = ak.stock_yjkb_em(date="20240331")
print(yjkb_q1_df)

# 获取2024年半年报业绩快报
yjkb_h1_df = ak.stock_yjkb_em(date="20240630")
print(yjkb_h1_df)

# 获取2024年三季报业绩快报
yjkb_q3_df = ak.stock_yjkb_em(date="20240930")
print(yjkb_q3_df)
```

**返回数据**:
- 序号: 序号
- 股票代码: 股票代码
- 股票简称: 股票简称
- 每股收益: 每股收益
- 营业收入-营业收入: 营业收入
- 营业收入-去年同期: 去年同期营业收入
- 营业收入-同比增长: 营业收入同比增长
- 营业收入-季度环比增长: 营业收入季度环比增长
- 净利润-净利润: 净利润
- 净利润-去年同期: 去年同期净利润
- 净利润-同比增长: 净利润同比增长
- 净利润-季度环比增长: 净利润季度环比增长
- 每股净资产: 每股净资产
- 净资产收益率: 净资产收益率
- 所处行业: 所处行业
- 公告日期: 公告日期
- 市场板块: 市场板块
- 证券类型: 证券类型

---

#### 4.2 获取业绩报表
获取指定日期的业绩报表数据。

**函数**: `stock_yjbb_em(date="20220331")`

**参数说明**:
- date: 日期，格式 "YYYYMMDD"，可选 "XXXX0331"(一季报)、"XXXX0630"(半年报)、"XXXX0930"(三季报)、"XXXX1231"(年报)；从 20100331 开始

**使用示例**:
```python
import akshare as ak

# 获取2024年年报业绩报表
yjbb_df = ak.stock_yjbb_em(date="20241231")
print(yjbb_df)

# 获取2024年一季报业绩报表
yjbb_q1_df = ak.stock_yjbb_em(date="20240331")
print(yjbb_q1_df)
```

**返回数据**:
- 序号: 序号
- 股票代码: 股票代码
- 股票简称: 股票简称
- 每股收益: 每股收益（注意单位：元）
- 营业总收入-营业总收入: 营业总收入（注意单位：元）
- 营业总收入-同比增长: 营业总收入同比增长（注意单位：%）
- 营业总收入-季度环比增长: 营业总收入季度环比增长（注意单位：%）
- 净利润-净利润: 净利润（注意单位：元）
- 净利润-同比增长: 净利润同比增长（注意单位：%）
- 净利润-季度环比增长: 净利润季度环比增长（注意单位：%）
- 每股净资产: 每股净资产（注意单位：元）
- 净资产收益率: 净资产收益率（注意单位：%）
- 每股经营现金流量: 每股经营现金流量（注意单位：元）
- 销售毛利率: 销售毛利率（注意单位：%）
- 所处行业: 所处行业
- 最新公告日期: 最新公告日期

---



### 5. 财务数据

#### 5.1 获取财务指标（推荐）
获取股票的财务指标数据，包含EPS、BPS、ROE等关键估值指标。

**函数**: `stock_financial_analysis_indicator_em(symbol="600004.SH", indicator="按报告期")`

**参数说明**:
- symbol: 股票代码（需要加上交易所后缀，如 "600004.SH" 或 "000001.SZ"）
- indicator: 报告类型，可选 "按报告期"、"年度"

**使用示例**:
```python
import akshare as ak

# 获取股票财务指标
df = ak.stock_financial_analysis_indicator_em(symbol="600004.SH", indicator="按报告期")
print(df)

# 获取最新期的EPS、BPS、ROE
latest = df.iloc[0]
print(f"每股收益(EPS): {latest.get('EPSJB')}")
print(f"每股净资产(BPS): {latest.get('BPS')}")
print(f"净资产收益率(ROE): {latest.get('ROEJQ')}%")
```

**返回数据**:
- REPORT_DATE: 报告日期
- EPSJB: 基本每股收益
- BPS: 每股净资产
- ROEJQ: 净资产收益率（加权）
- ROEKCJQ: 净资产收益率（扣非/加权）
- TOTALOPERATEREVE: 营业总收入
- PARENTNETPROFIT: 归属母公司净利润
- NET_ASSETS: 净资产
- TOTAL_ASSETS: 总资产
- 等等（共140个财务指标）

---

#### 5.2 获取财务指标（新浪财经）
获取股票的财务指标数据。

**函数**: `stock_financial_analysis_indicator(symbol="000001", start_year="2020")`

**参数说明**:
- symbol: 股票代码
- start_year: 开始查询的年份

**使用示例**:
```python
import akshare as ak

# 获取平安银行财务指标
df = ak.stock_financial_analysis_indicator(symbol="000001", start_year="2020")
print(df)
```

**返回数据**:
- 日期: 报告日期
- 摊薄每股收益(元): 摊薄每股收益
- 加权每股收益(元): 加权每股收益
- 每股净资产_调整前(元): 每股净资产
- 每股经营性现金流(元): 每股经营性现金流
- 销售净利率(%): 销售净利率
- 销售毛利率(%): 销售毛利率
- 净资产收益率(%): 净资产收益率
- 资产负债率(%): 资产负债率
- 流动比率: 流动比率
- 速动比率: 速动比率
- 总资产(元): 总资产
- 等等（共86个财务指标）

---

#### 5.3 获取资产负债表
获取股票的资产负债表数据。

**函数**: `stock_balance_sheet_by_report_em(symbol="000001")`

**使用示例**:
```python
import akshare as ak

# 获取资产负债表
df = ak.stock_balance_sheet_by_report_em(symbol="000001")
print(df)
```

---

#### 5.4 获取利润表
获取股票的利润表数据。

**函数**: `stock_profit_sheet_by_report_em(symbol="000001")`

**使用示例**:
```python
import akshare as ak

# 获取利润表
df = ak.stock_profit_sheet_by_report_em(symbol="000001")
print(df)
```

---

#### 5.5 获取现金流量表
获取股票的现金流量表数据。

**函数**: `stock_cash_flow_sheet_by_report_em(symbol="000001")`

**使用示例**:
```python
import akshare as ak

# 获取现金流量表
df = ak.stock_cash_flow_sheet_by_report_em(symbol="000001")
print(df)
```

---

### 6. 个股信息查询

#### 6.1 获取个股基本信息 ⚠️
获取指定股票的基本信息（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_individual_info_em(symbol="000001")`

**参数说明**:
- symbol: 股票代码
- timeout: 超时时间（可选）

**使用示例**:
```python
import akshare as ak

# 获取个股信息
stock_info = ak.stock_individual_info_em(symbol="000001")
print(stock_info)
```

**返回数据**:
- 最新: 最新价
- 股票代码: 股票代码
- 股票简称: 股票简称
- 总股本: 总股本
- 流通股: 流通股
- 总市值: 总市值
- 流通市值: 流通市值
- 行业: 所属行业
- 上市时间: 上市时间

---

#### 6.2 获取个股实时行情（雪球）⚠️
获取指定股票的实时行情数据（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_individual_spot_xq(symbol="SH600000")`

**参数说明**:
- symbol: 证券代码，格式为 "SH600000"（沪市）或 "SZ000001"（深市）
- token: token参数（可选，默认不设置）
- timeout: 超时时间（可选）

**使用示例**:
```python
import akshare as ak

# 获取个股实时行情
stock_info = ak.stock_individual_spot_xq(symbol="SH600000")
print(stock_info)
```

**返回数据**:
- 代码: 股票代码
- 名称: 股票名称
- 现价: 最新价格
- 涨跌: 涨跌幅
- 涨幅: 涨幅百分比
- 昨收: 昨日收盘价
- 最高: 最高价
- 最低: 最低价
- 均价: 均价
- 成交量: 成交量
- 市盈率(动): 动态市盈率
- 52周最高: 52周最高价
- 52周最低: 52周最低价
- 今年以来涨幅: 今年以来涨幅
- 等等

**注意**: 
- 此接口来源于雪球网
- 接口可能不稳定，建议多次重试
- 需要完整的股票代码，包含交易所前缀（SH或SZ）

---


## 注意事项

1. **接口稳定性说明**：
   - ⚠️ **不稳定接口**：实时行情接口（2.1-2.5）、历史行情接口（3.1）、个股信息查询接口（6.1）经常出现连接错误，建议谨慎使用
   - ✅ **稳定接口**：股票列表查询（1.1-1.4）、财务指标接口（5.1-5.2）、业绩报表接口（4.2）、资产负债表/利润表/现金流量表接口（5.3-5.5）工作稳定
   - 建议优先使用稳定接口，对于不稳定接口可考虑多次重试或使用其他数据源

2. 部分数据接口可能需要较长时间下载，请耐心等待
3. 股票代码格式：
   - 沪市: 6位数字，如 600519
   - 深市: 6位数字，如 000001
   - 北市: 8位数字，如 430017
4. 日期格式统一为 "YYYYMMDD"，如 "20240101"
5. 实时行情数据来源于东方财富，可能有延迟且接口不稳定
6. 建议在非交易时间获取历史数据，避免网络拥堵
7. **历史行情数据接口不稳定**，如需获取最新股价，建议使用网络搜索或稳定的数据源
8. 财务数据可能存在延迟，最新数据需要等待财报发布
9. 年报季报数据：
   - 业绩快报接口从 20100331 开始
   - 业绩报表接口从 20100331 开始
   - 预约披露时间接口从 20081231 开始
   - 日期格式统一为 "YYYYMMDD"，如 "20241231" 表示2024年年报
   - 季报日期：0331(一季报)、0630(半年报)、0930(三季报)、1231(年报)
10. **财务指标接口注意事项**：
    - `stock_financial_analysis_indicator_em()` 接口需要加上交易所后缀
    - 沪市股票：股票代码 + ".SH"，如 "600004.SH"
    - 深市股票：股票代码 + ".SZ"，如 "000001.SZ"
    - 该接口返回140个财务指标，包含EPSJB（每股收益）、BPS（每股净资产）、ROEJQ（净资产收益率）等关键估值指标
    - indicator参数可选 "按报告期" 或 "年度"
    - 该接口工作稳定，推荐使用
11. **估值指标计算**：
    - 市盈率(PE) = 股价 / 每股收益(EPS)
    - 市净率(PB) = 股价 / 每股净资产(BPS)
    - 净资产收益率(ROE) = 净利润 / 净资产 × 100%


## 参考文档

- [AKShare官方文档](https://akshare.akfamily.xyz/data/stock/stock.html)
- [AKShare GitHub](https://github.com/akfamily/akshare)
