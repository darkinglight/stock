import akshare as ak
from typing import Optional, Dict
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
                
                # 提取税前分红率
                pre_tax_dividend_rate = row.get('税前分红率', '')
                if not pre_tax_dividend_rate:
                    continue
                
                try:
                    # 去除百分号并转换为浮点数
                    rate = float(pre_tax_dividend_rate.replace('%', ''))
                    if year not in year_rates:
                        year_rates[year] = []
                    year_rates[year].append(rate)
                except:
                    continue
            
            if not year_rates:
                return None
            
            # 计算每年的累计分红率
            yearly_totals = {}
            for year, rates in year_rates.items():
                yearly_totals[year] = sum(rates)
            
            # 计算近3年的平均分红率（基于每年的累计分红率）
            recent_three_years = [year for year in yearly_totals if year >= three_years_ago]
            
            if not recent_three_years:
                # 没有近3年数据，返回 None
                return 0
            
            # 使用近3年数据计算平均值
            target_rates = [yearly_totals[year] for year in recent_three_years]
            average_rate = sum(target_rates) / len(target_rates)
            
            return average_rate
            
        except Exception as e:
            print(f"获取A股分红率失败: {e}")
            return None


if __name__ == "__main__":
    # 测试
    a_stock_bonus_service = AStockBonusService()
    
    # 测试获取平均分红率
    stock_code = "002867"
    average_bonus_rate = a_stock_bonus_service.get_bonus_rate(stock_code)
    print(f"A股 {stock_code} 的平均分红率: {average_bonus_rate:.2f}%")
