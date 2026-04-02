"""
My first application
"""

import toga
from toga.style.pack import COLUMN, ROW, Pack

from stocks.a_stock_controller import AStockController


class stocks(toga.App):
    def startup(self):
        self.controller = AStockController()

        main_box = toga.Box(style=toga.style.Pack(flex=1, direction=COLUMN))

        self.stock_list_view = self.controller.initialize_stock_list()
        main_box.add(self.stock_list_view)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.controller.setup_toolbar(self.main_window)
        self.main_window.show()


def main():
    return stocks()
