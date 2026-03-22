from typing import List, Optional
from models.financial import Financial
import akshare as ak


class FinancialDataService:
    """财务数据服务 - 处理财务数据的获取和处理"""
    
    def __init__(self):
        """
        初始化财务数据服务
        """
        pass
    
    def get_quarterly_financial_data(self, code: str) -> List[Financial]:
        """
        获取单个股票的季度财务数据
        :param code: 股票代码
        :return: 季度财务数据列表
        """
        try:
            # 获取ROE数据
            financial_list = self._get_financial_data(code)
            
            if len(financial_list) < 13:
                print(f"股票 {code} 数据不足13个季度，返回空列表")
                return []
            
            # 计算季度ROE（直接修改原对象）
            self.calculate_quarterly_roe(financial_list)
            
            # 只返回最近12个季度的数据
            return financial_list[:12]
            
        except Exception as e:
            print(f"获取股票 {code} 季度财务数据失败: {e}")
            return []
    
    def calculate_quarterly_roe(self, financial_list: List[Financial]):
        """
        计算季度ROE（直接修改原对象）
        :param financial_list: 最近13个季度的财务数据列表，每个元素为Financial对象
        """
        if len(financial_list) < 13:
            return
        
        # 计算最近12个季度的季度ROE
        for i in range(1, 13):
            current_report = financial_list[i-1]
            if current_report.report_period.endswith('0331'):
                # 03-31报告期的ROE就是季度ROE
                current_report.quarterly_roe = current_report.roe
            else:
                # 其他报告期需要当期减去上期
                current_report.quarterly_roe = current_report.roe - financial_list[i].roe
    
    def _get_financial_data(self, code: str) -> List[Financial]:
        """
        使用stock_financial_abstract获取财务数据
        :param code: 股票代码
        :return: 财务数据列表，每个元素为Financial对象
        """
        financial_list = []
        roe_data = {}
        net_asset_data = {}
        
        try:
            # 从akshare获取财务摘要数据
            stock_financial_abstract_df = ak.stock_financial_abstract(symbol=code)
            
            # 提取ROE和每股净资产数据
            for index, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '净资产收益率(ROE)':
                    # 提取最近13个季度的ROE数据
                    for col in stock_financial_abstract_df.columns[2:15]:  # 从第2列开始，提取最近13个季度的数据
                        roe_value = row[col]
                        if roe_value and not isinstance(roe_value, str):
                            roe_data[col] = float(roe_value)
                elif row['指标'] == '每股净资产':
                    # 提取最近13个季度的每股净资产数据
                    for col in stock_financial_abstract_df.columns[2:15]:  # 从第2列开始，提取最近13个季度的数据
                        net_asset_value = row[col]
                        if net_asset_value and not isinstance(net_asset_value, str):
                            net_asset_data[col] = float(net_asset_value)
            
            # 创建Financial对象
            for period in roe_data.keys():
                report = Financial(
                    code=code,
                    report_period=period,
                    roe=roe_data.get(period),
                    net_asset_per_share=net_asset_data.get(period)
                )
                financial_list.append(report)
            
            # 确保数据按时间顺序排列（最近的在前）
            financial_list = financial_list[:13]  # 只保留最近13个季度的数据
            
        except Exception as e:
            print(f"获取股票 {code} 财务数据失败: {e}")
        
        return financial_list


if __name__ == "__main__":
    service = FinancialDataService()
    reports = service.get_quarterly_financial_data('600987')
    print(reports)