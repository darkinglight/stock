"""
stock filter application
"""
import os
from threading import Thread

import toga
from toga import Table
from toga.style.pack import COLUMN, ROW, Pack
from stocks import hkstock, hkfinancial, stocklist
from stocks.detail import Detail


class stock(toga.App):
    def startup(self):
        # self.db_path = self.paths.data
        self.db_path = "/Users/janet/Site/stock"
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path, exist_ok=True)

        table = toga.Table(
            headings=["配置项", "值"],
            data=[
                ("缓存路径", self.paths.cache),
                ("数据路径", self.paths.data),
            ],
            style=Pack(flex=1)
        )

        container = toga.OptionContainer(content=[
            ("港股通", stocklist.Stocklist(self.db_path, self.stock_detail)),
            ("系统配置", toga.Box(children=[table]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.menu()
        self.main_window.show()

    def stock_detail(self, widget: Table):
        self.main_window.content = Detail(widget.selection.code)

    def menu(self):
        def refresh_hk_data_async(command, **kwargs):
            def refresh_hk_data():
                db_file = os.path.join(self.db_path, "finance.db")
                stock_repository = hkstock.HkStockRepository(db_file)
                stock_repository.init_table()
                stock_repository.init_hk_stock()
                finance_repository = hkfinancial.HkFinanceRepository(db_file)
                finance_repository.create_table()
                finance_repository.refresh_all()

            t = Thread(target=refresh_hk_data)
            t.start()
            print("refresh finish")

        cmd = toga.Command(
            action=refresh_hk_data_async,
            text="refresh",
            tooltip="港股数据刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd)


def main():
    return stock()
