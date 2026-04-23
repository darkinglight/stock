"""
My first application
"""

import toga
from toga.style.pack import COLUMN

from stocks.a_stock_controller import AStockController
from database.connection import DatabaseConnectionManager


class stocks(toga.App):
    def startup(self):
        # 设置数据库连接
        db_manager = DatabaseConnectionManager()
        db_manager.set_default_db_name(r"D:\Site\stock\finance.db")

        # 创建主窗口
        self.main_window = toga.MainWindow(title=self.formal_name)

        # 初始化控制器并传递主窗口引用
        self.controller = AStockController(main_window=self.main_window)

        # 初始化股票列表页面
        stock_list_view = self.controller.initialize_stock_list()
        self.controller.initialize_hk_stock_list()
        
        main_box = toga.Box(style=toga.style.Pack(flex=1, direction=COLUMN))
        main_box.add(stock_list_view)

        self.main_window.content = main_box
        for command in self.controller.get_toolbar_commands():
            self.main_window.toolbar.add(command)
        self.main_window.show()


def main():
    return stocks()
