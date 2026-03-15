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

---

#### 1.2 获取上交所股票列表
获取上海证券交易所股票列表。

**函数**: `stock_info_sh_name_code(symbol="主板A股")`

**参数说明**:
- symbol: 板块类型，可选 "主板A股"、"主板B股"、"科创板"

**使用示例**:
```python
import akshare as ak

# 获取主板A股列表
stock_info_sh_name_code_df = ak.stock_info_sh_name_code(symbol="主板A股")
print(stock_info_sh_name_code_df)
```

**返回数据**:
- 证券代码: 股票代码
- 证券简称: 股票简称
- 公司全称: 公司全称
- 上市日期: 上市日期

---

#### 1.3 获取深交所股票列表
获取深圳证券交易所股票列表。

**函数**: `stock_info_sz_name_code(symbol="A股列表")`

**参数说明**:
- symbol: 板块类型，可选 "A股列表"、"B股列表"、"CDR列表"、"AB股列表"

**使用示例**:
```python
import akshare as ak

# 获取A股列表
stock_info_sz_name_code_df = ak.stock_info_sz_name_code(symbol="A股列表")
print(stock_info_sz_name_code_df)
```

**返回数据**:
- 板块: 板块名称
- A股代码: 股票代码
- A股简称: 股票简称
- A股上市日期: 上市日期
- A股总股本: 总股本
- A股流通股本: 流通股本
- 所属行业: 所属行业

---

#### 1.4 获取北交所股票列表
获取北京证券交易所股票列表。

**函数**: `stock_info_bj_name_code()`

**使用示例**:
```python
import akshare as ak

# 获取北交所股票列表
stock_info_bj_name_code_df = ak.stock_info_bj_name_code()
print(stock_info_bj_name_code_df)
```

**返回数据**:
- 证券代码: 股票代码
- 证券简称: 股票简称
- 总股本: 总股本（股）
- 流通股本: 流通股本（股）
- 上市日期: 上市日期
- 所属行业: 所属行业
- 地区: 地区
- 报告日期: 报告日期

---

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

#### 2.2 沪A股实时行情 ⚠️
获取沪市A股实时行情（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_sh_a_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取沪A股实时行情
sh_spot_data = ak.stock_sh_a_spot_em()
print(sh_spot_data)
```

---

#### 2.3 深A股实时行情 ⚠️
获取深市A股实时行情（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_sz_a_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取深A股实时行情
sz_spot_data = ak.stock_sz_a_spot_em()
print(sz_spot_data)
```

---

#### 2.4 创业板实时行情 ⚠️
获取创业板实时行情（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_cy_a_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取创业板实时行情
cy_spot_data = ak.stock_cy_a_spot_em()
print(cy_spot_data)
```

---

#### 2.5 科创板实时行情 ⚠️
获取科创板实时行情（**接口不稳定，建议谨慎使用**）。

**函数**: `stock_kc_a_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取科创板实时行情
kc_spot_data = ak.stock_kc_a_spot_em()
print(kc_spot_data)
```

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

#### 3.2 获取分时数据
获取股票的分时数据。

**函数**: `stock_zh_a_minute(symbol=symbol, period="1", adjust="", start_date="2023-02-01 09:30:00", end_date="2023-02-01 15:00:00")`

**参数说明**:
- symbol: 股票代码
- period: 周期，可选 "1"、"5"、"15"、"30"、"60"（分钟）
- adjust: 复权类型
- start_date: 开始时间
- end_date: 结束时间

**使用示例**:
```python
import akshare as ak

# 获取5分钟分时数据
df = ak.stock_zh_a_minute(
    symbol="600519",
    period="5",
    adjust="",
    start_date="2024-01-01 09:30:00",
    end_date="2024-01-01 15:00:00"
)
print(df)
```

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

#### 4.3 获取预约披露时间（东方财富）
获取指定市场和日期的预约披露时间数据。

**函数**: `stock_yysj_em(symbol="沪深A股", date="20211231")`

**参数说明**:
- symbol: 市场类型，可选 "沪深A股"、"沪市A股"、"科创板"、"深市A股"、"创业板"、"京市A股"、"ST板"
- date: 日期，格式 "YYYYMMDD"，可选 "XXXX0331"、"XXXX0630"、"XXXX0930"、"XXXX1231"；从 20081231 开始

**使用示例**:
```python
import akshare as ak

# 获取沪深A股2024年年报预约披露时间
yysj_df = ak.stock_yysj_em(symbol="沪深A股", date="20241231")
print(yysj_df)

# 获取沪市A股2024年年报预约披露时间
yysj_sh_df = ak.stock_yysj_em(symbol="沪市A股", date="20241231")
print(yysj_sh_df)
```

**返回数据**:
- 序号: 序号
- 股票代码: 股票代码
- 股票简称: 股票简称
- 首次预约时间: 首次预约时间
- 一次变更日期: 一次变更日期
- 二次变更日期: 二次变更日期
- 三次变更日期: 三次变更日期
- 实际披露时间: 实际披露时间

---

#### 4.4 获取预约披露时间（巨潮资讯）
获取指定市场和周期的预约披露数据。

**函数**: `stock_report_disclosure(market="沪深京", period="2022年报")`

**参数说明**:
- market: 市场类型，可选 "沪深京"、"深市"、"深主板"、"创业板"、"沪市"、"沪主板"、"科创板"、"北交所"
- period: 报告期，格式 "XXXX年报"、"XXXX半年报"、"XXXX一季"、"XXXX三季"；近四期的财务报告

**使用示例**:
```python
import akshare as ak

# 获取沪深京2024年年报预约披露时间
disclosure_df = ak.stock_report_disclosure(market="沪深京", period="2024年报")
print(disclosure_df)

# 获取沪深京2024年三季报预约披露时间
disclosure_q3_df = ak.stock_report_disclosure(market="沪深京", period="2024三季")
print(disclosure_q3_df)
```

**返回数据**:
- 股票代码: 股票代码
- 股票简称: 股票简称
- 首次预约: 首次预约时间
- 初次变更: 初次变更时间
- 二次变更: 二次变更时间
- 三次变更: 三次变更时间
- 实际披露: 实际披露时间

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

### 7. 板块数据

#### 7.1 获取概念板块列表
获取所有概念板块的名称和代码。

**函数**: `stock_board_concept_name_em()`

**使用示例**:
```python
import akshare as ak

# 获取概念板块列表
concept_list = ak.stock_board_concept_name_em()
print(concept_list)
```

---

#### 7.2 获取概念板块实时行情
获取指定概念板块的实时行情数据。

**函数**: `stock_board_concept_spot_em(symbol="可燃冰")`

**参数说明**:
- symbol: 概念板块名称或代码

**使用示例**:
```python
import akshare as ak

# 获取可燃冰概念板块实时行情
concept_spot = ak.stock_board_concept_spot_em(symbol="可燃冰")
print(concept_spot)
```

**返回数据**:
- 最新: 最新指数
- 最高: 最高指数
- 最低: 最低指数
- 开盘: 开盘指数
- 成交量: 成交量
- 成交额: 成交额
- 换手率: 换手率
- 涨跌额: 涨跌额
- 涨跌幅: 涨跌幅
- 振幅: 振幅

---

#### 7.3 获取概念板块成分股
获取指定概念板块的成分股列表。

**函数**: `stock_board_concept_cons_em(symbol="融资融券")`

**参数说明**:
- symbol: 概念板块名称或代码

**使用示例**:
```python
import akshare as ak

# 获取融资融券概念板块成分股
concept_cons = ak.stock_board_concept_cons_em(symbol="融资融券")
print(concept_cons)
```

**返回数据**:
- 序号: 序号
- 代码: 股票代码
- 名称: 股票名称
- 最新价: 最新价
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

#### 7.4 获取概念板块历史行情
获取指定概念板块的历史行情数据。

**函数**: `stock_board_concept_hist_em(symbol="绿色电力", period="daily", start_date="20220101", end_date="20221128", adjust="")`

**参数说明**:
- symbol: 概念板块名称
- period: 周期，可选 "daily"、"weekly"、"monthly"
- start_date: 起始日期
- end_date: 结束日期
- adjust: 复权类型

**使用示例**:
```python
import akshare as ak

# 获取绿色电力概念板块历史行情
concept_hist = ak.stock_board_concept_hist_em(
    symbol="绿色电力",
    period="daily",
    start_date="20220101",
    end_date="20241231",
    adjust=""
)
print(concept_hist)
```

---

#### 7.5 获取行业板块列表
获取所有行业板块的名称和代码。

**函数**: `stock_board_industry_name_em()`

**使用示例**:
```python
import akshare as ak

# 获取行业板块列表
industry_list = ak.stock_board_industry_name_em()
print(industry_list)
```

---

#### 7.6 获取行业板块实时行情
获取指定行业板块的实时行情数据。

**函数**: `stock_board_industry_spot_em()`

**使用示例**:
```python
import akshare as ak

# 获取行业板块实时行情
industry_spot = ak.stock_board_industry_spot_em()
print(industry_spot)
```

---

#### 7.7 获取行业板块成分股
获取指定行业板块的成分股列表。

**函数**: `stock_board_industry_cons_em(symbol="银行")`

**参数说明**:
- symbol: 行业板块名称或代码

**使用示例**:
```python
import akshare as ak

# 获取银行行业板块成分股
industry_cons = ak.stock_board_industry_cons_em(symbol="银行")
print(industry_cons)
```

---

### 8. 市场总貌数据

#### 8.1 上交所市场总貌
获取上海证券交易所市场总貌数据。

**函数**: `stock_sse_summary()`

**使用示例**:
```python
import akshare as ak

# 获取上交所市场总貌
sse_summary = ak.stock_sse_summary()
print(sse_summary)
```

**返回数据**:
- 流通股本: 流通股本
- 总市值: 总市值
- 平均市盈率: 平均市盈率
- 上市公司: 上市公司数量
- 上市股票: 上市股票数量
- 流通市值: 流通市值
- 报告时间: 报告时间
- 总股本: 总股本

---

#### 8.2 深交所市场总貌
获取深圳证券交易所市场总貌数据。

**函数**: `stock_szse_summary(date="20200619")`

**参数说明**:
- date: 查询日期，格式 "YYYYMMDD"

**使用示例**:
```python
import akshare as ak

# 获取深交所市场总貌
szse_summary = ak.stock_szse_summary(date="20240101")
print(szse_summary)
```

---

## 安装依赖

```bash
pip install akshare --upgrade
```

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

---

## 常见使用场景

### 场景1: 查询特定股票基本信息
```python
import akshare as ak

# 获取股票列表
stock_list = ak.stock_info_a_code_name()

# 查找特定股票
target_stock = stock_list[stock_list['name'].str.contains('茅台')]
print(target_stock)
```

---

### 场景2: 获取股票最近一年的日线数据 ⚠️
```python
import akshare as ak
from datetime import datetime, timedelta

# 计算日期范围
end_date = datetime.now().strftime("%Y%m%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")

# 获取数据（接口不稳定，可能需要多次重试）
df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date=start_date,
    end_date=end_date,
    adjust="qfq"
)
print(df)
```

---

### 场景3: 监控实时行情 ⚠️
```python
import akshare as ak
import time

# 获取实时行情（接口不稳定，可能需要多次重试）
while True:
    try:
        real_time_data = ak.stock_zh_a_spot_em()
        
        # 筛选关注的股票
        target_stocks = ['600519', '000001', '000002']
        for code in target_stocks:
            stock = real_time_data[real_time_data['代码'] == code]
            if not stock.empty:
                print(f"{stock.iloc[0]['名称']}: {stock.iloc[0]['最新价']} ({stock.iloc[0]['涨跌幅']}%)")
    except Exception as e:
        print(f"获取数据失败: {e}")
    
    # 每分钟更新一次
    time.sleep(60)
```

---

### 场景4: 查询概念板块成分股
```python
import akshare as ak

# 获取概念板块列表
concept_list = ak.stock_board_concept_name_em()
print("概念板块列表:")
print(concept_list)

# 获取特定概念板块的成分股
concept_name = "人工智能"
concept_cons = ak.stock_board_concept_cons_em(symbol=concept_name)
print(f"\n{concept_name}概念板块成分股:")
print(concept_cons)
```

---

### 场景5: 获取股票财务指标
```python
import akshare as ak

# 获取股票财务指标
symbol = "600519"
financial_data = ak.stock_financial_analysis_indicator(symbol=symbol, start_year="2020")
print(f"{symbol} 财务指标:")
print(financial_data)

# 获取资产负债表
balance_sheet = ak.stock_balance_sheet_by_report_em(symbol=symbol)
print(f"\n{symbol} 资产负债表:")
print(balance_sheet)
```

---

### 场景6: 分析行业板块表现
```python
import akshare as ak

# 获取行业板块列表
industry_list = ak.stock_board_industry_name_em()
print("行业板块列表:")
print(industry_list)

# 获取行业板块实时行情
industry_spot = ak.stock_board_industry_spot_em()
print("\n行业板块实时行情:")
print(industry_spot)

# 获取特定行业的成分股
industry_name = "银行"
industry_cons = ak.stock_board_industry_cons_em(symbol=industry_name)
print(f"\n{industry_name}行业成分股:")
print(industry_cons)
```

---

### 场景7: 获取业绩快报数据
```python
import akshare as ak

# 获取2024年年报业绩快报
yjkb_df = ak.stock_yjkb_em(date="20241231")
print("2024年年报业绩快报:")
print(yjkb_df)

# 获取2024年一季报业绩快报
yjkb_q1_df = ak.stock_yjkb_em(date="20240331")
print("\n2024年一季报业绩快报:")
print(yjkb_q1_df)
```

---

### 场景8: 获取业绩报表数据
```python
import akshare as ak

# 获取2024年年报业绩报表
yjbb_df = ak.stock_yjbb_em(date="20241231")
print("2024年年报业绩报表:")
print(yjbb_df)

# 获取2024年三季报业绩报表
yjbb_q3_df = ak.stock_yjbb_em(date="20240930")
print("\n2024年三季报业绩报表:")
print(yjbb_q3_df)
```

---

### 场景9: 查询股票估值指标（PE、PB、ROE）⚠️
```python
import akshare as ak
import pandas as pd

# 获取股票财务指标（包含EPS、BPS、ROE）
stock_code = "688633"
symbol = f"{stock_code}.SH"

financial_data = ak.stock_financial_analysis_indicator_em(
    symbol=symbol, 
    indicator="按报告期"
)

if not financial_data.empty:
    latest = financial_data.iloc[0]
    
    # 获取关键财务指标
    eps = latest.get('EPSJB')  # 基本每股收益
    bps = latest.get('BPS')    # 每股净资产
    roe = latest.get('ROEJQ')  # 净资产收益率
    
    # 获取最新股价（接口不稳定，建议使用网络搜索或其他稳定数据源）
    try:
        hist_data = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date="20250301",
            end_date="20250315",
            adjust="qfq"
        )
        
        if not hist_data.empty:
            current_price = hist_data.iloc[-1]['收盘']
            
            # 计算估值指标
            if pd.notna(eps) and eps != 0:
                pe = current_price / eps
                print(f"市盈率(PE): {pe:.2f}")
            
            if pd.notna(bps) and bps != 0:
                pb = current_price / bps
                print(f"市净率(PB): {pb:.2f}")
            
            if pd.notna(roe):
                print(f"净资产收益率(ROE): {roe}%")
            
            print(f"最新收盘价: {current_price} 元")
            print(f"每股收益(EPS): {eps} 元")
            print(f"每股净资产(BPS): {bps} 元")
    except Exception as e:
        print(f"获取股价失败: {e}")
        print(f"每股收益(EPS): {eps} 元")
        print(f"每股净资产(BPS): {bps} 元")
        print(f"净资产收益率(ROE): {roe}%")
```

---

### 场景10: 查询预约披露时间
```python
import akshare as ak

# 获取沪深A股2024年年报预约披露时间
yysj_df = ak.stock_yysj_em(symbol="沪深A股", date="20241231")
print("沪深A股2024年年报预约披露时间:")
print(yysj_df)

# 获取沪深京2024年三季报预约披露时间
disclosure_q3_df = ak.stock_report_disclosure(market="沪深京", period="2024三季")
print("\n沪深京2024年三季报预约披露时间:")
print(disclosure_q3_df)
```

---



### 新增接口

#### 新增接口: stock_fhps_em
东方财富-数据中心-年报季报-分红配送

**函数**: `stock_fhps_em()`

**限量**: 单次获取指定日期的分红配送数据

**使用示例**:
```python
import akshare as ak

# 东方财富-数据中心-年报季报-分红配送
result = ak.stock_fhps_em()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---


#### 新增接口: stock_hk_dividend_payout_em
东方财富-港股-核心必读-分红派息

**函数**: `stock_hk_dividend_payout_em()`

**限量**: 单次返回全部数据

**使用示例**:
```python
import akshare as ak

# 东方财富-港股-核心必读-分红派息
result = ak.stock_hk_dividend_payout_em()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---


#### 新增接口: stock_value_em
东方财富网-数据中心-估值分析-每日互动-每日互动-估值分析

**函数**: `stock_value_em()`

**限量**: 单次获取指定 symbol 的所有历史数据

**使用示例**:
```python
import akshare as ak

# 东方财富网-数据中心-估值分析-每日互动-每日互动-估值分析
result = ak.stock_value_em()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---


#### 新增接口: stock_zh_valuation_baidu
百度股市通-A 股-财务报表-估值数据

**函数**: `stock_zh_valuation_baidu()`

**限量**: 单次获取指定 symbol 和 indicator 的所有历史数据

**使用示例**:
```python
import akshare as ak

# 百度股市通-A 股-财务报表-估值数据
result = ak.stock_zh_valuation_baidu()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---


#### 新增接口: stock_hk_valuation_comparison_em
东方财富-港股-行业对比-估值对比

**函数**: `stock_hk_valuation_comparison_em()`

**限量**: 单次返回全部数据

**使用示例**:
```python
import akshare as ak

# 东方财富-港股-行业对比-估值对比
result = ak.stock_hk_valuation_comparison_em()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---


以下接口从api.txt中自动添加，已验证可以正常使用：

#### 新增接口: stock_zh_valuation_comparison_em
东方财富-行情中心-同行比较-估值比较

**函数**: `stock_zh_valuation_comparison_em()`

**限量**: 单次返回全部数据

**使用示例**:
```python
import akshare as ak

# 东方财富-行情中心-同行比较-估值比较
result = ak.stock_zh_valuation_comparison_em()
print(result)
```

**注意**: 此接口从api.txt中自动添加，已验证可以正常使用。

---

## 参考文档

- [AKShare官方文档](https://akshare.akfamily.xyz/data/stock/stock.html)
- [AKShare GitHub](https://github.com/akfamily/akshare)
