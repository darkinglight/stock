"""
stock filter application
"""
from threading import Thread

import toga
from toga import Table
from toga.style.pack import COLUMN, ROW, Pack
from stocks import hkstock, hkfinancial, stocklist
from stocks.detail import Detail


class stock(toga.App):
    def startup(self):
        table = toga.Table(
            headings=["配置项", "值"],
            data=[
                ("缓存路径", self.paths.cache),
                ("数据路径", self.paths.data),
            ],
            style=Pack(flex=1)
        )

        container = toga.OptionContainer(content=[
            ("港股通", stocklist.Stocklist(self.paths.cache, self.stock_detail)),
            ("系统配置", toga.Box(children=[table]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.menu()
        self.main_window.show()

    def stock_detail(self, widget: Table):
        self.main_window.content = Detail(widget.selection.code)

    def menu(self):
        cmd = toga.Command(
            action=refresh_hk_data_async,
            text="refresh",
            tooltip="港股数据刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd)


def refresh_hk_data_async(command, **kwargs):
    t = Thread(target=refresh_hk_data)
    t.start()
    print("refresh finish")


def refresh_hk_data():
    hkstock.init_table()
    hkstock.init_hk_stock()
    hkfinancial.create_table()
    hkfinancial.refresh_all()


def main():
    return stock()
