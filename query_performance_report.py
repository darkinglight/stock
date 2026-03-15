import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

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
        
        # 复制DataFrame以避免警告
        profit_both_positive = profit_both_positive.copy()
        
        # 获取股票代码列表
        stock_codes = profit_both_positive['股票代码'].tolist()
        print(f"正在获取 {len(stock_codes)} 只股票的最新价...")
        
        # 获取最新价
        stock_prices = {}
        success_count = 0
        
        for code in stock_codes:
            try:
                # 确定交易所前缀
                if code.startswith('6'):
                    symbol = f'SH{code}'
                else:
                    symbol = f'SZ{code}'
                
                # 尝试获取雪球实时行情
                spot_data = ak.stock_individual_spot_xq(symbol=symbol)
                
                if spot_data is not None and len(spot_data) > 0:
                    # 查找现价
                    if '现价' in spot_data.columns:
                        latest_price = spot_data.iloc[0]['现价']
                        stock_prices[code] = latest_price
                        success_count += 1
            except Exception as e:
                stock_prices[code] = None
        
        # 将最新价添加到DataFrame
        profit_both_positive['最新价'] = profit_both_positive['股票代码'].map(stock_prices)
        
        # 统计获取到最新价的股票数量
        valid_prices = profit_both_positive['最新价'].notna().sum()
        if valid_prices > 0:
            print(f"✓ 成功获取 {valid_prices} 只股票的最新价")
        else:
            print(f"✗ 未能获取股票最新价（雪球接口不稳定）")
        
        # 保存净利润数据
        profit_filename = "业绩快报_2025年报_净利润同比环比双增长.csv"
        profit_both_positive.to_csv(profit_filename, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存到: {profit_filename}")
    
except Exception as e:
    print(f"✗ 查询2025年年报业绩快报失败: {e}")
