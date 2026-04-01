"""
My first application
"""

import toga
from toga.style.pack import COLUMN, ROW, Pack

from services.a_stock_service import AStockService
from view.stock_list import StockListView
from database.connection import DatabaseConnectionManager


class stocks(toga.App):
    def startup(self):
        db_manager = DatabaseConnectionManager()
        db_manager.set_default_db_name(r"D:\Site\stock\finance.db")

        main_box = toga.Box(style=toga.style.Pack(flex=1, direction=COLUMN))

        service = AStockService()
        stocks_data = service.get_stocks_paginated(page=1, page_size=20, sort_by='growth', sort_order='desc')
        service.close()

        self.stock_list_view = StockListView(stocks=stocks_data, on_config_change=self._on_config_change)
        main_box.add(self.stock_list_view)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self._setup_toolbar()
        self.main_window.show()

    def _setup_toolbar(self):
        cmd_config = toga.Command(
            action=self._show_config,
            text="配置",
            tooltip="列表配置",
            icon="resources/config.png"
        )
        self.main_window.toolbar.add(cmd_config)

    def _show_config(self, widget):
        self.stock_list_view.show_config_dialog()

    def _on_config_change(self, config):
        service = AStockService()
        stocks_data = service.get_stocks_paginated(
            page=1,
            page_size=config['page_size'],
            sort_by=config['sort_by'],
            sort_order=config['sort_order'],
            max_debt_ratio=config['max_debt_ratio']
        )
        service.close()
        self.stock_list_view.update_data(stocks_data)


def main():
    return stocks()
