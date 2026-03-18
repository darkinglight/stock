import pytest
from src.services.stock_service import StockService
from src.models.stock import Stock


@pytest.fixture
def stock_service():
    """创建股票服务实例"""
    return StockService(":memory:")


def test_stock_service_creation(stock_service):
    """测试股票服务创建"""
    assert stock_service is not None
    assert stock_service.db_name == ":memory:"


def test_stock_service_save_stock(stock_service):
    """测试保存股票"""
    stock = Stock(
        code="600000",
        name="浦发银行",
        price=10.5,
        market="a",
        pe=5.2,
        pb=0.8,
        bonus_rate=0.05,
        market_cap=300000000000
    )
    
    # 保存股票
    result = stock_service._save_stock(stock)
    assert result is True
    
    # 查询股票
    saved_stock = stock_service._get_stock_by_code("600000", "a")
    assert saved_stock is not None
    assert saved_stock.code == "600000"
    assert saved_stock.name == "浦发银行"
    assert saved_stock.price == 10.5
    assert saved_stock.pe == 5.2
    assert saved_stock.pb == 0.8
    assert saved_stock.bonus_rate == 0.05
    assert saved_stock.market_cap == 300000000000


def test_stock_service_get_all_stocks(stock_service):
    """测试获取所有股票"""
    # 保存多个股票
    stocks = [
        Stock(code="600000", name="浦发银行", price=10.5, market="a"),
        Stock(code="600036", name="招商银行", price=35.2, market="a"),
        Stock(code="000001", name="平安银行", price=12.8, market="a")
    ]
    
    for stock in stocks:
        stock_service._save_stock(stock)
    
    # 获取所有股票
    all_stocks = stock_service._get_all_stocks("a")
    assert len(all_stocks) == 3
    assert any(s.code == "600000" for s in all_stocks)
    assert any(s.code == "600036" for s in all_stocks)
    assert any(s.code == "000001" for s in all_stocks)


def test_stock_service_filter_by_pe(stock_service):
    """测试根据市盈率筛选股票"""
    # 保存多个股票
    stocks = [
        Stock(code="600000", name="浦发银行", price=10.5, market="a", pe=5.2),
        Stock(code="600036", name="招商银行", price=35.2, market="a", pe=8.5),
        Stock(code="000001", name="平安银行", price=12.8, market="a", pe=4.8)
    ]
    
    for stock in stocks:
        stock_service._save_stock(stock)
    
    # 筛选市盈率在5-9之间的股票
    filtered_stocks = stock_service.filter_by_pe(5.0, 9.0, "a")
    assert len(filtered_stocks) == 2
    assert any(s.code == "600000" for s in filtered_stocks)
    assert any(s.code == "600036" for s in filtered_stocks)
    assert not any(s.code == "000001" for s in filtered_stocks)


def test_stock_service_get_stock_detail(stock_service):
    """测试获取股票详情"""
    # 保存股票
    stock = Stock(
        code="600000",
        name="浦发银行",
        price=10.5,
        market="a",
        pe=5.2,
        pb=0.8,
        bonus_rate=0.05
    )
    stock_service._save_stock(stock)
    
    # 获取股票详情
    detail = stock_service.get_stock_detail("600000", "a")
    assert detail is not None
    assert detail.code == "600000"
    assert detail.name == "浦发银行"
    assert detail.price == 10.5
