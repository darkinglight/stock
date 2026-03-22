from typing import List, Optional
from models.financial import FinancialReport
import akshare as ak


class FinancialDataService:
    """财务数据服务 - 处理财务数据的获取和处理"""
    
    def __init__(self):
        """
        初始化财务数据服务
        """
        pass
    
    def get_quarterly_financial_data(self, code: str) -> List[FinancialReport]:
        """
        获取单个股票的季度财务数据
        :param code: 股票代码
        :return: 季度财务数据列表
        """
        try:
            # 获取ROE数据
            roe_list = self._get_roe_data(code)
            
            if len(roe_list) < 13:
                print(f"股票 {code} 数据不足13个季度，返回空列表")
                return []
            
            # 计算季度ROE（直接修改原对象）
            self.calculate_quarterly_roe(roe_list)
            
            # 只返回最近12个季度的数据
            return roe_list[:12]
            
        except Exception as e:
            print(f"获取股票 {code} 季度财务数据失败: {e}")
            return []
    
    def calculate_quarterly_roe(self, roe_list: List[FinancialReport]):
        """
        计算季度ROE（直接修改原对象）
        :param roe_list: 最近13个季度的ROE数据列表，每个元素为FinancialReport对象
        """
        if len(roe_list) < 13:
            return
        
        # 计算最近12个季度的季度ROE
        for i in range(1, 13):
            current_report = roe_list[i-1]
            if current_report.report_period.endswith('0331'):
                # 03-31报告期的ROE就是季度ROE
                current_report.quarterly_roe = current_report.roe
            else:
                # 其他报告期需要当期减去上期
                current_report.quarterly_roe = current_report.roe - roe_list[i].roe
    
    def _get_roe_data(self, code: str) -> List[FinancialReport]:
        """
        使用stock_financial_abstract获取ROE数据
        :param code: 股票代码
        :return: ROE数据列表，每个元素为FinancialReport对象
        """
        roe_list = []
        
        try:
            # 从akshare获取财务摘要数据
            stock_financial_abstract_df = ak.stock_financial_abstract(symbol=code)
            
            # 提取ROE数据
            for index, row in stock_financial_abstract_df.iterrows():
                if row['指标'] == '净资产收益率(ROE)':
                    # 提取最近13个季度的数据
                    for col in stock_financial_abstract_df.columns[2:15]:  # 从第2列开始，提取最近13个季度的数据
                        roe_value = row[col]
                        if roe_value and not isinstance(roe_value, str):
                            report = FinancialReport(
                                code=code,
                                report_period=col,
                                roe=float(roe_value)
                            )
                            roe_list.append(report)
                    break
            
            # 确保数据按时间顺序排列（最近的在前）
            roe_list = roe_list[:13]  # 只保留最近13个季度的数据
            
        except Exception as e:
            print(f"获取股票 {code} ROE数据失败: {e}")
        
        return roe_list


if __name__ == "__main__":
    service = FinancialDataService()
    reports = service.get_quarterly_financial_data('600987')
    print(reports)