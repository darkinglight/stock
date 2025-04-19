"""
stock filter application
"""
import os
from threading import Thread

import toga
from toga import Table
from toga.style.pack import COLUMN, ROW, Pack

from hs import HsFacade
from stocks import hkstock, hkfinancial, stocklist
from stocks.detail import Detail


class stock(toga.App):
    pre_page = None

    def startup(self):
        self.db_path = os.path.join(self.paths.data, "finance.db")
        # self.db_path = "/Users/janet"
        if not os.path.exists(self.paths.data):
            os.makedirs(self.paths.data, exist_ok=True)

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
            # ("A股", HsFacade.HsBox(self.db_path, None)),
            ("系统配置", toga.Box(children=[table]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.menu()
        self.main_window.show()

    def stock_detail(self, widget: Table):
        self.pre_page = self.main_window.content
        self.main_window.content = Detail(self.db_path, widget.selection.code)

    def menu(self):
        def refresh_hk_data_async(command, **kwargs):
            def refresh_hk_data():
                stock_repository = hkstock.HkStockRepository(self.db_path)
                stock_repository.init_table()
                stock_repository.init_hk_stock()
                finance_repository = hkfinancial.HkFinanceRepository(self.db_path)
                finance_repository.create_table()
                finance_repository.refresh_all()
                HsFacade.init(self.db_path)

            t = Thread(target=refresh_hk_data)
            t.start()
            print("refresh finish")

        def goto_pre_page(command):
            if self.pre_page is not None:
                self.main_window.content = self.pre_page
                self.pre_page = None

        cmd_pre_page = toga.Command(
            action=goto_pre_page,
            text="pre",
            tooltip="上一页",
            icon="resources/icons/brutus"
        )
        self.main_window.toolbar.add(cmd_pre_page)
        cmd_refresh = toga.Command(
            action=refresh_hk_data_async,
            text="refresh",
            tooltip="港股数据刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh)


def main():
    return stock()
