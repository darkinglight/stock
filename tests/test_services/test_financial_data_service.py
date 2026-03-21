"""测试财务数据服务"""

import pytest
from src.services.financial_data_service import FinancialDataService


class TestFinancialDataService:
    """财务数据服务测试类"""
    
    def setup_method(self):
        """测试方法的 setup"""
        self.service = FinancialDataService()
        self.stock_code = "600000"
    
    def test_get_roe_data_sorted_by_date(self):
        """测试_get_roe_data方法返回值是否按日期逆序排序"""
        roe_list = self.service._get_roe_data(self.stock_code)
        assert isinstance(roe_list, list), "ROE数据应该是一个列表"
        assert len(roe_list) > 0, "ROE数据列表长度应该大于0"
        
        # 验证数据按日期逆序排序（最近的日期在前）
        for i in range(len(roe_list) - 1):
            current_date = roe_list[i][0]
            next_date = roe_list[i + 1][0]
            assert current_date > next_date, f"日期应该按逆序排序，当前日期 {current_date} 应该大于下一个日期 {next_date}"
