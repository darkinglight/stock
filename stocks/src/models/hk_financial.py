from dataclasses import dataclass
from typing import Optional


@dataclass
class HkFinancial:
    """港股财务数据模型"""
    secucode: str  # 带后缀股票代码
    security_code: str  # 不带后缀股票代码
    security_name_abbr: Optional[str] = None  # 股票名称
    org_code: Optional[str] = None  # 组织代码
    report_date: Optional[str] = None  # 报告期
    date_type_code: Optional[str] = None  # 数据类型
    per_netcash_operate: Optional[float] = None  # 每股经营现金流(元)
    per_oi: Optional[float] = None  # 每股营业收入(元)
    bps: Optional[float] = None  # 每股净资产(元)
    basic_eps: Optional[float] = None  # 基本每股收益(元)
    diluted_eps: Optional[float] = None  # 稀释每股收益(元)
    operate_income: Optional[float] = None  # 营业总收入(元)
    operate_income_yoy: Optional[float] = None  # 营业总收入同比增长(%)
    gross_profit: Optional[float] = None  # 毛利润(元)
    gross_profit_yoy: Optional[float] = None  # 毛利润同比增长(%)
    holder_profit: Optional[float] = None  # 归母净利润(元)
    holder_profit_yoy: Optional[float] = None  # 归母净利润同比增长(%)
    gross_profit_ratio: Optional[float] = None  # 毛利率(%)
    eps_ttm: Optional[float] = None  # TTM每股收益(元)
    operate_income_qoq: Optional[float] = None  # 营业总收入滚动环比增长(%)
    net_profit_ratio: Optional[float] = None  # 净利率(%)
    roe_avg: Optional[float] = None  # 平均净资产收益率(%)
    gross_profit_qoq: Optional[float] = None  # 毛利润滚动环比增长(%)
    roa: Optional[float] = None  # 总资产净利率(%)
    holder_profit_qoq: Optional[float] = None  # 归母净利润滚动环比增长(%)
    roe_yearly: Optional[float] = None  # 年化净资产收益率(%)
    roic_yearly: Optional[float] = None  # 年化投资回报率(%)
    tax_ebt: Optional[float] = None  # 所得税/利润总额(%)
    ocf_sales: Optional[float] = None  # 经营现金流/营业收入(%)
    debt_asset_ratio: Optional[float] = None  # 资产负债率(%)
    current_ratio: Optional[float] = None  # 流动比率(倍)
    currentdebt_debt: Optional[float] = None  # 流动负债/总负债(%)
    start_date: Optional[str] = None  # 起始日期
    fiscal_year: Optional[str] = None  # 最后日期
    currency: Optional[str] = None  # 币种
    is_cny_code: Optional[int] = None  # 是否人民币
    updated_at: Optional[str] = None  # 最后更新日期
