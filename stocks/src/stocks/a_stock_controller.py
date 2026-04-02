import toga
from services.a_stock_service import AStockService
from view.a_stock_list import StockListView
from view.a_stock_config import StockConfigView


class AStockController:
    def __init__(self):
        self.stock_list_view = None
        self.stock_config_view = None
        self.service = AStockService()
    
    def initialize_stock_list(self):
        stocks_data = self.service.get_stocks_paginated(page=1, page_size=20, sort_by='growth', sort_order='desc')
        
        self.stock_list_view = StockListView(stocks=stocks_data)
        self.stock_config_view = StockConfigView(on_config_change=self.on_config_change)
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
        stocks_data = self.get_stocks_data(config)
        if self.stock_list_view:
            self.stock_list_view.update_data(stocks_data)
