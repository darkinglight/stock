from typing import List, Optional
from src.models.quarterly_financial import QuarterlyFinancialReport


class FinancialDataService:
    """财务数据服务 - 处理财务数据的获取和处理"""
    
    def __init__(self):
        """
        初始化财务数据服务
        """
        pass
    
    def get_quarterly_financial_data(self, code: str) -> List[QuarterlyFinancialReport]:
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
            
            # 计算季度ROE和年化ROE
            quarterly_roe_list, annualized_roe_list = self.calculate_quarterly_and_annualized_roe(roe_list)
            
            if not quarterly_roe_list or not annualized_roe_list:
                print(f"股票 {code} 计算ROE失败，返回空列表")
                return []
            
            # 生成模型列表
            return self._generate_quarterly_financial_reports(code, quarterly_roe_list, annualized_roe_list)
            
        except Exception as e:
            print(f"获取股票 {code} 季度财务数据失败: {e}")
            return []
    
    def calculate_quarterly_and_annualized_roe(self, roe_list: List[float]) -> tuple:
        """
        计算季度ROE和年化ROE
        :param roe_list: 最近13个季度的ROE数据列表
        :return: (季度ROE列表, 年化ROE列表)
        """
        if len(roe_list) < 13:
            return [], []
        
        # 计算最近12个季度的季度ROE
        quarterly_roe_list = []
        for i in range(1, 13):
            quarterly_roe = roe_list[i-1] - roe_list[i]
            quarterly_roe_list.append(quarterly_roe)
        
        # 计算最近9个季度的年化ROE
        annualized_roe_list = []
        for i in range(0, 9):
            # 最近4个季度的ROE之和作为年化ROE
            if i + 4 <= len(quarterly_roe_list):
                annualized_roe = sum(quarterly_roe_list[i:i+4])
                annualized_roe_list.append(annualized_roe)
        
        return quarterly_roe_list, annualized_roe_list
    
    def _get_roe_data(self, code: str) -> List[float]:
        """
        使用stock_financial_abstract获取ROE数据
        :param code: 股票代码
        :return: ROE数据列表
        """
        import akshare as ak
        
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
                            roe_list.append(float(roe_value))
                    break
            
            # 确保数据按时间顺序排列（最近的在前）
            roe_list = roe_list[:13]  # 只保留最近13个季度的数据
            
        except Exception as e:
            print(f"获取股票 {code} ROE数据失败: {e}")
        
        return roe_list
    
    def _generate_quarterly_financial_reports(self, code: str, quarterly_roe_list: List[float], annualized_roe_list: List[float]) -> List[QuarterlyFinancialReport]:
        """
        生成季度财务报告模型列表
        :param code: 股票代码
        :param quarterly_roe_list: 季度ROE列表
        :param annualized_roe_list: 年化ROE列表
        :return: 季度财务报告模型列表
        """
        reports = []
        
        for i in range(len(quarterly_roe_list)):
            # 生成报告期（这里简化处理，实际应该根据真实的财报日期）
            year = 2024 - (i // 4)
            quarter = 4 - (i % 4)
            report_period = f"{year}-{quarter*3:02d}-30"
            
            # 计算年化ROE（如果有）
            annualized_roe = None
            if i < len(annualized_roe_list):
                annualized_roe = annualized_roe_list[i]
            
            # 创建模型对象
            report = QuarterlyFinancialReport(
                code=code,
                report_period=report_period,
                quarterly_roe=quarterly_roe_list[i],
                annualized_roe=annualized_roe
            )
            reports.append(report)
        
        return reports
