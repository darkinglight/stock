#!/usr/bin/env python3
"""
测试A股刷新功能
"""

from src.services.a_stock_service import AStockService

def test_refresh_functionality():
    """测试刷新功能"""
    print("=== 测试A股刷新功能 ===")
    
    # 创建A股服务实例
    service = AStockService()
    
    # 第一次刷新
    print("\n1. 第一次刷新:")
    count1 = service.refresh_stocks()
    print(f"   更新了 {count1} 只股票")
    
    # 立即再次刷新（应该跳过，因为1天内不重复更新）
    print("\n2. 立即再次刷新（应该跳过）:")
    count2 = service.refresh_stocks()
    print(f"   更新了 {count2} 只股票")
    
    # 获取所有A股
    print("\n3. 获取所有A股:")
    stocks = service._get_all_stocks()
    print(f"   共有 {len(stocks)} 只A股")
    
    # 显示股票信息
    print("\n4. 股票信息:")
    for i, stock in enumerate(stocks):
        print(f"   {i+1}. {stock.code} - {stock.name} - {stock.market} - ¥{stock.price}")
    
    # 测试根据代码获取股票
    print("\n5. 测试根据代码获取股票:")
    test_code = "600000"
    stock = service.get_stock_detail(test_code)
    if stock:
        print(f"   股票 {test_code} 详情: {stock.name} - {stock.market} - ¥{stock.price}")
    else:
        print(f"   股票 {test_code} 未找到")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_refresh_functionality()