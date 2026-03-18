from src.services.a_stock_service import AStockService

if __name__ == "__main__":
    print("测试 AStockService 刷新功能...")
    service = AStockService()
    result = service.refresh_stocks()
    print(f"刷新结果: 更新了 {result} 只股票")