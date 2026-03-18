import pytest
from src.services import AStockService, HStockService
from src.models.stock import Stock


@pytest.fixture
def a_stock_service():
    """创建A股服务实例"""
    return AStockService()


@pytest.fixture
def h_stock_service():
    """创建H股服务实例"""
    return HStockService()


def test_a_stock_service_creation(a_stock_service):
    """测试A股服务创建"""
    assert a_stock_service is not None


def test_h_stock_service_creation(h_stock_service):
    """测试H股服务创建"""
    assert h_stock_service is not None


def test_a_stock_service_save_stock(a_stock_service):
    """测试保存A股"""
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
    result = a_stock_service._save_stock(stock)
    assert result is True
    
    # 查询股票
    saved_stock = a_stock_service._get_stock_by_code("600000")
    assert saved_stock is not None
    assert saved_stock.code == "600000"
    assert saved_stock.name == "浦发银行"
    assert saved_stock.price == 10.5
    assert saved_stock.pe == 5.2
    assert saved_stock.pb == 0.8
    assert saved_stock.bonus_rate == 0.05
    assert saved_stock.market_cap == 300000000000


def test_h_stock_service_save_stock(h_stock_service):
    """测试保存H股"""
    stock = Stock(
        code="00001",
        name="长江实业",
        price=50.5,
        market="h",
        pe=10.2,
        pb=1.5
    )
    
    # 保存股票
    result = h_stock_service._save_stock(stock)
    assert result is True
    
    # 查询股票
    saved_stock = h_stock_service._get_stock_by_code("00001")
    assert saved_stock is not None
    assert saved_stock.code == "00001"
    assert saved_stock.name == "长江实业"
    assert saved_stock.price == 50.5
    assert saved_stock.pe == 10.2
    assert saved_stock.pb == 1.5


def test_a_stock_service_get_all_stocks(a_stock_service):
    """测试获取所有A股"""
    # 保存多个股票
    stocks = [
        Stock(code="600000", name="浦发银行", price=10.5, market="a"),
        Stock(code="600036", name="招商银行", price=35.2, market="a"),
        Stock(code="000001", name="平安银行", price=12.8, market="a")
    ]
    
    for stock in stocks:
        a_stock_service._save_stock(stock)
    
    # 获取所有股票
    all_stocks = a_stock_service._get_all_stocks()
    assert len(all_stocks) == 3
    assert any(s.code == "600000" for s in all_stocks)
    assert any(s.code == "600036" for s in all_stocks)
    assert any(s.code == "000001" for s in all_stocks)


def test_h_stock_service_get_all_stocks(h_stock_service):
    """测试获取所有H股"""
    # 保存多个股票
    stocks = [
        Stock(code="00001", name="长江实业", price=50.5, market="h"),
        Stock(code="00002", name="中电控股", price=25.2, market="h"),
        Stock(code="00003", name="中华煤气", price=18.8, market="h")
    ]
    
    for stock in stocks:
        h_stock_service._save_stock(stock)
    
    # 获取所有股票
    all_stocks = h_stock_service._get_all_stocks()
    assert len(all_stocks) == 3
    assert any(s.code == "00001" for s in all_stocks)
    assert any(s.code == "00002" for s in all_stocks)
    assert any(s.code == "00003" for s in all_stocks)


def test_a_stock_service_filter_by_pe(a_stock_service):
    """测试根据市盈率筛选A股"""
    # 保存多个股票
    stocks = [
        Stock(code="600000", name="浦发银行", price=10.5, market="a", pe=5.2),
        Stock(code="600036", name="招商银行", price=35.2, market="a", pe=8.5),
        Stock(code="000001", name="平安银行", price=12.8, market="a", pe=4.8)
    ]
    
    for stock in stocks:
        a_stock_service._save_stock(stock)
    
    # 筛选市盈率在5-9之间的股票
    filtered_stocks = a_stock_service.filter_by_pe(5.0, 9.0)
    assert len(filtered_stocks) == 2
    assert any(s.code == "600000" for s in filtered_stocks)
    assert any(s.code == "600036" for s in filtered_stocks)
    assert not any(s.code == "000001" for s in filtered_stocks)


def test_a_stock_service_get_stock_detail(a_stock_service):
    """测试获取A股详情"""
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
    a_stock_service._save_stock(stock)
    
    # 获取股票详情
    detail = a_stock_service.get_stock_detail("600000")
    assert detail is not None
    assert detail.code == "600000"
    assert detail.name == "浦发银行"
    assert detail.price == 10.5


def test_h_stock_service_get_stock_detail(h_stock_service):
    """测试获取H股详情"""
    # 保存股票
    stock = Stock(
        code="00001",
        name="长江实业",
        price=50.5,
        market="h",
        pe=10.2,
        pb=1.5
    )
    h_stock_service._save_stock(stock)
    
    # 获取股票详情
    detail = h_stock_service.get_stock_detail("00001")
    assert detail is not None
    assert detail.code == "00001"
    assert detail.name == "长江实业"
    assert detail.price == 50.5
