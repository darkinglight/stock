import akshare as ak
from typing import Optional
import datetime
import re


class AStockBonusService:
    """A股分红服务 - 处理A股分红率相关数据"""
    
    def get_bonus_rate(self, code: str) -> Optional[float]:
        """
        获取A股的平均分红率（基于近3年数据）
        
        Args:
            code: A股代码
            
        Returns:
            Optional[float]: 近3年的平均分红率，如果没有近3年数据返回 None
        """
        try:
            # 从同花顺获取分红配送数据
            df = ak.stock_fhps_detail_ths(symbol=code)
            
            if df.empty:
                return None
            
            # 处理数据 - 按年份分组
            year_rates = {}
            current_year = datetime.datetime.now().year
            three_years_ago = current_year - 3
            
            for _, row in df.iterrows():
                # 提取报告期年份
                report_period = row.get('报告期', '')
                if not report_period:
                    continue
                
                try:
                    # 尝试从不同格式的日期中提取年份
                    # 格式1: 2023-12-31
                    # 格式2: 2023/12/31
                    # 格式3: 2023年12月31日
                    year_match = re.search(r'\d{4}', report_period)
                    if not year_match:
                        continue
                    year = int(year_match.group())
                except:
                    continue
                
                # 提取股利支付率
                dividend_payout_rate = row.get('股利支付率', '')
                if not dividend_payout_rate:
                    continue
                
                try:
                    # 去除百分号并转换为浮点数
                    rate = float(dividend_payout_rate.replace('%', ''))
                    if year not in year_rates:
                        year_rates[year] = []
                    year_rates[year].append(rate)
                except:
                    continue
            
            if not year_rates:
                return None
            
            # 收集近三年的所有记录
            recent_three_years = [year for year in year_rates if year >= three_years_ago]
            
            if not recent_three_years:
                # 没有近3年数据，返回 None
                return 0
            
            # 收集近三年的所有记录
            target_rates = []
            for year in recent_three_years:
                target_rates.extend(year_rates[year])
            
            if not target_rates:
                # 没有近3年数据，返回 None
                return 0
            
            # 计算近3年所有记录的平均值
            average_rate = sum(target_rates) / len(target_rates)
            
            return average_rate
            
        except Exception as e:
            print(f"获取A股分红率失败: {e}")
            return None


if __name__ == "__main__":
    # 测试
    a_stock_bonus_service = AStockBonusService()
    
    # 测试获取平均分红率
    stock_code = "600987"
    print(f"正在测试股票代码: {stock_code}")
    average_bonus_rate = a_stock_bonus_service.get_bonus_rate(stock_code)
    if average_bonus_rate is not None:
        print(f"A股 {stock_code} 的平均分红率: {average_bonus_rate:.2f}%")
    else:
        print(f"A股 {stock_code} 没有找到分红数据")
