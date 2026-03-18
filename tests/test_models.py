import pytest
from src.models.stock import Stock


def test_stock_model_creation():
    """测试股票模型创建"""
    stock = Stock(
        code="600000",
        name="浦发银行",
        price=10.5,
        market="a",
        pe=5.2,
        pb=0.8,
        bonus_rate=0.05
    )
    
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5
    assert stock.market == "a"
    assert stock.pe == 5.2
    assert stock.pb == 0.8
    assert stock.bonus_rate == 0.05


def test_stock_model_validation():
    """测试股票模型验证"""
    # 有效股票
    stock = Stock(
        code="600000",
        name="浦发银行",
        price=10.5,
        market="a"
    )
    assert stock.validate() is True
    
    # 无效股票 - 缺少代码
    stock_no_code = Stock(
        code="",
        name="浦发银行",
        price=10.5,
        market="a"
    )
    assert stock_no_code.validate() is False
    
    # 无效股票 - 缺少名称
    stock_no_name = Stock(
        code="600000",
        name="",
        price=10.5,
        market="a"
    )
    assert stock_no_name.validate() is False
    
    # 无效股票 - 价格为负
    stock_neg_price = Stock(
        code="600000",
        name="浦发银行",
        price=-10.5,
        market="a"
    )
    assert stock_neg_price.validate() is False


def test_stock_model_from_dict():
    """测试从字典创建股票模型"""
    data = {
        "code": "600000",
        "name": "浦发银行",
        "price": "10.5",
        "market": "a",
        "pe": "5.2",
        "pb": "0.8",
        "bonus_rate": "0.05"
    }
    
    stock = Stock.from_dict(data)
    
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5
    assert stock.market == "a"
    assert stock.pe == 5.2
    assert stock.pb == 0.8
    assert stock.bonus_rate == 0.05


def test_stock_model_from_dict_with_missing_fields():
    """测试从缺少字段的字典创建股票模型"""
    data = {
        "code": "600000",
        "name": "浦发银行",
        "price": "10.5"
    }
    
    stock = Stock.from_dict(data)
    
    assert stock.code == "600000"
    assert stock.name == "浦发银行"
    assert stock.price == 10.5
    assert stock.market == "a"  # 默认值
    assert stock.pe is None  # 默认值
    assert stock.pb is None  # 默认值
    assert stock.bonus_rate is None  # 默认值
