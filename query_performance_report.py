import akshare as ak
import pandas as pd
from datetime import datetime

print("正在查询2025年年报业绩快报...")

try:
    yjkb_2025 = ak.stock_yjkb_em(date="20251231")
    print(f"✓ 成功获取2025年年报业绩快报，共 {len(yjkb_2025)} 条记录")
    
    # 定义字段名
    profit_growth_col = '净利润-同比增长'
    profit_qoq_col = '净利润-季度环比增长'
    
    # 过滤净利润同比和环比都为正的记录
    if profit_growth_col in yjkb_2025.columns and profit_qoq_col in yjkb_2025.columns:
        profit_both_positive = yjkb_2025[
            (yjkb_2025[profit_growth_col] > 0) & 
            (yjkb_2025[profit_qoq_col] > 0)
        ]
        print(f"✓ 净利润同比和环比都为正的记录: {len(profit_both_positive)} 条")
        
        # 保存净利润数据
        profit_filename = "业绩快报_2025年报_净利润同比环比双增长.csv"
        profit_both_positive.to_csv(profit_filename, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存到: {profit_filename}")
    
except Exception as e:
    print(f"✗ 查询2025年年报业绩快报失败: {e}")
