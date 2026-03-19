import akshare as ak

# 获取财务摘要数据
stock_financial_abstract_df = ak.stock_financial_abstract(symbol="600004")

# 输出详细内容
print("=== 财务摘要数据详细信息 ===")
print(f"数据形状: {stock_financial_abstract_df.shape}")
print(f"列名: {list(stock_financial_abstract_df.columns)}")
print("\n=== 数据前10行 ===")
print(stock_financial_abstract_df.head(10))
print("\n=== 数据后10行 ===")
print(stock_financial_abstract_df.tail(10))
print("\n=== 数据统计信息 ===")
print(stock_financial_abstract_df.describe())
print("\n=== 完整数据 ===")
print(stock_financial_abstract_df)
# 获取所有指标名称（列名）
print("所有指标名称：")
for col in stock_financial_abstract_df.columns:
    print(col)
