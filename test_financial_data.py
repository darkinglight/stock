"""测试财务数据接口"""

from src.services.a_stock_service import AStockService

# 创建A股服务实例
service = AStockService()

# 测试股票代码
stock_code = "600004"

# 获取财务数据
financial_data = service.get_financial_data(stock_code)

# 输出结果
print(f"股票代码: {stock_code}")
print(f"财务数据: {financial_data}")

if financial_data:
    print(f"最近4个季度ROE总和: {financial_data['roe']}")
    print(f"分红率: {financial_data['bonus_rate']}")
    print(f"市净率: {financial_data['pb']}")
    print(f"资产负债率: {financial_data['debt_ratio']}")

print("测试完成！")
