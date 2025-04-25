"""
stock filter application
"""
import os
from threading import Thread

import toga
from toga import Table
from toga.style.pack import COLUMN, ROW, Pack

from hs import HsFacade, HsSpot
from hs.HsDetail import HsDetailRepository
from hs.HsFhps import HsFhps, HsFhpsRepository
from hs.HsFinancial import HsFinancialRepository
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
            ("A股", HsFacade.HsBox(self.db_path, None)),
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
        # todo 添加删除重建所有表的按钮
        def refresh_price_async(command, **kwargs):
            # todo 15s超时失败太频繁，延长超时时间
            def refresh_price_data():
                try:
                    stock_repository = hkstock.HkStockRepository(self.db_path)
                    stock_repository.init_table()
                    stock_repository.init_hk_stock()
                    print("refresh hk stock finish.")
                except Exception as e:
                    print(f"refresh hk stock error: {e}")
                try:
                    hs_detail_repository = HsDetailRepository(self.db_path)
                    hs_detail_repository.init_table()
                    hs_spot_repository = HsSpot.HsSpotRepository(self.db_path)
                    hs_spot_repository.init_table()
                    hs_spot_repository.refresh()
                    print("refresh hs stock finish.")
                except Exception as e:
                    print(f"refresh hs stock error: {e}")

            t = Thread(target=refresh_price_data)
            t.start()

        def refresh_financial_async(command, **kwargs):
            def refresh_financial_data():
                try:
                    finance_repository = hkfinancial.HkFinanceRepository(self.db_path)
                    finance_repository.create_table()
                    finance_repository.refresh_all()
                    print("refresh hk financial finish.")
                except Exception as e:
                    print(f"refresh hk financial error: {e}")
                try:
                    hs_financial_repository = HsFinancialRepository(self.db_path)
                    hs_financial_repository.init_table()
                    hs_financial_repository.refresh_all()
                    print("refresh hs financial finish.")
                except Exception as e:
                    print(f"refresh hs financial error: {e}")
                try:
                    hs_fhps_repository = HsFhpsRepository(self.db_path)
                    hs_fhps_repository.init_table()
                    hs_fhps_repository.refresh_all()
                    print("refresh hs fhps finish.")
                except Exception as e:
                    print(f"refresh hs fhps error: {e}")

            t = Thread(target=refresh_financial_data)
            t.start()

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
            action=refresh_price_async,
            text="日K刷新",
            tooltip="日k数据刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh)
        cmd_refresh_financial = toga.Command(
            action=refresh_financial_async,
            text="财报刷新",
            tooltip="财报刷新",
            icon="resources/icons/brutus",
        )
        self.main_window.toolbar.add(cmd_refresh_financial)


def main():
    return stock()
