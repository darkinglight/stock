from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class Bonus:
    """分红模型"""
    report_period: str  # 报告期
    bonus_description: str  # 分红方案说明
    bonus_amount: float  # 分红总额
    dividend_payout_rate: float  # 股利支付率
    pre_tax_dividend_rate: float  # 税前分红率
    year: int  # 年份
    
    @classmethod
    def from_row(cls, row) -> 'Bonus':
        """从DataFrame行创建模型"""
        # 处理报告期
        report_period = row.get('报告期', '')
        
        # 提取年份
        year = 0
        if report_period:
            try:
                # 尝试从不同格式的日期中提取年份
                # 格式1: 2023-12-31
                # 格式2: 2023/12/31
                # 格式3: 2023年12月31日
                year_match = re.search(r'\d{4}', report_period)
                if year_match:
                    year = int(year_match.group())
            except:
                pass
        
        # 处理分红方案说明
        bonus_description = row.get('分红方案说明', '')
        
        # 处理分红总额
        bonus_amount = 0.0
        bonus_amount_val = row.get('分红总额', 0)
        if bonus_amount_val:
            try:
                bonus_amount = float(bonus_amount_val)
            except:
                pass
        
        # 处理股利支付率
        dividend_payout_rate = 0.0
        dividend_payout_rate_val = row.get('股利支付率', 0)
        if dividend_payout_rate_val:
            try:
                if isinstance(dividend_payout_rate_val, str) and '%' in dividend_payout_rate_val:
                    dividend_payout_rate = float(dividend_payout_rate_val.replace('%', ''))
                else:
                    dividend_payout_rate = float(dividend_payout_rate_val)
            except:
                pass
        
        # 处理税前分红率
        pre_tax_dividend_rate = 0.0
        pre_tax_dividend_rate_val = row.get('税前分红率', 0)
        if pre_tax_dividend_rate_val:
            try:
                if isinstance(pre_tax_dividend_rate_val, str) and '%' in pre_tax_dividend_rate_val:
                    pre_tax_dividend_rate = float(pre_tax_dividend_rate_val.replace('%', ''))
                else:
                    pre_tax_dividend_rate = float(pre_tax_dividend_rate_val)
            except:
                pass
        
        return cls(
            report_period=report_period,
            bonus_description=bonus_description,
            bonus_amount=bonus_amount,
            dividend_payout_rate=dividend_payout_rate,
            pre_tax_dividend_rate=pre_tax_dividend_rate,
            year=year
        )
