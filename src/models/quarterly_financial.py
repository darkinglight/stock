from dataclasses import dataclass
from typing import Optional, List


@dataclass
class QuarterlyFinancialReport:
    """单季度财务数据模型"""
    code: str  # 股票代码
    report_period: str  # 报告期，格式：YYYY-MM-DD
    roe: Optional[float] = None  # 净资产收益率（当期）
    quarterly_roe: Optional[float] = None  # 季度ROE
    annualized_roe: Optional[float] = None  # 年化ROE

