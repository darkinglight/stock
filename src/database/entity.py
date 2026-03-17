"""
Entity 基类
提供简洁的 Entity 定义，让 Repository 可以直接操作 Entity 对象
"""
from dataclasses import dataclass, fields as dataclass_fields
from typing import TypeVar, Type, Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='BaseEntity')


@dataclass
class BaseEntity:
    """
    Entity 基类
    所有 Entity 都应该继承此类
    
    使用示例：
    @dataclass
    class Stock(BaseEntity):
        __tablename__ = 'a_stock'
        
        code: str
        name: str
        price: float
    """
    
    __tablename__: str = ""
    """表名"""
    
    @classmethod
    def get_table_name(cls) -> str:
        """获取表名"""
        return cls.__tablename__
    
    @classmethod
    def get_field_names(cls) -> List[str]:
        """获取所有字段名"""
        return [f.name for f in dataclass_fields(cls)]
    
    def to_dict(self) -> Dict[str, Any]:
        """将 Entity 转换为字典"""
        return {f.name: getattr(self, f.name) for f in dataclass_fields(self)}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """从字典创建 Entity"""
        field_dict = {f.name: data.get(f.name) for f in dataclass_fields(cls)}
        return cls(**field_dict)
    
    def validate(self) -> bool:
        """
        验证实体数据
        子类可以重写此方法实现自定义验证逻辑
        :return: 是否有效
        """
        return True