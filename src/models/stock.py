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
    market_cap: Optional[float] = None  # 市值
    created_at: Optional[str] = None  # 创建时间
    updated_at: Optional[str] = None  # 更新时间
    
    def validate(self) -> bool:
        """验证模型数据"""
        if not self.code or not self.name:
            return False
        if self.price <= 0:
            return False
        return True
    
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
            market_cap=float(data.get('market_cap')) if data.get('market_cap') else None,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
