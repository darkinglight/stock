"""测试财务数据服务"""

import pytest
from src.services.financial_data_service import FinancialDataService


class TestFinancialDataService:
    """财务数据服务测试类"""
    
    def setup_method(self):
        """测试方法的 setup"""
        self.service = FinancialDataService()
        self.stock_code = "600000"
    
    def test_get_roe_data(self):
        """测试获取ROE数据方法"""
        roe_list = self.service._get_roe_data(self.stock_code)
        assert isinstance(roe_list, list), "ROE数据应该是一个列表"
        assert len(roe_list) > 0, "ROE数据列表长度应该大于0"
    
    def test_calculate_quarterly_and_annualized_roe(self):
        """测试计算季度ROE和年化ROE方法"""
        roe_list = self.service._get_roe_data(self.stock_code)
        if len(roe_list) >= 13:
            quarterly_roe_list, annualized_roe_list = self.service.calculate_quarterly_and_annualized_roe(roe_list)
            assert isinstance(quarterly_roe_list, list), "季度ROE数据应该是一个列表"
            assert isinstance(annualized_roe_list, list), "年化ROE数据应该是一个列表"
            assert len(quarterly_roe_list) > 0, "季度ROE数据列表长度应该大于0"
            assert len(annualized_roe_list) > 0, "年化ROE数据列表长度应该大于0"
    
    def test_get_quarterly_financial_data(self):
        """测试获取季度财务数据方法"""
        reports = self.service.get_quarterly_financial_data(self.stock_code)
        assert isinstance(reports, list), "财务报告数据应该是一个列表"
        assert len(reports) > 0, "财务报告数据列表长度应该大于0"
        
        if reports:
            for report in reports:
                assert hasattr(report, 'report_period'), "报告对象应该有report_period属性"
                assert hasattr(report, 'quarterly_roe'), "报告对象应该有quarterly_roe属性"
                assert hasattr(report, 'annualized_roe'), "报告对象应该有annualized_roe属性"
