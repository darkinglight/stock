"""
stock filter application
"""
import asyncio
import time
from threading import Thread

import toga
from toga.style.pack import COLUMN, ROW, Pack
from stocks import hkstock, hkfinancial, stocklist


class stock(toga.App):
    def startup(self):
        table = toga.Table(
            headings=["Name", "Age"],
            data=[
                ("Arthur Dent", 42),
                ("Ford Prefect", 37),
                ("Tricia McMillan", 38),
            ]
        )

        container = toga.OptionContainer(content=[
            ("港股", stocklist.Stocklist(self.paths.cache, self.stock_detail)),
            ("A股", toga.Box(children=[table]))
        ])
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = container
        self.menu()
        self.main_window.show()

    def stock_detail(self, widget):
        self.main_window.content = toga.Label(text="hahaha")

    def menu(self):
        cmd = toga.Command(
            action=refresh_hk_data,
            text="refresh",
            tooltip="港股数据刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd)


def refresh_hk_data(command, **kwargs):
    t = Thread(target=echo)
    t.start()
    # hkstock.init_hk_stock()
    # hkfinancial.refresh_all()
    print("refresh")


def echo():
    print("echo start:" + time.asctime())
    time.sleep(3)
    hkfinancial.refresh_all()
    print("echo end" + time.asctime())


def main():
    return stock()
