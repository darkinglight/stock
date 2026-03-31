from dataclasses import dataclass
from typing import Optional


@dataclass
class Stock:
    """股票模型"""
    code: str  # 股票代码
    name: Optional[str] = None  # 股票名称
    price: Optional[float] = None  # 股票价格
    market: Optional[str] = None  # 市场类型，'sh' for 沪市, 'sz' for 深市, 'bj' for 京市, 'h' for H股
    pe: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    bonus_rate: Optional[float] = None  # 分红率
    net_asset_per_share: Optional[float] = None  # 每股净资产
    basic_eps: Optional[float] = None  # 每股收益
    assets_debt_ratio: Optional[float] = None  # 资产负债率
    roe: Optional[float] = None  # 净资产收益率
    growth: Optional[float] = None  # 内在增长率 = roe * (1 - 分红率) + roe * 分红率 / pb
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    

