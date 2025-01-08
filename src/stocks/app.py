"""
stock filter application
"""
import time

import toga
from toga.style.pack import COLUMN, ROW, Pack
from stocks import hkstock, hkfinancial, stocklist


class stock(toga.App):
    def startup(self):
        label = toga.TextInput("abcdefg", style=Pack(flex=1))
        container = toga.OptionContainer(content=[
            ("港股", stocklist.Stocklist(self.paths.cache, self.stock_detail)),
            ("A股", toga.Box(children=[label]))
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


async def refresh_hk_data(command, **kwargs):
    # hkstock.init_hk_stock()
    # hkfinancial.refresh_all()

    print("refresh")


def main():
    return stock()
