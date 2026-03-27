from dataclasses import dataclass
from typing import Optional


@dataclass
class Stock:
    """股票模型"""
    code: str  # 股票代码
    name: str  # 股票名称
    price: float  # 股票价格
    market: str  # 市场类型，'a' for A股, 'h' for H股
    pe: Optional[float] = None  # 市盈率
    pb: Optional[float] = None  # 市净率
    bonus_rate: Optional[float] = None  # 分红率
    net_asset_per_share: Optional[float] = None  # 每股净资产
    basic_eps: Optional[float] = None  # 每股收益
    assets_debt_ratio: Optional[float] = None  # 资产负债率
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Stock':
        """从字典创建模型"""
        return cls(
            code=data.get('code', ''),
            name=data.get('name', ''),
            price=float(data.get('price', 0)),
            market=data.get('market', 'a'),
            pe=float(data.get('pe')) if data.get('pe') else None,
            pb=float(data.get('pb')) if data.get('pb') else None,
            bonus_rate=float(data.get('bonus_rate')) if data.get('bonus_rate') else None,
            net_asset_per_share=float(data.get('net_asset_per_share')) if data.get('net_asset_per_share') else None,
            basic_eps=float(data.get('basic_eps')) if data.get('basic_eps') else None,
            assets_debt_ratio=float(data.get('assets_debt_ratio')) if data.get('assets_debt_ratio') else None,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
