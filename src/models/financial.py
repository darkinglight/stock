from dataclasses import dataclass
from typing import Optional

@dataclass
class FinancialReport:
    """单季度财务数据模型"""
    code: str  # 股票代码
    report_period: str  # 报告期，格式：YYYY-MM-DD
    quarterly_roe: Optional[float] = None  # 单季净资产收益率
