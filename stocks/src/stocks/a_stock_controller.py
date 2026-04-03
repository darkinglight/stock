import toga
from services.a_stock_service import AStockService
from services.a_bonus_service import ABonusService
from services.a_financial_service import AFinancialService
from services.config_service import ConfigService
from view.a_stock_list import StockListView
from view.a_stock_config import StockConfigView
from view.a_stock_detail import StockDetailView


class AStockController:
    def __init__(self):
        self.stock_list_view = None
        self.stock_config_view = None
        self.stock_detail_view = None
        self.detail_window = None
        self.service = AStockService()
        self.bonus_service = ABonusService()
        self.financial_service = AFinancialService()
        self.config_service = ConfigService()
        self._config = self.config_service.load_stock_list_config()

    def initialize_stock_list(self):
        stocks_data = self.get_stocks_data(self._config)

        self.stock_list_view = StockListView(
            stocks=stocks_data,
            on_select=self.on_stock_select
        )
        self.stock_config_view = StockConfigView(
            on_config_change=self.on_config_change,
            default_config=self._config
        )
        return self.stock_list_view
    
    def get_stocks_data(self, config):
        stocks_data = self.service.get_stocks_paginated(
            page=1,
            page_size=config['page_size'],
            sort_by=config['sort_by'],
            sort_order=config['sort_order'],
            max_debt_ratio=config.get('max_debt_ratio'),
            min_pe=config.get('min_pe'),
            max_pe=config.get('max_pe'),
            min_pb=config.get('min_pb'),
            max_pb=config.get('max_pb'),
            min_roe=config.get('min_roe'),
            max_roe=config.get('max_roe'),
            min_bonus_rate=config.get('min_bonus_rate'),
            max_bonus_rate=config.get('max_bonus_rate')
        )
        return stocks_data
    
    def show_config_dialog(self, widget=None):
        if self.stock_config_view:
            self.stock_config_view.show_config_dialog()
    
    def get_toolbar_commands(self):
        cmd_config = toga.Command(
            action=self.show_config_dialog,
            text="配置",
            tooltip="列表配置",
            icon="resources/config.png"
        )
        return [cmd_config]
    
    def on_config_change(self, config):
        self._config = config
        self.config_service.save_stock_list_config(config)
        stocks_data = self.get_stocks_data(config)
        if self.stock_list_view:
            self.stock_list_view.update_data(stocks_data)
    
    def on_stock_select(self, row):
        """
        处理股票选择事件
        :param row: 选中的行数据
        """
        if not row:
            return
        
        # 获取选中股票的代码
        stock_code = row[1]  # 代码在第二列
        
        # 获取股票详情、财报数据和分红数据
        stock = self.service.get_stock_by_code(stock_code)
        financial_reports = self.financial_service.get_financial_reports_by_code(stock_code)
        bonus_details = self.bonus_service.get_bonus_details_by_code(stock_code)
        
        if not stock:
            return
        
        # 准备财报数据
        financial_data = {}
        if financial_reports:
            latest_report = financial_reports[0]
            financial_data = {
                'net_asset_per_share': latest_report.net_asset_per_share,
                'basic_eps': latest_report.basic_eps,
                'revenue': None,  # 暂时返回None，后续可以从API获取
                'net_profit': None,  # 暂时返回None，后续可以从API获取
                'gross_profit_rate': None,  # 暂时返回None，后续可以从API获取
                'net_profit_rate': None,  # 暂时返回None，后续可以从API获取
                'reports': [
                    {
                        'report_period': report.report_period,
                        'roe': report.roe,
                        'net_asset_per_share': report.net_asset_per_share,
                        'basic_eps': report.basic_eps,
                        'assets_debt_ratio': report.assets_debt_ratio
                    }
                    for report in financial_reports
                ]
            }
        
        # 准备分红数据
        bonus_data = {
            'history': [
                {
                    'year': bonus.year,
                    'amount': bonus.bonus_amount,
                    'rate': bonus.pre_tax_dividend_rate
                }
                for bonus in bonus_details
            ]
        }
        
        # 创建股票详情视图
        if not self.stock_detail_view:
            self.stock_detail_view = StockDetailView()
        
        # 准备股票数据字典
        stock_data = {
            'code': stock.code,
            'name': stock.name,
            'price': stock.price,
            'pe': stock.pe,
            'pb': stock.pb,
            'bonus_rate': stock.bonus_rate,
            'assets_debt_ratio': stock.assets_debt_ratio,
            'roe': stock.roe,
            'growth': stock.growth
        }
        
        # 更新详情视图数据
        self.stock_detail_view.update_data(stock_data, financial_data, bonus_data)
        
        # 使用复用的窗口显示详情页面
        if not self.detail_window:
            self.detail_window = toga.Window(
                title=f"{stock_data['name']} 详情",
                size=(800, 600),
                resizable=True,
                content=self.stock_detail_view,
                on_resize=None,
                on_gain_focus=None,
                on_lose_focus=None,
                on_show=None,
                on_hide=None
            )
        else:
            self.detail_window.title = f"{stock_data['name']} 详情"
            self.detail_window.content = self.stock_detail_view
        
        self.detail_window.show()

