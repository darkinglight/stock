from dataclasses import dataclass
from typing import Optional


@dataclass
class HkFinancial:
    """港股财务数据模型"""
    secucode: str
    security_code: str
    security_name_abbr: Optional[str] = None
    org_code: Optional[str] = None
    report_date: Optional[str] = None
    date_type_code: Optional[str] = None
    per_netcash_operate: Optional[float] = None
    per_oi: Optional[float] = None
    bps: Optional[float] = None
    basic_eps: Optional[float] = None
    diluted_eps: Optional[float] = None
    operate_income: Optional[float] = None
    operate_income_yoy: Optional[float] = None
    gross_profit: Optional[float] = None
    gross_profit_yoy: Optional[float] = None
    holder_profit: Optional[float] = None
    holder_profit_yoy: Optional[float] = None
    gross_profit_ratio: Optional[float] = None
    eps_ttm: Optional[float] = None
    operate_income_qoq: Optional[float] = None
    net_profit_ratio: Optional[float] = None
    roe_avg: Optional[float] = None
    gross_profit_qoq: Optional[float] = None
    roa: Optional[float] = None
    holder_profit_qoq: Optional[float] = None
    roe_yearly: Optional[float] = None
    roic_yearly: Optional[float] = None
    tax_ebt: Optional[float] = None
    ocf_sales: Optional[float] = None
    debt_asset_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    currentdebt_debt: Optional[float] = None
    start_date: Optional[str] = None
    fiscal_year: Optional[str] = None
    currency: Optional[str] = None
    is_cny_code: Optional[int] = None
    updated_at: Optional[str] = None
