"""
My first application
"""

import toga
from toga.style.pack import COLUMN, ROW

from services.a_stock_service import AStockService
from view.stock_list import StockListView
from database.connection import DatabaseConnectionManager


class stocks(toga.App):
    def startup(self):
        db_manager = DatabaseConnectionManager()
        db_manager.set_default_db_name(r"D:\Site\stock2\stocks\finance.db")

        main_box = toga.Box(style=toga.style.Pack(flex=1, direction=COLUMN))

        service = AStockService()
        stocks_data = service.get_stocks_paginated(page=1, page_size=20, sort_by='growth', sort_order='desc')
        service.close()

        self.stock_list_view = StockListView(stocks=stocks_data)
        main_box.add(self.stock_list_view)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return stocks()
