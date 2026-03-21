from typing import List, Optional, Tuple
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
            
            # 计算季度ROE
            quarterly_roe_list = self.calculate_quarterly_roe(roe_list)
            
            if not quarterly_roe_list:
                print(f"股票 {code} 计算ROE失败，返回空列表")
                return []
            
            # 生成模型列表
            return self._generate_financial_reports(code, quarterly_roe_list)
            
        except Exception as e:
            print(f"获取股票 {code} 季度财务数据失败: {e}")
            return []
    
    def calculate_quarterly_roe(self, roe_list: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """
        计算季度ROE
        :param roe_list: 最近13个季度的ROE数据列表，每个元素为(财报日期, ROE值)元组
        :return: 季度ROE列表，每个元素为(财报日期, 季度ROE值)元组
        """
        if len(roe_list) < 13:
            return []
        
        # 计算最近12个季度的季度ROE
        quarterly_roe_list = []
        for i in range(1, 13):
            current_period = roe_list[i-1][0]
            if current_period.endswith('0331'):
                # 03-31报告期的ROE就是季度ROE
                quarterly_roe = roe_list[i-1][1]
            else:
                # 其他报告期需要当期减去上期
                quarterly_roe = roe_list[i-1][1] - roe_list[i][1]
            quarterly_roe_list.append((current_period, quarterly_roe))
        
        return quarterly_roe_list
    
    def _get_roe_data(self, code: str) -> List[Tuple[str, float]]:
        """
        使用stock_financial_abstract获取ROE数据
        :param code: 股票代码
        :return: ROE数据列表，每个元素为(财报日期, ROE值)元组
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
                            roe_list.append((col, float(roe_value)))
                    break
            
            # 确保数据按时间顺序排列（最近的在前）
            roe_list = roe_list[:13]  # 只保留最近13个季度的数据
            
        except Exception as e:
            print(f"获取股票 {code} ROE数据失败: {e}")
        
        return roe_list
    
    def _generate_financial_reports(self, code: str, quarterly_roe_list: List[Tuple[str, float]]) -> List[FinancialReport]:
        """
        生成季度财务报告模型列表
        :param code: 股票代码
        :param quarterly_roe_list: 季度ROE列表，每个元素为(财报日期, 季度ROE值)元组
        :return: 季度财务报告模型列表
        """
        reports = []
        
        for item in quarterly_roe_list:
            report_period, quarterly_roe = item
            
            # 创建模型对象
            report = FinancialReport(
                code=code,
                report_period=report_period,
                quarterly_roe=quarterly_roe
            )
            reports.append(report)
        
        return reports

if __name__ == "__main__":
    service = FinancialDataService()
    reports = service.get_quarterly_financial_data('600987')
    print(reports)