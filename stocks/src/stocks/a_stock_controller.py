import toga
from services.a_stock_service import AStockService
from view.stock_list import StockListView


class AStockController:
    def __init__(self):
        self.stock_list_view = None
        self.service = AStockService()
    
    def initialize_stock_list(self):
        stocks_data = self.service.get_stocks_paginated(page=1, page_size=20, sort_by='growth', sort_order='desc')
        
        self.stock_list_view = StockListView(stocks=stocks_data, on_config_change=self.on_config_change)
        return self.stock_list_view
    
    def get_stocks_data(self, config):
        stocks_data = self.service.get_stocks_paginated(
            page=1,
            page_size=config['page_size'],
            sort_by=config['sort_by'],
            sort_order=config['sort_order'],
            max_debt_ratio=config['max_debt_ratio']
        )
        return stocks_data
    
    def show_config_dialog(self, widget=None):
        if self.stock_list_view:
            self.stock_list_view.show_config_dialog()
    
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
