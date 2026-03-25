import akshare as ak
from typing import List
from models.financial import Financial

class FinancialThsService:
    """同花顺财务数据服务"""
    
    def get_financial_data(self, symbol: str) -> List[Financial]:
        """
        获取股票的财务数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            List[Financial]: 财务数据列表
        """
        # 获取财务摘要数据
        stock_financial_abstract_new_ths_df = ak.stock_financial_abstract_new_ths(
            symbol=symbol, 
            indicator="按报告期"
        )
        
        # 按报告期分组处理数据
        financial_data = {}
        
        for _, row in stock_financial_abstract_new_ths_df.iterrows():
            report_date = row['report_date']
            metric_name = row['metric_name']
            value = row['value']
            
            # 初始化该报告期的 Financial 对象
            if report_date not in financial_data:
                financial_data[report_date] = Financial(
                    code=symbol,
                    report_period=report_date
                )
            
            # 处理不同的指标
            if metric_name == 'index_weighted_avg_roe':
                # 季度净资产收益率
                financial_data[report_date].quarterly_roe = value
            elif metric_name == 'calc_per_net_assets':
                # 每股净资产
                financial_data[report_date].net_asset_per_share = value
            elif metric_name == 'basic_eps':
                # 每股收益
                financial_data[report_date].basic_eps = value
            elif metric_name == 'index_per_operating_cash_flow_net':
                # 每股经营现金流
                financial_data[report_date].operating_cash_flow_per_share = value
            elif metric_name == 'assets_debt_ratio':
                # 资产负债率
                financial_data[report_date].assets_debt_ratio = value
        
        # 转换为列表
        financial_list = list(financial_data.values())
        
        # 按报告期降序排序
        financial_list.sort(key=lambda x: x.report_period, reverse=True)
        
        # 只保留最近12个季度的数据
        financial_list = financial_list[:12]
        
        return financial_list

if __name__ == "__main__":
    # 测试
    financial_ths_service = FinancialThsService()
    financial_data = financial_ths_service.get_financial_data("000063")
    print(financial_data)