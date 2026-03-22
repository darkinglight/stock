from dataclasses import dataclass
from typing import Optional

@dataclass
class Financial:
    """单季度财务数据模型"""
    code: str  # 股票代码
    report_period: str  # 报告期，格式：YYYY-MM-DD
    roe: Optional[float] = None  # 净资产收益率
    quarterly_roe: Optional[float] = None  # 单季净资产收益率
    net_asset_per_share: Optional[float] = None  # 每股净资产
